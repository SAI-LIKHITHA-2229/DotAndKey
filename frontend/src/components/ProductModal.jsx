import { useEffect, useState } from 'react'
import { createPortal } from 'react-dom'
import { useNavigate } from 'react-router-dom'
import { useAddToCart } from '../hooks/useAddToCart'
import VariantPicker from './VariantPicker'

function ProductModal({ product, initialIndex, onClose }) {
  const variants = product.variants || []
  const [selectedIndex, setSelectedIndex] = useState(initialIndex)
  // Variant under the mouse (null when none); only changes the picture.
  const [previewIndex, setPreviewIndex] = useState(null)
  const navigate = useNavigate()

  const selected = variants[selectedIndex] || null
  const { status, label, inCart, shownInCart, add } = useAddToCart(
    product,
    selected?.label ?? null,
    variants[previewIndex]?.label ?? null
  )
  const image = selected?.image || product.image
  const shownImage = variants[previewIndex]?.image || image

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
          src={`/images/${shownImage}`}
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
            previewIndex={previewIndex}
            onSelect={setSelectedIndex}
            onPreview={setPreviewIndex}
          />

          <button
            id="modalAddToCart"
            className={shownInCart ? 'in-cart' : undefined}
            disabled={status === 'adding'}
            // Already in the cart: go there to change the quantity instead.
            onClick={() =>
              inCart
                ? navigate('/cart')
                : add(image, () => setTimeout(onClose, 600))
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