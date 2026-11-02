import { useState } from 'react'
import { addToCart } from '../api/cart'

const BUTTON_LABELS = {
  idle: 'Add to Cart',
  adding: 'Adding...',
  added: 'Added ✓',
  error: 'Try again',
}

function ProductCard({ product }) {
  const [status, setStatus] = useState('idle')

  async function handleAddToCart() {
    setStatus('adding')
    try {
      await addToCart(product, null, product.image)
      setStatus('added')
    } catch (error) {
      console.error(error)
      setStatus('error')
    }
    setTimeout(() => setStatus('idle'), 1400)
  }

  return (
    <div className="product-card">
      <img
        src={`/images/${product.image}`}
        alt={product.name}
        className="product-image"
      />
      <h3>{product.name}</h3>
      <p className="price">₹{product.price}</p>
      <button
        className="add-to-cart-btn"
        onClick={handleAddToCart}
        disabled={status === 'adding'}
      >
        {BUTTON_LABELS[status]}
      </button>
    </div>
  )
}

export default ProductCard