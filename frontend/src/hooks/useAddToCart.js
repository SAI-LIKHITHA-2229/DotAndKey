import { useState } from 'react'
import { addToCart } from '../api/cart'

const LABELS = {
  idle: 'Add to Cart',
  adding: 'Adding...',
  added: 'Added ✓',
  error: 'Try again',
}

export function useAddToCart(product) {
  const [status, setStatus] = useState('idle')

  async function add(variantLabel, image, onSuccess) {
    setStatus('adding')
    try {
      await addToCart(product, variantLabel, image)
      setStatus('added')
      if (onSuccess) onSuccess()
    } catch (error) {
      console.error(error)
      setStatus('error')
    }
    setTimeout(() => setStatus('idle'), 1400)
  }

  return { status, label: LABELS[status], add }
}