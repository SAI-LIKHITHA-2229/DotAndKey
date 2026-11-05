import { Navigate } from 'react-router-dom'
import { useAuth } from '../context/AuthContext'

function RequireAuth({ children }) {
  const { isLoggedIn, checking } = useAuth()

  // Wait for the server to say whether the session cookie is still valid.
  if (checking) return null

  return isLoggedIn ? children : <Navigate to="/login" replace />
}

export default RequireAuth
