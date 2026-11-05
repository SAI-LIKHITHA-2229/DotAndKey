import { useRef, useState } from 'react'
import { Link, Navigate, useLocation } from 'react-router-dom'
import { placeOrder } from '../api/cart'

function Payment() {
  // The Cart page sends the order details here through the route "state".
  const { state: order } = useLocation()

  const [digits, setDigits] = useState(['', '', '', ''])
  const [error, setError] = useState('')
  const [paying, setPaying] = useState(false)
  const [placedOrder, setPlacedOrder] = useState(null)
  const boxes = useRef([])

  // Opened this page directly (no order details)? Go back to the cart.
  if (!order) {
    return <Navigate to="/cart" replace />
  }

  function handleDigit(index, value) {
    const digit = value.replace(/\D/g, '').slice(0, 1)

    setDigits((current) => {
      const next = [...current]
      next[index] = digit
      return next
    })
    setError('')

    // Jump to the next box after typing a digit.
    if (digit && index < 3) {
      boxes.current[index + 1].focus()
    }
  }

  function handleKeyDown(index, event) {
    // Backspace on an empty box goes back one box.
    if (event.key === 'Backspace' && !digits[index] && index > 0) {
      boxes.current[index - 1].focus()
    }
  }

  async function handlePay(event) {
    event.preventDefault()

    if (digits.some((d) => d === '')) {
      setError('Enter your 4-digit PIN')
      return
    }

    setPaying(true)
    try {
      const result = await placeOrder(order)
      setPlacedOrder(result)
    } catch (err) {
      console.error(err)
      setError(err.message)
    } finally {
      setPaying(false)
    }
  }

  if (placedOrder) {
    return (
      <section className="cart-section">
        <div className="order-success-card">
          <h2>Payment successful 🎉</h2>
          <p>
            Order #{placedOrder.order_id} • ₹{placedOrder.total}
          </p>
          <Link to="/account">View my orders</Link>
        </div>
      </section>
    )
  }

  return (
    <section className="cart-section">
      <h2>Secure payment</h2>
      <p>Paying with {order.paymentOption || order.paymentMethod}.</p>
      <p className="demo-note" role="note">
        <strong>Demo payment:</strong> no real money is charged and no card
        details are collected. Any 4-digit PIN works.
      </p>

      <form onSubmit={handlePay}>
        <div className="pin-boxes">
          {digits.map((digit, index) => (
            <input
              key={index}
              ref={(el) => (boxes.current[index] = el)}
              className="pin-box"
              type="password"
              inputMode="numeric"
              maxLength={1}
              value={digit}
              onChange={(e) => handleDigit(index, e.target.value)}
              onKeyDown={(e) => handleKeyDown(index, e)}
              autoFocus={index === 0}
            />
          ))}
        </div>

        {error && <p>{error}</p>}

        <button type="submit" className="checkout-btn" disabled={paying}>
          {paying ? 'Processing...' : 'Pay now'}
        </button>
        <p>
          <Link to="/cart">← Back to cart</Link>
        </p>
      </form>
    </section>
  )
}

export default Payment