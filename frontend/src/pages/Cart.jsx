import { useEffect, useState } from 'react'
import { getCart, increaseItem, decreaseItem, removeItem } from '../api/cart'

const DISCOUNT_PERCENT = 20

function Cart() {
  const [items, setItems] = useState([])
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState('')

  async function loadCart() {
    try {
      const data = await getCart()
      setItems(data)
      setError('')
    } catch (err) {
      console.error(err)
      setError("Couldn't load your cart. Is the server running?")
    } finally {
      setLoading(false)
    }
  }

  useEffect(() => {
    loadCart()
  }, [])

  async function changeItem(action, id) {
    try {
      await action(id)
      await loadCart()
    } catch (err) {
      console.error(err)
      setError('Something went wrong. Please try again.')
    }
  }

  const subtotal = items.reduce(
    (sum, item) => sum + item.price * item.quantity,
    0
  )
  const discount = Math.round((subtotal * DISCOUNT_PERCENT) / 100)
  const total = subtotal - discount

  if (loading) {
    return (
      <section className="cart-section">
        <p>Loading your cart...</p>
      </section>
    )
  }

  return (
    <section className="cart-section">
      <h2>Your Cart</h2>
      {error && <p>{error}</p>}

      {items.length === 0 ? (
        <p>Your cart is empty.</p>
      ) : (
        <>
          {items.map((item) => (
            <div className="cart-item" key={item.id}>
              <span>{item.product_name}</span>
              <img
                src={`/images/${item.image}`}
                alt={item.product_name}
                className="cart-item-image"
              />
              <span>
                ₹{item.price} x {item.quantity}
              </span>
              <button
                className="decrease-btn"
                onClick={() => changeItem(decreaseItem, item.id)}
              >
                −
              </button>
              <button
                className="increase-btn"
                onClick={() => changeItem(increaseItem, item.id)}
              >
                +
              </button>
              <button
                className="remove-btn"
                onClick={() => changeItem(removeItem, item.id)}
              >
                Remove
              </button>
            </div>
          ))}

          <p id="cartTotal">
            <span className="bill-row">
              <span>Subtotal</span>
              <span>₹{subtotal}</span>
            </span>
            <span className="bill-row bill-discount">
              <span>Discount ({DISCOUNT_PERCENT}% off)</span>
              <span>− ₹{discount}</span>
            </span>
            <span className="bill-row bill-grand">
              <span>Total payable</span>
              <span>₹{total}</span>
            </span>
          </p>
        </>
      )}
    </section>
  )
}

export default Cart