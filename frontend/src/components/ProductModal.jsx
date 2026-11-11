import { useEffect, useId, useRef, useState } from 'react'
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

  const titleId = useId()
  const dialogRef = useRef(null)
  const closeRef = useRef(null)

  // Move focus into the dialog, and give it back to whatever opened it.
  useEffect(() => {
    const opener = document.activeElement
    closeRef.current?.focus()
    return () => opener?.focus?.()
  }, [])

  // Esc closes; Tab and Shift+Tab stay inside the dialog.
  useEffect(() => {
    function handleKey(event) {
      if (event.key === 'Escape') {
        onClose()
        return
      }
      if (event.key !== 'Tab' || !dialogRef.current) return

      const focusable = dialogRef.current.querySelectorAll('button:not([disabled])')
      const first = focusable[0]
      const last = focusable[focusable.length - 1]
      if (event.shiftKey && document.activeElement === first) {
        event.preventDefault()
        last.focus()
      } else if (!event.shiftKey && document.activeElement === last) {
        event.preventDefault()
        first.focus()
      }
    }
    window.addEventListener('keydown', handleKey)
    return () => window.removeEventListener('keydown', handleKey)
  }, [onClose])

  return createPortal(
    <div className="modal-overlay active" onClick={onClose}>
      <div
        ref={dialogRef}
        className="modal-content"
        role="dialog"
        aria-modal="true"
        aria-labelledby={titleId}
        onClick={(e) => e.stopPropagation()}
      >
        <button
          ref={closeRef}
          type="button"
          className="close-btn"
          aria-label="Close"
          onClick={onClose}
        >
          &times;
        </button>

        <img
          src={`/images/${shownImage}`}
          alt={product.name}
          onError={(e) => {
            e.currentTarget.onerror = null
            e.currentTarget.src = `/images/${product.image}`
          }}
        />

        <div className="modal-details">
          <h2 id={titleId}>{product.name}</h2>
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
                : add(() => setTimeout(onClose, 600))
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