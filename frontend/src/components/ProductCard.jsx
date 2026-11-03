import { useState } from 'react'
import { addToCart } from '../api/cart'

const BUTTON_LABELS = {
  idle: 'Add to Cart',
  adding: 'Adding...',
  added: 'Added ✓',
  error: 'Try again',
}

function ProductCard({ product }) {
  const variants = product.variants || []
  const hasVariants = variants.length > 0
  const useSwatches = hasVariants && Boolean(variants[0].color)

  const [selectedIndex, setSelectedIndex] = useState(0)
  const [status, setStatus] = useState('idle')

  const selected = hasVariants ? variants[selectedIndex] : null
  const image = selected?.image || product.image

  async function handleAddToCart() {
    setStatus('adding')
    try {
      await addToCart(product, selected ? selected.label : null, image)
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
        src={`/images/${image}`}
        alt={product.name}
        className="product-image"
        onError={(e) => {
          e.currentTarget.onerror = null
          e.currentTarget.src = `/images/${product.image}`
        }}
      />
      <h3>{product.name}</h3>
      <p className="price">₹{product.price}</p>

      {hasVariants && useSwatches && (
        <div className="variant-swatches">
          <span className="swatch-name">{selected.label}</span>
          <div className="swatch-dots">
            {variants.map((variant, index) => (
              <button
                key={variant.label}
                type="button"
                className={`swatch-dot${
                  index === selectedIndex ? ' selected' : ''
                }`}
                style={{ backgroundColor: variant.color || '#ccc' }}
                title={variant.label}
                aria-label={variant.label}
                onClick={() => setSelectedIndex(index)}
              />
            ))}
          </div>
        </div>
      )}

      {hasVariants && !useSwatches && (
        <div className="variant-list">
          {variants.map((variant, index) => (
            <button
              key={variant.label}
              type="button"
              className={`variant-pill${
                index === selectedIndex ? ' selected' : ''
              }`}
              onClick={() => setSelectedIndex(index)}
            >
              {variant.label}
            </button>
          ))}
        </div>
      )}

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