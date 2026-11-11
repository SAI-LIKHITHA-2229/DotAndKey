import { render, screen } from '@testing-library/react'
import userEvent from '@testing-library/user-event'
import { MemoryRouter, Route, Routes } from 'react-router-dom'
import { beforeEach, describe, expect, it, vi } from 'vitest'
import { addToCart } from '../api/cart'
import ProductCard from './ProductCard'

// Which cart names count as "already in the cart" for each test.
const cart = vi.hoisted(() => ({ names: new Set() }))

vi.mock('../api/cart', async (importOriginal) => ({
  ...(await importOriginal()),
  addToCart: vi.fn(() => Promise.resolve({ message: 'Item added to cart' })),
}))

vi.mock('../context/CartContext', () => ({
  useCart: () => ({
    isInCart: (name) => cart.names.has(name),
    markAdded: (name) => cart.names.add(name),
  }),
}))

const product = {
  id: 1,
  name: 'Moisturizer',
  price: 499,
  image: 'moisturizer.jpg',
  variants: [
    { label: 'Gel', image: 'gel.jpg' },
    { label: 'Cream', image: 'cream.jpg' },
  ],
}

function renderCard() {
  const view = render(
    <MemoryRouter>
      <Routes>
        <Route path="/" element={<ProductCard product={product} />} />
        <Route path="/cart" element={<p>Cart page</p>} />
      </Routes>
    </MemoryRouter>
  )
  return { ...view, user: userEvent.setup() }
}

const picture = (container) => container.querySelector('.product-image').getAttribute('src')

describe('ProductCard', () => {
  beforeEach(() => {
    cart.names = new Set()
    vi.mocked(addToCart).mockClear()
  })

  it('adds the selected variant to the cart', async () => {
    const { user } = renderCard()
    await user.click(screen.getByRole('button', { name: 'Add to Cart' }))

    expect(addToCart).toHaveBeenCalledWith(product, 'Gel')
    expect(await screen.findByRole('button', { name: 'Added ✓' })).toBeInTheDocument()
  })

  it('sends shoppers to the cart instead of adding an item twice', async () => {
    cart.names.add('Moisturizer (Gel)')
    const { user } = renderCard()

    await user.click(screen.getByRole('button', { name: 'Added ✓ · Go to cart' }))
    expect(screen.getByText('Cart page')).toBeInTheDocument()
    expect(addToCart).not.toHaveBeenCalled()
  })

  it('previews the hovered variant picture and cart state', async () => {
    cart.names.add('Moisturizer (Cream)')
    const { container, user } = renderCard()
    expect(picture(container)).toBe('/images/gel.jpg')

    await user.hover(screen.getByRole('button', { name: 'Cream' }))
    expect(picture(container)).toBe('/images/cream.jpg')
    expect(screen.getByRole('button', { name: 'Added ✓ · Go to cart' })).toBeInTheDocument()

    await user.unhover(screen.getByRole('button', { name: 'Cream' }))
    expect(picture(container)).toBe('/images/gel.jpg')
    expect(screen.getByRole('button', { name: 'Add to Cart' })).toBeInTheDocument()
  })

  it('opens the details dialog from the picture', async () => {
    const { user } = renderCard()
    await user.click(screen.getByRole('button', { name: 'View details for Moisturizer' }))

    const dialog = screen.getByRole('dialog', { name: 'Moisturizer' })
    expect(dialog).toBeInTheDocument()
    expect(screen.getByRole('button', { name: 'Close' })).toHaveFocus()
  })
})
