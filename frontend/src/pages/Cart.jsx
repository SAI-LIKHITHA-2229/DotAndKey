import { useEffect, useState } from 'react'
import {
  getCart,
  increaseItem,
  decreaseItem,
  removeItem,
  placeOrder,
} from '../api/cart'

const DISCOUNT_PERCENT = 20
const PAYMENT_METHODS = ['Cash on Delivery', 'UPI', 'Credit / Debit Card']

function Cart() {
  const [items, setItems] = useState([])
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState('')
  const [address, setAddress] = useState('')
  const [paymentMethod, setPaymentMethod] = useState(PAYMENT_METHODS[0])
  const [placing, setPlacing] = useState(false)
  const [orderMessage, setOrderMessage] = useState('')

  useEffect(() => {
    let ignore = false

    async function fetchCart() {
      try {
        const data = await getCart()
        if (!ignore) {
          setItems(data)
          setError('')
        }
      } catch (err) {
        console.error(err)
        if (!ignore) {
          setError("Couldn't load your cart. Is the server running?")
        }
      } finally {
        if (!ignore) {
          setLoading(false)
        }
      }
    }

    fetchCart()

    return () => {
      ignore = true
    }
  }, [])

  async function refreshCart() {
    const data = await getCart()
    setItems(data)
  }

  async function changeItem(action, id) {
    try {
      await action(id)
      await refreshCart()
      setError('')
    } catch (err) {
      console.error(err)
      setError('Something went wrong. Please try again.')
    }
  }

  async function handlePlaceOrder(event) {
    event.preventDefault()
    setError('')
    setPlacing(true)
    try {
      const result = await placeOrder(address.trim(), paymentMethod)
      setOrderMessage(
        `Order #${result.order_id} placed! Total: ₹${result.total} 🎉`
      )
      setAddress('')
      await refreshCart()
    } catch (err) {
      setError(err.message)
    } finally {
      setPlacing(false)
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
      {orderMessage && <p className="cart-empty-msg">{orderMessage}</p>}
      {error && <p className="auth-error">{error}</p>}

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

          <form onSubmit={handlePlaceOrder}>
            <label className="auth-field">
              <span>Delivery address</span>
              <input
                type="text"
                value={address}
                onChange={(e) => setAddress(e.target.value)}
                placeholder="House no, street, city, PIN"
                required
              />
            </label>

            <label className="auth-field">
              <span>Payment method</span>
              <select
                value={paymentMethod}
                onChange={(e) => setPaymentMethod(e.target.value)}
              >
                {PAYMENT_METHODS.map((method) => (
                  <option key={method} value={method}>
                    {method}
                  </option>
                ))}
              </select>
            </label>

            <button type="submit" className="checkout-btn" disabled={placing}>
              {placing ? 'Placing order...' : `Place order • ₹${total}`}
            </button>
          </form>
        </>
      )}
    </section>
  )
}

export default Cart