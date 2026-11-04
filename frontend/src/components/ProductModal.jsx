import { useEffect, useState } from 'react'
import { createPortal } from 'react-dom'
import { useAddToCart } from '../hooks/useAddToCart'
import VariantPicker from './VariantPicker'

function ProductModal({ product, initialIndex, onClose }) {
  const variants = product.variants || []
  const [selectedIndex, setSelectedIndex] = useState(initialIndex)
  const { status, label, add } = useAddToCart(product)

  const selected = variants[selectedIndex] || null
  const image = selected?.image || product.image

  useEffect(() => {
    function handleKey(event) {
      if (event.key === 'Escape') onClose()
    }
    window.addEventListener('keydown', handleKey)
    return () => window.removeEventListener('keydown', handleKey)
  }, [onClose])

  return createPortal(
    <div className="modal-overlay active" onClick={onClose}>
      <div className="modal-content" onClick={(e) => e.stopPropagation()}>
        <span
          className="close-btn"
          role="button"
          aria-label="Close"
          onClick={onClose}
        >
          &times;
        </span>

        <img
          src={`/images/${image}`}
          alt={product.name}
          onError={(e) => {
            e.currentTarget.onerror = null
            e.currentTarget.src = `/images/${product.image}`
          }}
        />

        <div className="modal-details">
          <h2>{product.name}</h2>
          <p>₹{product.price}</p>

          <VariantPicker
            id="modalVariants"
            variants={variants}
            selectedIndex={selectedIndex}
            onSelect={setSelectedIndex}
          />

          <button
            id="modalAddToCart"
            disabled={status === 'adding'}
            onClick={() =>
              add(selected ? selected.label : null, image, () =>
                setTimeout(onClose, 600)
              )
            }
          >
            {label}
          </button>
        </div>
      </div>
    </div>,
    document.body
  )
}

export default ProductModal