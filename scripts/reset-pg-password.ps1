# Resets the password of the PostgreSQL "postgres" user when it is forgotten,
# then saves the matching DATABASE_URL in backend/.env.
#
# It briefly lets local connections in without a password (pg_hba.conf "trust"),
# sets the new password, and always puts pg_hba.conf back afterwards.
# The new password is hidden while typing and is never printed or logged.
#
# Run it in a PowerShell window opened as Administrator:
#   powershell -ExecutionPolicy Bypass -File C:\dev\DotAndKey\scripts\reset-pg-password.ps1

$ErrorActionPreference = 'Stop'

$ServiceName = 'postgresql-x64-18'
$PgRoot = 'C:\Program Files\PostgreSQL\18'
$HbaPath = "$PgRoot\data\pg_hba.conf"
$BackupPath = "$HbaPath.backup"
$PsqlPath = "$PgRoot\bin\psql.exe"
$PgIsReadyPath = "$PgRoot\bin\pg_isready.exe"
$Port = 5432
$EnvPath = Join-Path (Split-Path $PSScriptRoot -Parent) 'backend\.env'

function Test-IsAdministrator {
    $identity = [Security.Principal.WindowsIdentity]::GetCurrent()
    $principal = New-Object Security.Principal.WindowsPrincipal($identity)
    return $principal.IsInRole([Security.Principal.WindowsBuiltInRole]::Administrator)
}

function ConvertFrom-SecureText([Security.SecureString]$Secure) {
    $bstr = [Runtime.InteropServices.Marshal]::SecureStringToBSTR($Secure)
    try {
        return [Runtime.InteropServices.Marshal]::PtrToStringBSTR($bstr)
    } finally {
        [Runtime.InteropServices.Marshal]::ZeroFreeBSTR($bstr)
    }
}

# Changes only the active 127.0.0.1 and ::1 scram-sha-256 lines.
function ConvertTo-TrustHba([string]$Text) {
    $pattern = '(?m)^(host[ \t]+\S+[ \t]+\S+[ \t]+(?:127\.0\.0\.1/32|::1/128)[ \t]+)scram-sha-256(?=\s|\z)'
    return [regex]::Replace($Text, $pattern, '${1}trust')
}

function New-PasswordSql([string]$Password) {
    $quoted = $Password.Replace("'", "''")
    # The SET lines keep the statement out of the server log, even on an error.
    return "SET log_statement = 'none';`n" +
        "SET log_min_error_statement = 'panic';`n" +
        "SET log_min_duration_statement = -1;`n" +
        "SET password_encryption = 'scram-sha-256';`n" +
        "SET standard_conforming_strings = on;`n" +
        "ALTER USER postgres PASSWORD '$quoted';`n"
}

# Sends the SQL through stdin. psql's output is discarded because an error
# message could quote the statement. Returns psql's exit code.
function Invoke-PsqlStdin([string]$Psql, [int]$PgPort, [string]$Sql) {
    $info = New-Object Diagnostics.ProcessStartInfo
    $info.FileName = $Psql
    $info.Arguments = "-X -q -w -v ON_ERROR_STOP=1 -h 127.0.0.1 -p $PgPort -U postgres -d postgres"
    $info.UseShellExecute = $false
    $info.CreateNoWindow = $true
    $info.RedirectStandardInput = $true
    $info.RedirectStandardOutput = $true
    $info.RedirectStandardError = $true
    $info.EnvironmentVariables['PGCLIENTENCODING'] = 'UTF8'

    $process = [Diagnostics.Process]::Start($info)
    try {
        $bytes = (New-Object Text.UTF8Encoding($false)).GetBytes($Sql)
        $process.StandardInput.BaseStream.Write($bytes, 0, $bytes.Length)
        $process.StandardInput.Close()
        $null = $process.StandardOutput.ReadToEnd()
        $null = $process.StandardError.ReadToEnd()
        $process.WaitForExit()
        return $process.ExitCode
    } finally {
        $process.Dispose()
    }
}

function Wait-PostgresReady([string]$PgIsReady, [int]$PgPort) {
    for ($i = 0; $i -lt 30; $i++) {
        & $PgIsReady -q -h 127.0.0.1 -p $PgPort
        if ($LASTEXITCODE -eq 0) { return $true }
        Start-Sleep -Seconds 1
    }
    return $false
}

function Restart-Postgres {
    Restart-Service -Name $ServiceName -Force -WarningAction SilentlyContinue
    if (-not (Wait-PostgresReady $PgIsReadyPath $Port)) {
        throw 'PostgreSQL did not become ready after the restart.'
    }
}

# Adds or updates only the DATABASE_URL line, the same way set-db-url.ps1 does.
function Set-DatabaseUrl([string]$Path, [string]$Password, [int]$PgPort) {
    $encoded = [Uri]::EscapeDataString($Password)
    $line = "DATABASE_URL=postgresql://postgres:${encoded}@localhost:$PgPort/dotandkey"

    $text = ''
    if (Test-Path -LiteralPath $Path) {
        $text = [IO.File]::ReadAllText($Path)
    }

    $pattern = '(?m)^[ \t]*DATABASE_URL[ \t]*=[^\r\n]*'
    if ([regex]::IsMatch($text, $pattern)) {
        $text = [regex]::Replace($text, $pattern, $line.Replace('$', '$$'))
    } else {
        $newline = [Environment]::NewLine
        if ($text.Contains("`n") -and -not $text.Contains("`r`n")) {
            $newline = "`n"
        }
        if ($text.Length -gt 0 -and -not $text.EndsWith("`n")) {
            $text += $newline
        }
        $text += $line + $newline
    }

    # UTF-8 without a byte-order mark, which would corrupt the first line.
    [IO.File]::WriteAllText($Path, $text, (New-Object Text.UTF8Encoding($false)))
}

# --- Main ---

if (-not (Test-IsAdministrator)) {
    Write-Host 'Please open PowerShell as Administrator and run this script again. Nothing was changed.'
    exit 1
}

foreach ($required in @($HbaPath, $PsqlPath, $PgIsReadyPath)) {
    if (-not (Test-Path -LiteralPath $required)) {
        Write-Host "Not found: $required. Nothing was changed."
        exit 1
    }
}
$null = Get-Service -Name $ServiceName

$first = ConvertFrom-SecureText (Read-Host -Prompt 'New password for user postgres' -AsSecureString)
$second = ConvertFrom-SecureText (Read-Host -Prompt 'Type the new password again' -AsSecureString)

if ([string]::IsNullOrEmpty($first)) {
    Write-Host 'The password is empty. Nothing was changed.'
    exit 1
}
# -cne is case-sensitive; plain -ne would treat "Abc" and "abc" as equal.
if ($first -cne $second) {
    Write-Host 'The two passwords do not match. Nothing was changed.'
    exit 1
}

if (Test-Path -LiteralPath $BackupPath) {
    Write-Host 'Keeping the existing pg_hba.conf.backup.'
} else {
    Copy-Item -LiteralPath $HbaPath -Destination $BackupPath
    Write-Host 'Backed up pg_hba.conf.'
}

# Latin-1 maps each byte to one character, so other bytes stay exactly as they were.
$latin1 = [Text.Encoding]::GetEncoding(28591)
$original = $latin1.GetString([IO.File]::ReadAllBytes($BackupPath))
$trust = ConvertTo-TrustHba $original
if ($trust -ceq $original) {
    Write-Host 'No scram-sha-256 lines for 127.0.0.1 or ::1 in pg_hba.conf. Nothing was changed.'
    exit 1
}

$passwordChanged = $false
$restored = $false
$running = $false

try {
    [IO.File]::WriteAllBytes($HbaPath, $latin1.GetBytes($trust))
    Write-Host 'Allowing local access for a moment and restarting PostgreSQL...'
    Restart-Postgres

    Write-Host 'Setting the new password...'
    $exitCode = Invoke-PsqlStdin $PsqlPath $Port (New-PasswordSql $first)
    if ($exitCode -ne 0) {
        throw "psql could not set the password (exit code $exitCode)."
    }
    $passwordChanged = $true
    Write-Host 'Password changed.'
} catch {
    Write-Host "Failed: $($_.Exception.Message)"
} finally {
    Write-Host 'Restoring pg_hba.conf and restarting PostgreSQL...'
    try {
        Copy-Item -LiteralPath $BackupPath -Destination $HbaPath -Force
        $restored = $true
    } catch {
        Write-Host "Could not restore pg_hba.conf: $($_.Exception.Message)"
    }
    try {
        Restart-Postgres
        $running = $true
    } catch {
        Write-Host "Could not restart PostgreSQL: $($_.Exception.Message)"
    }
}

if (-not $restored) {
    Write-Host "WARNING: local logins may still need no password. Copy $BackupPath over $HbaPath and restart $ServiceName."
}
if (-not $running) {
    Write-Host "WARNING: PostgreSQL may not be running. Check the $ServiceName service."
}

if (-not $passwordChanged) {
    Write-Host 'The password was not changed. backend/.env was not changed.'
    exit 1
}

Set-DatabaseUrl $EnvPath $first $Port
Write-Host 'DATABASE_URL saved to backend/.env'

if (-not ($restored -and $running)) {
    exit 1
}
Write-Host 'Done.'
