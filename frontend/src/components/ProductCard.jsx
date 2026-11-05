import { useState } from 'react'
import { useNavigate } from 'react-router-dom'
import { useAddToCart } from '../hooks/useAddToCart'
import VariantPicker from './VariantPicker'
import ProductModal from './ProductModal'

function ProductCard({ product }) {
  const variants = product.variants || []
  const [selectedIndex, setSelectedIndex] = useState(0)
  // Variant under the mouse (null when none); only changes the picture.
  const [previewIndex, setPreviewIndex] = useState(null)
  const [modalOpen, setModalOpen] = useState(false)
  const navigate = useNavigate()

  const selected = variants[selectedIndex] || null
  const { status, label, inCart, shownInCart, add } = useAddToCart(
    product,
    selected?.label ?? null,
    variants[previewIndex]?.label ?? null
  )
  const image = selected?.image || product.image
  const shownImage = variants[previewIndex]?.image || image

  return (
    <div className="product-card">
      {/* A real button, so the details can be opened with the keyboard too. */}
      <button
        type="button"
        className="product-image-btn"
        aria-label={`View details for ${product.name}`}
        onClick={() => setModalOpen(true)}
      >
        <img
          src={`/images/${shownImage}`}
          alt=""
          className="product-image"
          onError={(e) => {
            e.currentTarget.onerror = null
            e.currentTarget.src = `/images/${product.image}`
          }}
        />
      </button>
      <h3>{product.name}</h3>
      <p className="price">₹{product.price}</p>

      <VariantPicker
        variants={variants}
        selectedIndex={selectedIndex}
        previewIndex={previewIndex}
        onSelect={setSelectedIndex}
        onPreview={setPreviewIndex}
      />

      <button
        className={`add-to-cart-btn${shownInCart ? ' in-cart' : ''}`}
        disabled={status === 'adding'}
        // Already in the cart: go there to change the quantity instead.
        onClick={() => (inCart ? navigate('/cart') : add())}
      >
        {label}
      </button>

      {modalOpen && (
        <ProductModal
          product={product}
          initialIndex={selectedIndex}
          onClose={() => setModalOpen(false)}
        />
      )}
    </div>
  )
}

export default ProductCard