import { useEffect, useRef, useState } from 'react'
import { addToCart, cartItemName } from '../api/cart'
import { useCart } from '../context/CartContext'

const LABELS = {
  idle: 'Add to Cart',
  adding: 'Adding...',
  added: 'Added ✓',
  error: 'Try again',
  inCart: 'Added ✓ · Go to cart',
}

// variantLabel: the selected variant (or null). inCart tells the button
// that this exact item is already in the cart, so it should not add it again.
// previewLabel: the variant under the mouse (or null). While set, the label
// and shownInCart describe that variant instead, like the picture does.
export function useAddToCart(product, variantLabel, previewLabel = null) {
  const [status, setStatus] = useState('idle')
  const { isInCart, markAdded } = useCart()
  const inCart = isInCart(cartItemName(product, variantLabel))

  // Timer that turns "Added ✓" / "Try again" back into the normal label.
  // Cleared on unmount so it never fires for a card that is gone.
  const resetTimer = useRef(null)
  useEffect(() => () => clearTimeout(resetTimer.current), [])

  async function add(onSuccess) {
    clearTimeout(resetTimer.current)
    setStatus('adding')
    try {
      await addToCart(product, variantLabel)
      markAdded(cartItemName(product, variantLabel))
      setStatus('added')
      if (onSuccess) onSuccess()
    } catch (error) {
      console.error(error)
      setStatus('error')
    }
    resetTimer.current = setTimeout(() => setStatus('idle'), 1400)
  }

  const previewing = previewLabel !== null && previewLabel !== variantLabel
  const shownInCart = previewing
    ? isInCart(cartItemName(product, previewLabel))
    : inCart
  // "Adding..." / "Added ✓" belong to the selected variant, not the hovered one.
  const shownStatus = previewing ? 'idle' : status
  const label =
    shownStatus === 'idle' && shownInCart ? LABELS.inCart : LABELS[shownStatus]

  return { status, label, inCart, shownInCart, add }
}
