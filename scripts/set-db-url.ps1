# Asks for the PostgreSQL "postgres" password and saves DATABASE_URL in
# backend/.env, leaving every other line in that file unchanged.
# The password is hidden while typing and is never printed.
#
# Run it from the project root (the policy flag applies to this one run only):
#   powershell -ExecutionPolicy Bypass -File scripts\set-db-url.ps1

$ErrorActionPreference = 'Stop'

$envPath = Join-Path (Split-Path $PSScriptRoot -Parent) 'backend\.env'

$securePassword = Read-Host -Prompt 'PostgreSQL password for user postgres' -AsSecureString

# Turn the hidden value into plain text in memory, only to encode it below.
$bstr = [Runtime.InteropServices.Marshal]::SecureStringToBSTR($securePassword)
try {
    $password = [Runtime.InteropServices.Marshal]::PtrToStringBSTR($bstr)
} finally {
    [Runtime.InteropServices.Marshal]::ZeroFreeBSTR($bstr)
}

if ([string]::IsNullOrEmpty($password)) {
    Write-Host 'No password entered. backend/.env was not changed.'
    exit 1
}

# URL-encode so characters like @ # / : % can't break the connection URL.
$encoded = [Uri]::EscapeDataString($password)
$line = "DATABASE_URL=postgresql://postgres:${encoded}@localhost:5432/dotandkey"

$text = ''
if (Test-Path -LiteralPath $envPath) {
    $text = [IO.File]::ReadAllText($envPath)
}

$pattern = '(?m)^[ \t]*DATABASE_URL[ \t]*=[^\r\n]*'
if ([regex]::IsMatch($text, $pattern)) {
    # In a regex replacement "$" is special, so it has to be doubled.
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

# UTF-8 without a byte-order mark, which would corrupt the file's first line.
[IO.File]::WriteAllText($envPath, $text, (New-Object Text.UTF8Encoding($false)))

Write-Host 'DATABASE_URL saved to backend/.env'
