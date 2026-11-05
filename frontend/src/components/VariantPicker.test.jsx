import { render, screen } from '@testing-library/react'
import userEvent from '@testing-library/user-event'
import { describe, expect, it, vi } from 'vitest'
import VariantPicker from './VariantPicker'

const pills = [{ label: 'Gel' }, { label: 'Cream' }, { label: 'Lotion' }]
const swatches = [
  { label: 'Peony', color: '#f2d8cf' },
  { label: 'Rose', color: '#eccbb4' },
]

function setup(variants, props = {}) {
  const onSelect = vi.fn()
  const onPreview = vi.fn()
  render(
    <VariantPicker
      variants={variants}
      selectedIndex={0}
      onSelect={onSelect}
      onPreview={onPreview}
      {...props}
    />
  )
  return { onSelect, onPreview, user: userEvent.setup() }
}

describe('VariantPicker', () => {
  it('renders nothing for a product without variants', () => {
    const { container } = render(<VariantPicker variants={[]} selectedIndex={0} />)
    expect(container).toBeEmptyDOMElement()
  })

  it('selects a variant on click', async () => {
    const { onSelect, user } = setup(pills)
    await user.click(screen.getByRole('button', { name: 'Lotion' }))
    expect(onSelect).toHaveBeenCalledWith(2)
  })

  it('previews on hover and stops when the pointer leaves', async () => {
    const { onPreview, user } = setup(pills)
    await user.hover(screen.getByRole('button', { name: 'Cream' }))
    expect(onPreview).toHaveBeenLastCalledWith(1)

    await user.unhover(screen.getByRole('button', { name: 'Cream' }))
    expect(onPreview).toHaveBeenLastCalledWith(null)
  })

  it('shows colour swatches with the previewed shade name', () => {
    setup(swatches, { previewIndex: 1 })
    expect(screen.getByRole('button', { name: 'Peony' })).toHaveClass('selected')
    expect(screen.getByText('Rose', { selector: '.swatch-name' })).toBeInTheDocument()
  })
})
