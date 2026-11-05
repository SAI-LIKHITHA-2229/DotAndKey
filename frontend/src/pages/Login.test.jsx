import { render, screen } from '@testing-library/react'
import userEvent from '@testing-library/user-event'
import { MemoryRouter } from 'react-router-dom'
import { beforeEach, describe, expect, it, vi } from 'vitest'
import { getMe, loginUser, registerUser } from '../api/auth'
import { AuthProvider } from '../context/AuthContext'
import Login from './Login'

vi.mock('../api/auth', () => ({
  getMe: vi.fn(),
  loginUser: vi.fn(),
  logoutUser: vi.fn(),
  registerUser: vi.fn(),
}))

function renderLogin() {
  render(
    <AuthProvider>
      <MemoryRouter>
        <Login />
      </MemoryRouter>
    </AuthProvider>
  )
  return userEvent.setup()
}

describe('Login', () => {
  beforeEach(() => {
    vi.mocked(getMe).mockRejectedValue(new Error('Login required'))
    vi.mocked(loginUser).mockReset()
    vi.mocked(registerUser).mockReset()
  })

  it('shows the server message when sign-in fails', async () => {
    vi.mocked(loginUser).mockRejectedValueOnce(new Error('Invalid username or password'))
    const user = renderLogin()

    await user.type(await screen.findByLabelText('Username'), 'alice')
    await user.type(screen.getByLabelText('Password'), 'wrong-password')
    await user.click(screen.getByRole('button', { name: 'Sign In' }))

    expect(await screen.findByText('Invalid username or password')).toBeInTheDocument()
    expect(loginUser).toHaveBeenCalledWith('alice', 'wrong-password')
  })

  it('checks that both sign-up passwords match before calling the server', async () => {
    const user = renderLogin()

    await user.click(await screen.findByRole('button', { name: 'Create an account' }))
    await user.type(screen.getByLabelText('Username'), 'alice')
    await user.type(screen.getByLabelText('Password'), 'password123')
    await user.type(screen.getByLabelText('Re-enter Password'), 'password124')
    await user.click(screen.getByRole('button', { name: 'Create Account' }))

    expect(screen.getByText('Passwords do not match')).toBeInTheDocument()
    expect(registerUser).not.toHaveBeenCalled()
  })
})
