import { useEffect, useState } from 'react'
import { Link, useNavigate } from 'react-router-dom'
import {
  getCart,
  getCheckoutSummary,
  increaseItem,
  decreaseItem,
  removeItem,
  placeOrder,
} from '../api/cart'

// Fetch the cart and the server's checkout numbers together.
async function fetchAll() {
  const [items, summary] = await Promise.all([getCart(), getCheckoutSummary()])
  return { items, summary }
}

function Cart() {
  const navigate = useNavigate()

  const [items, setItems] = useState([])
  const [summary, setSummary] = useState(null)
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState('')

  const [address, setAddress] = useState('')
  const [methodId, setMethodId] = useState('cod')
  const [option, setOption] = useState('')
  const [selectedGifts, setSelectedGifts] = useState([])

  const [placing, setPlacing] = useState(false)
  const [placedOrder, setPlacedOrder] = useState(null)

  // Save fresh data into state. If the cart shrank, keep only as many
  // gifts as the server now allows.
  function applyData({ items, summary }) {
    setItems(items)
    setSummary(summary)
    setSelectedGifts((current) => current.slice(0, summary.gifts.max))
    setError('')
  }

  // Load once when the page opens.
  useEffect(() => {
    let ignore = false

    fetchAll()
      .then((data) => {
        if (!ignore) applyData(data)
      })
      .catch((err) => {
        console.error(err)
        if (!ignore) setError("Couldn't load your cart. Is the server running?")
      })
      .finally(() => {
        if (!ignore) setLoading(false)
      })

    return () => {
      ignore = true
    }
  }, [])

  // Load again after +, - or Remove.
  async function changeItem(action, id) {
    try {
      await action(id)
      applyData(await fetchAll())
    } catch (err) {
      console.error(err)
      setError('Something went wrong. Please try again.')
    }
  }

  function chooseMethod(method) {
    setMethodId(method.id)
    setOption(method.options[0] || '')
  }

  function toggleGift(name) {
    setSelectedGifts((current) => {
      if (current.includes(name)) {
        return current.filter((g) => g !== name)
      }
      if (current.length >= summary.gifts.max) {
        return current
      }
      return [...current, name]
    })
  }

  async function handlePlaceOrder(event) {
    event.preventDefault()
    const method = summary.methods.find((m) => m.id === methodId)

    const order = {
      address: address.trim(),
      paymentMethod: method.id,
      paymentOption: option,
      gifts: selectedGifts,
    }

    // Prepaid methods go to the PIN page first (built in the next step).
    if (method.prepaid) {
      navigate('/payment', { state: order })
      return
    }

    setPlacing(true)
    setError('')
    try {
      const result = await placeOrder(order)
      setPlacedOrder(result)
    } catch (err) {
      console.error(err)
      setError(err.message)
    } finally {
      setPlacing(false)
    }
  }

  if (loading) {
    return (
      <section className="cart-section">
        <p>Loading your cart...</p>
      </section>
    )
  }

  if (placedOrder) {
    return (
      <section className="cart-section">
        <div className="order-success-card">
          <h2>Order placed 🎉</h2>
          <p>
            Order #{placedOrder.order_id} • ₹{placedOrder.total}
          </p>
          <Link to="/account">View my orders</Link>
        </div>
      </section>
    )
  }

  const method = summary?.methods.find((m) => m.id === methodId)

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
              <span>₹{summary.subtotal}</span>
            </span>
            <span className="bill-row bill-discount">
              <span>Discount ({summary.discount_percent}% off)</span>
              <span>− ₹{summary.discount}</span>
            </span>
            {method.prepaid && (
              <span className="bill-row bill-discount">
                <span>Prepaid extra ({summary.prepaid_percent}% off)</span>
                <span>− ₹{method.discount}</span>
              </span>
            )}
            <span className="bill-row bill-grand">
              <span>Total payable</span>
              <span>₹{method.total}</span>
            </span>
          </p>

          {/* Free shipping message */}
          <div className="free-shipping">
            {summary.free_shipping
              ? '🎉 Woohoo! Free shipping on this order'
              : `Add ₹${summary.free_shipping_remaining} more to unlock free shipping`}
          </div>

          {/* Free gifts */}
          <div className="free-gifts">
            <div className="free-gifts-head">
              {summary.gifts.all_unlocked
                ? '🎁 All free gifts unlocked and added to your order!'
                : summary.gifts.max === 0
                  ? `🎁 Add ₹${summary.gifts.next_unlock_in} more to unlock your first free gift`
                  : `🎁 Choose ${summary.gifts.max} free gift${summary.gifts.max > 1 ? 's' : ''} (${selectedGifts.length}/${summary.gifts.max} selected). Add ₹${summary.gifts.next_unlock_in} more for one more.`}
            </div>

            <div className="free-gifts-list">
              {summary.gifts.available.map((gift) => {
                const chosen =
                  summary.gifts.all_unlocked || selectedGifts.includes(gift.name)
                const locked = summary.gifts.max === 0

                return (
                  <button
                    type="button"
                    key={gift.name}
                    className={`gift-pill${chosen ? ' selected' : ''}`}
                    disabled={locked || summary.gifts.all_unlocked}
                    onClick={() => toggleGift(gift.name)}
                  >
                    <img src={`/images/${gift.image}`} alt="" width="36" />
                    <span>{gift.name}</span>
                  </button>
                )
              })}
            </div>
          </div>

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

            {/* Payment methods */}
            <div className="payment-options">
              {summary.methods.map((m) => (
                <label className="pay-option" key={m.id}>
                  <input
                    type="radio"
                    name="payment"
                    checked={m.id === methodId}
                    onChange={() => chooseMethod(m)}
                  />
                  <span>
                    <strong>{m.title}</strong>
                    <br />
                    <small>{m.sub}</small>
                    {m.prepaid && (
                      <>
                        <br />
                        <small className="prepaid-note">
                          ✨ Extra {summary.prepaid_percent}% off on prepaid payment
                        </small>
                      </>
                    )}
                  </span>
                  <span>₹{m.total}</span>
                </label>
              ))}
            </div>

            {method.options.length > 0 && (
              <label className="auth-field">
                <span>Choose {method.title}</span>
                <select
                  className="pay-select"
                  value={option || method.options[0]}
                  onChange={(e) => setOption(e.target.value)}
                >
                  {method.options.map((o) => (
                    <option key={o} value={o}>
                      {o}
                    </option>
                  ))}
                </select>
              </label>
            )}

            <button type="submit" className="checkout-btn" disabled={placing}>
              {placing
                ? 'Placing order...'
                : method.prepaid
                  ? `Pay • ₹${method.total}`
                  : `Place order • ₹${method.total}`}
            </button>
          </form>
        </>
      )}
    </section>
  )
}

export default Cart