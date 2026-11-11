import { useEffect, useRef, useState } from 'react'
import { Link } from 'react-router-dom'
import { useAuth } from '../context/AuthContext'
import { getOrders } from '../api/cart'
import {
  getAddresses,
  addAddress,
  updateAddress,
  deleteAddress,
} from '../api/addresses'
import AddressForm from '../components/AddressForm'

function formatDate(isoString) {
  return new Date(isoString).toLocaleDateString('en-IN', {
    weekday: 'short',
    day: 'numeric',
    month: 'long',
    year: 'numeric',
  })
}

// Labels for the statuses the server stores on each order.
const ORDER_STATUS_LABELS = {
  confirmed: 'Order confirmed',
  shipped: 'Shipped',
  delivered: 'Delivered',
  cancelled: 'Cancelled',
}

function paymentText(order) {
  if (order.payment_status === 'demo_paid') {
    return `Paid via ${order.payment_method} (demo, no money charged)`
  }
  return `${order.payment_method} · payment due on delivery`
}

function Account() {
  const { username } = useAuth()
  const [orders, setOrders] = useState([])
  const [addresses, setAddresses] = useState([])
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState('')

  // editing is: null (form closed), 'new' (adding), or an address (editing it)
  const [editing, setEditing] = useState(null)
  const formRef = useRef(null)

  // When the form opens (Edit or Add), scroll to it and focus the first field.
  useEffect(() => {
    if (editing === null || !formRef.current) return
    formRef.current.scrollIntoView({ behavior: 'smooth', block: 'start' })
    formRef.current.querySelector('input')?.focus({ preventScroll: true })
  }, [editing])

  useEffect(() => {
    async function loadAll() {
      try {
        const [orderData, addressData] = await Promise.all([
          getOrders(),
          getAddresses(),
        ])
        setOrders(orderData)
        setAddresses(addressData)
      } catch (err) {
        console.error(err)
        setError("Couldn't load your account details.")
      } finally {
        setLoading(false)
      }
    }

    loadAll()
  }, [])

  // Called by the form. If it throws, the form shows the error.
  async function handleSaveAddress(values) {
    if (editing === 'new') {
      await addAddress(values)
    } else {
      await updateAddress(editing.id, values)
    }
    setAddresses(await getAddresses())
    setEditing(null)
  }

  async function handleDeleteAddress(id) {
    if (!window.confirm('Delete this address?')) return

    try {
      await deleteAddress(id)
      setAddresses(await getAddresses())
    } catch (err) {
      console.error(err)
      setError('Could not delete the address. Please try again.')
    }
  }

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

      {loading && <p>Loading your account...</p>}
      {error && <p className="auth-error">{error}</p>}

      {/* Saved addresses */}
      {!loading && (
        <div className="order-card address-book">
          <div className="address-book-head">
            <h3>My addresses</h3>
            {addresses.length > 0 && (
              <span className="address-count">
                {addresses.length} saved
              </span>
            )}
          </div>

          <div className="address-grid">
            {addresses.map((a) => (
              <div
                className={`address-card${editing?.id === a.id ? ' is-editing' : ''}`}
                key={a.id}
              >
                <span className="address-type">{a.type}</span>
                <strong className="address-name">{a.full_name}</strong>
                <p className="address-text">
                  {a.flat}, {a.area}
                  {a.landmark ? `, ${a.landmark}` : ''}
                  <br />
                  {a.city}, {a.state} – {a.pincode}
                </p>
                <p className="address-phone">📞 {a.mobile}</p>

                <div className="address-actions">
                  <button
                    type="button"
                    className="address-btn"
                    onClick={() => setEditing(a)}
                  >
                    Edit
                  </button>
                  <button
                    type="button"
                    className="address-btn is-danger"
                    onClick={() => handleDeleteAddress(a.id)}
                  >
                    Delete
                  </button>
                </div>
              </div>
            ))}

            {editing === null && (
              <button
                type="button"
                className="address-add"
                onClick={() => setEditing('new')}
              >
                <span className="address-add-plus">+</span>
                {addresses.length === 0
                  ? "You haven't saved any addresses yet. Add one"
                  : 'Add new address'}
              </button>
            )}
          </div>

          {editing !== null && (
            <div ref={formRef} className="address-form-anchor">
              <h4 className="address-form-title">
                {editing === 'new' ? 'Add a new address' : 'Edit address'}
              </h4>
              <AddressForm
                key={editing === 'new' ? 'new' : editing.id}
                initial={editing === 'new' ? null : editing}
                onSave={handleSaveAddress}
                onCancel={() => setEditing(null)}
              />
            </div>
          )}
        </div>
      )}

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
                order.status === 'delivered' ? ' is-delivered' : ''
              }`}
            >
              {ORDER_STATUS_LABELS[order.status] || order.status}
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
            <span>{paymentText(order)}</span>
            <span className="order-total">Total ₹{order.total}</span>
          </div>
          <p className="order-address">
            <strong>Delivery address:</strong> {order.address}
          </p>
        </div>
      ))}
    </section>
  )
}

export default Account