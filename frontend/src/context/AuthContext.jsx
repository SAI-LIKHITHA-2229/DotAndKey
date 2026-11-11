import { createContext, useContext, useEffect, useState } from 'react'
import { getMe, loginUser, logoutUser, registerUser } from '../api/auth'

const AuthContext = createContext(null)

export function AuthProvider({ children }) {
  // undefined = still asking the server, null = logged out,
  // otherwise { username, expiresAt }.
  const [session, setSession] = useState(undefined)

  // The session cookie can't be read by JavaScript, so ask the server.
  useEffect(() => {
    let ignore = false
    getMe()
      .then((data) => {
        if (!ignore) setSession({ username: data.username, expiresAt: data.expires_at })
      })
      .catch(() => {
        if (!ignore) setSession(null)
      })
    return () => {
      ignore = true
    }
  }, [])

  // Any 401 from the API means the session is over.
  useEffect(() => {
    function handleExpired() {
      setSession(null)
    }
    window.addEventListener('auth:expired', handleExpired)
    return () => window.removeEventListener('auth:expired', handleExpired)
  }, [])

  // Log out exactly when the session expires, even if the user is idle.
  useEffect(() => {
    if (!session) return
    const msLeft = new Date(session.expiresAt).getTime() - Date.now()
    const timer = setTimeout(() => setSession(null), Math.max(0, msLeft))
    return () => clearTimeout(timer)
  }, [session])

  async function login(name, password) {
    const data = await loginUser(name, password)
    setSession({ username: data.username, expiresAt: data.expires_at })
  }

  async function register(name, password) {
    await registerUser(name, password)
    await login(name, password)
  }

  async function logout() {
    try {
      await logoutUser()
    } catch (err) {
      console.error(err) // the cookie expires on its own anyway
    }
    setSession(null)
  }

  const value = {
    username: session?.username ?? null,
    isLoggedIn: Boolean(session),
    checking: session === undefined,
    login,
    register,
    logout,
  }

  return <AuthContext.Provider value={value}>{children}</AuthContext.Provider>
}

// eslint-disable-next-line react-refresh/only-export-components
export function useAuth() {
  return useContext(AuthContext)
}
