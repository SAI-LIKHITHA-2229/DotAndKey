import { createContext, useContext, useEffect, useState } from 'react'
import { loginUser, registerUser } from '../api/auth'
import {
  clearSession,
  getStoredUsername,
  getToken,
  saveSession,
} from '../api/client'

const AuthContext = createContext(null)

export function AuthProvider({ children }) {
  const [username, setUsername] = useState(() =>
    getToken() ? getStoredUsername() : null
  )

    useEffect(() => {
    function handleExpired() {
      setUsername(null)
    }
    window.addEventListener('auth:expired', handleExpired)
    return () => window.removeEventListener('auth:expired', handleExpired)
  }, [])

  async function login(name, password) {
    const data = await loginUser(name, password)
    saveSession(data.token, data.username)
    setUsername(data.username)
  }

  async function register(name, password) {
    await registerUser(name, password)
    await login(name, password)
  }

  function logout() {
    clearSession()
    setUsername(null)
  }

  const value = {
    username,
    isLoggedIn: Boolean(username),
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