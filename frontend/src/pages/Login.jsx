import { useState } from 'react'
import { Navigate } from 'react-router-dom'
import { useAuth } from '../context/AuthContext'

function Login() {
  const { isLoggedIn, login, register } = useAuth()

  const [mode, setMode] = useState('signin')
  const [username, setUsername] = useState('')
  const [password, setPassword] = useState('')
  const [confirm, setConfirm] = useState('')
  const [error, setError] = useState('')
  const [submitting, setSubmitting] = useState(false)

  const isSignup = mode === 'signup'

  if (isLoggedIn) {
    return <Navigate to="/" replace />
  }

  function switchMode(event) {
    event.preventDefault()
    setMode(isSignup ? 'signin' : 'signup')
    setError('')
  }

  async function handleSubmit(event) {
    event.preventDefault()
    setError('')

    if (isSignup && password !== confirm) {
      setError('Passwords do not match')
      return
    }

    setSubmitting(true)
    try {
      if (isSignup) {
        await register(username.trim(), password)
      } else {
        await login(username.trim(), password)
      }
    } catch (err) {
      setError(err.message)
      setSubmitting(false)
    }
  }

  let buttonLabel = 'Sign In'
  if (submitting) buttonLabel = 'Please wait...'
  else if (isSignup) buttonLabel = 'Create Account'

  return (
    <section className="auth-screen">
      <div className="auth-card">
        <h2>{isSignup ? 'Create Account' : 'Sign In'}</h2>
        <p className="auth-sub">
          {isSignup ? 'Join Dot & Key' : 'Welcome back to Dot & Key'}
        </p>

        <form className="auth-form" onSubmit={handleSubmit}>
          <label className="auth-field">
            <span>Username</span>
            <input
              type="text"
              value={username}
              onChange={(e) => setUsername(e.target.value)}
              autoComplete="username"
              autoCapitalize="none"
              required
            />
          </label>

          <label className="auth-field">
            <span>Password</span>
            <input
              type="password"
              value={password}
              onChange={(e) => setPassword(e.target.value)}
              autoComplete={isSignup ? 'new-password' : 'current-password'}
              required
            />
          </label>

          {isSignup && (
            <label className="auth-field">
              <span>Re-enter Password</span>
              <input
                type="password"
                value={confirm}
                onChange={(e) => setConfirm(e.target.value)}
                autoComplete="new-password"
                required
              />
            </label>
          )}

          {error && <p className="auth-error">{error}</p>}

          <button type="submit" className="auth-btn" disabled={submitting}>
            {buttonLabel}
          </button>
        </form>

        <p className="auth-toggle">
          <span>{isSignup ? 'Already have an account?' : 'New to Dot & Key?'}</span>{' '}
          <a href="#" onClick={switchMode}>
            {isSignup ? 'Sign in' : 'Create an account'}
          </a>
        </p>
      </div>
    </section>
  )
}

export default Login