import { request } from './client'

export function registerUser(username, password) {
  return request('/register', {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ username, password }),
  })
}

// Sets the httpOnly session cookie; returns { username, expires_at }.
export function loginUser(username, password) {
  return request('/login', {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ username, password }),
  })
}

// Who is logged in according to the session cookie (401 if nobody).
export function getMe() {
  return request('/me')
}

// Ends the session on the server and clears the cookie.
export function logoutUser() {
  return request('/logout', { method: 'POST' })
}
