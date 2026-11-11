// In development Vite forwards /api to the Flask server (see vite.config.js).
// Set VITE_API_URL only when the API lives somewhere else.
const API_URL = import.meta.env.VITE_API_URL || '/api'

// The login token lives in an httpOnly cookie set by the server, so page
// JavaScript never sees it. These keys held it in older versions; remove them.
try {
  localStorage.removeItem('dk_token')
  localStorage.removeItem('dk_user')
} catch {
  // storage unavailable; nothing to clean up
}

export async function request(path, options = {}) {
  const headers = {
    // The API requires this on cookie-authenticated writes (CSRF protection).
    'X-Requested-With': 'XMLHttpRequest',
    ...(options.headers || {}),
  }

  const response = await fetch(`${API_URL}${path}`, {
    ...options,
    headers,
    credentials: 'include', // send the session cookie
  })
  const data = await response.json().catch(() => ({}))

  if (response.status === 401) {
    window.dispatchEvent(new Event('auth:expired'))
  }

  if (!response.ok) {
    const error = new Error(data.error || `Request failed (HTTP ${response.status})`)
    error.status = response.status
    throw error
  }

  return data
}
