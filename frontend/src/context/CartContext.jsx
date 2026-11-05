import { createContext, useCallback, useContext, useEffect, useRef, useState } from 'react'
import { useLocation } from 'react-router-dom'
import { getCart } from '../api/cart'
import { useAuth } from './AuthContext'

const CartContext = createContext(null)

// Remembers which items (by cart name) are already in the cart, so product
// buttons can show "Added" instead of letting the same item be added twice.
export function CartProvider({ children }) {
  const { username } = useAuth()
  const { pathname } = useLocation()
  const [names, setNames] = useState(() => new Set())
  // Counts local additions. A reload that started before an item was added
  // would not include it, so its (older) answer is ignored.
  const changes = useRef(0)

  // Reload on every page change so changes made on the Cart page
  // (remove, −, placing an order) show up on the product buttons.
  useEffect(() => {
    if (!username) return

    let ignore = false
    const startedAt = changes.current
    getCart()
      .then((items) => {
        if (!ignore && changes.current === startedAt) {
          setNames(new Set(items.map((item) => item.product_name)))
        }
      })
      .catch((err) => console.error(err))

    return () => {
      ignore = true
    }
  }, [username, pathname])

  const markAdded = useCallback((name) => {
    changes.current += 1
    setNames((current) => new Set(current).add(name))
  }, [])

  const value = {
    isInCart: (name) => Boolean(username) && names.has(name),
    markAdded,
  }

  return <CartContext.Provider value={value}>{children}</CartContext.Provider>
}

// eslint-disable-next-line react-refresh/only-export-components
export function useCart() {
  return useContext(CartContext)
}
