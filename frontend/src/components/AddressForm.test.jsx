import { render, screen } from '@testing-library/react'
import userEvent from '@testing-library/user-event'
import { describe, expect, it, vi } from 'vitest'
import AddressForm from './AddressForm'

async function fillValidAddress(user) {
  await user.type(screen.getByLabelText('Full name'), 'Alice Example')
  await user.type(screen.getByLabelText('Mobile number'), '9876543210')
  await user.type(screen.getByLabelText('PIN code'), '500001')
  await user.type(screen.getByLabelText('Flat / House no.'), '12A')
  await user.type(screen.getByLabelText('Area / Street'), 'MG Road')
  await user.type(screen.getByLabelText('City'), 'Hyderabad')
  await user.selectOptions(screen.getByLabelText('State'), 'Telangana')
}

describe('AddressForm', () => {
  it('explains what is missing instead of saving', async () => {
    const onSave = vi.fn()
    const user = userEvent.setup()
    render(<AddressForm onSave={onSave} />)

    await user.click(screen.getByRole('button', { name: 'Save address' }))
    expect(screen.getByText('Enter your full name')).toBeInTheDocument()
    expect(onSave).not.toHaveBeenCalled()
  })

  it('only accepts digits in the mobile and PIN fields', async () => {
    const user = userEvent.setup()
    render(<AddressForm onSave={vi.fn()} />)

    await user.type(screen.getByLabelText('Mobile number'), '98-76 abc')
    expect(screen.getByLabelText('Mobile number')).toHaveValue('9876')
  })

  it('saves a valid address', async () => {
    const onSave = vi.fn(() => Promise.resolve())
    const user = userEvent.setup()
    render(<AddressForm onSave={onSave} />)

    await fillValidAddress(user)
    await user.click(screen.getByRole('button', { name: 'Save address' }))

    expect(onSave).toHaveBeenCalledWith(expect.objectContaining({
      full_name: 'Alice Example', mobile: '9876543210', pincode: '500001',
      city: 'Hyderabad', state: 'Telangana', type: 'Home',
    }))
  })

  it('shows the server error if saving fails', async () => {
    const onSave = vi.fn(() => Promise.reject(new Error('You can save up to 10 addresses')))
    const user = userEvent.setup()
    render(<AddressForm onSave={onSave} />)

    await fillValidAddress(user)
    await user.click(screen.getByRole('button', { name: 'Save address' }))
    expect(await screen.findByText('You can save up to 10 addresses')).toBeInTheDocument()
  })

  it('offers Cancel only when there is something to cancel', () => {
    const { rerender } = render(<AddressForm onSave={vi.fn()} />)
    expect(screen.queryByRole('button', { name: 'Cancel' })).not.toBeInTheDocument()

    rerender(<AddressForm onSave={vi.fn()} onCancel={vi.fn()} />)
    expect(screen.getByRole('button', { name: 'Cancel' })).toBeInTheDocument()
  })
})
