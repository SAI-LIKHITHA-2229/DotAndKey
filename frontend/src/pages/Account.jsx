import { useEffect, useState } from 'react'
import { Link } from 'react-router-dom'
import { useAuth } from '../context/AuthContext'
import { getOrders } from '../api/cart'

function formatDate(isoString) {
  return new Date(isoString).toLocaleDateString('en-IN', {
    weekday: 'short',
    day: 'numeric',
    month: 'long',
    year: 'numeric',
  })
}

function getStatus(isoString, now) {
  const ageDays = (now - new Date(isoString).getTime()) / 86400000
  if (ageDays > 6) return 'Delivered'
  if (ageDays > 2) return 'Out for delivery'
  return 'Order confirmed'
}

function Account() {
  const { username } = useAuth()
  const [orders, setOrders] = useState([])
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState('')

  useEffect(() => {
    async function loadOrders() {
      try {
        const data = await getOrders()
        const now = Date.now()
        setOrders(
          data.map((order) => ({
            ...order,
            status: getStatus(order.created_at, now),
          }))
        )
      } catch (err) {
        console.error(err)
        setError("Couldn't load your orders.")
      } finally {
        setLoading(false)
      }
    }

    loadOrders()
  }, [])

  return (
    <section className="account-section">
      <div className="account-top">
        <h2>My Orders</h2>
        <div className="account-user">
          <span>
            Hi, <strong>{username}</strong>
          </span>
        </div>
      </div>

      {loading && <p>Loading your orders...</p>}
      {error && <p className="auth-error">{error}</p>}

      {!loading && !error && orders.length === 0 && (
        <p className="orders-empty">
          You haven't placed any orders yet.{' '}
          <Link to="/shop">Start shopping →</Link>
        </p>
      )}

      {orders.map((order) => (
        <div className="order-card" key={order.id}>
          <div className="order-head">
            <div>
              <span className="order-id">Order #{order.id}</span>
              <span className="order-month">
                Ordered on {formatDate(order.created_at)}
              </span>
            </div>
            <span
              className={`order-status${
                order.status === 'Delivered' ? ' is-delivered' : ''
              }`}
            >
              {order.status}
            </span>
          </div>

          <p className="order-items-label">Items</p>
          <div className="order-items">
            {order.items.map((item, index) => (
              <div className="order-item" key={index}>
                <img
                  src={`/images/${item.image}`}
                  alt=""
                  onError={(e) => e.currentTarget.remove()}
                />
                <span className="order-item-name">{item.product_name}</span>
                <span className="order-item-qty">
                  ₹{item.price} × {item.quantity}
                </span>
              </div>
            ))}
          </div>

          <div className="order-foot">
            <span>Paid via {order.payment_method}</span>
            <span className="order-total">Total ₹{order.total}</span>
          </div>
          <p className="order-address">
            <strong>Delivered to:</strong> {order.address}
          </p>
        </div>
      ))}
    </section>
  )
}

export default Account