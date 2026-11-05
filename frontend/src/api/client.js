const API_URL = import.meta.env.VITE_API_URL || 'http://127.0.0.1:5001'
const TOKEN_KEY = 'dk_token'
const USER_KEY = 'dk_user'

export function getToken() {
  try {
    return localStorage.getItem(TOKEN_KEY)
  } catch {
    return null
  }
}

export function getStoredUsername() {
  try {
    return localStorage.getItem(USER_KEY)
  } catch {
    return null
  }
}

export function saveSession(token, username) {
  try {
    localStorage.setItem(TOKEN_KEY, token)
    localStorage.setItem(USER_KEY, username)
  } catch {
    // storage unavailable (private mode); user will need to log in again
  }
}

export function clearSession() {
  try {
    localStorage.removeItem(TOKEN_KEY)
    localStorage.removeItem(USER_KEY)
  } catch {
    // nothing to clear
  }
}

export async function request(path, options = {}) {
  const headers = { ...(options.headers || {}) }
  const token = getToken()
  if (token) {
    headers.Authorization = `Bearer ${token}`
  }

  const response = await fetch(`${API_URL}${path}`, { ...options, headers })
  const data = await response.json().catch(() => ({}))

  if (response.status === 401 && token) {
    clearSession()
    window.dispatchEvent(new Event('auth:expired'))
  }

  if (!response.ok) {
    const error = new Error(data.error || `Request failed (HTTP ${response.status})`)
    error.status = response.status
    throw error
  }

  return data
}