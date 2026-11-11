import { render, screen } from '@testing-library/react'
import { MemoryRouter, Route, Routes } from 'react-router-dom'
import { describe, expect, it, vi } from 'vitest'
import { getMe } from '../api/auth'
import { AuthProvider } from '../context/AuthContext'
import RequireAuth from './RequireAuth'

vi.mock('../api/auth', () => ({
  getMe: vi.fn(),
  loginUser: vi.fn(),
  logoutUser: vi.fn(),
  registerUser: vi.fn(),
}))

function renderAt(path) {
  render(
    <AuthProvider>
      <MemoryRouter initialEntries={[path]}>
        <Routes>
          <Route path="/login" element={<p>Login page</p>} />
          <Route path="/account" element={<RequireAuth><p>My account</p></RequireAuth>} />
        </Routes>
      </MemoryRouter>
    </AuthProvider>
  )
}

describe('RequireAuth', () => {
  it('shows the page when the session cookie is valid', async () => {
    const inAnHour = new Date(Date.now() + 3600_000).toISOString()
    vi.mocked(getMe).mockResolvedValueOnce({ username: 'alice', expires_at: inAnHour })
    renderAt('/account')
    expect(await screen.findByText('My account')).toBeInTheDocument()
  })

  it('redirects to login when there is no session', async () => {
    vi.mocked(getMe).mockRejectedValueOnce(Object.assign(new Error('Login required'), { status: 401 }))
    renderAt('/account')
    expect(await screen.findByText('Login page')).toBeInTheDocument()
    expect(screen.queryByText('My account')).not.toBeInTheDocument()
  })
})
