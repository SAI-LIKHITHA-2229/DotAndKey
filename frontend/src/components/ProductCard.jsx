import { useState } from 'react'
import { useAddToCart } from '../hooks/useAddToCart'
import VariantPicker from './VariantPicker'
import ProductModal from './ProductModal'

function ProductCard({ product }) {
  const variants = product.variants || []
  const [selectedIndex, setSelectedIndex] = useState(0)
  const [modalOpen, setModalOpen] = useState(false)
  const { status, label, add } = useAddToCart(product)

  const selected = variants[selectedIndex] || null
  const image = selected?.image || product.image

  return (
    <div className="product-card">
      <img
        src={`/images/${image}`}
        alt={product.name}
        className="product-image"
        onClick={() => setModalOpen(true)}
        onError={(e) => {
          e.currentTarget.onerror = null
          e.currentTarget.src = `/images/${product.image}`
        }}
      />
      <h3>{product.name}</h3>
      <p className="price">₹{product.price}</p>

      <VariantPicker
        variants={variants}
        selectedIndex={selectedIndex}
        onSelect={setSelectedIndex}
      />

      <button
        className="add-to-cart-btn"
        disabled={status === 'adding'}
        onClick={() => add(selected ? selected.label : null, image)}
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