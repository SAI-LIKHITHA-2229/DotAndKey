import { useState } from 'react'

const STATES = [
  'Andhra Pradesh', 'Arunachal Pradesh', 'Assam', 'Bihar', 'Chhattisgarh',
  'Goa', 'Gujarat', 'Haryana', 'Himachal Pradesh', 'Jharkhand', 'Karnataka',
  'Kerala', 'Madhya Pradesh', 'Maharashtra', 'Manipur', 'Meghalaya',
  'Mizoram', 'Nagaland', 'Odisha', 'Punjab', 'Rajasthan', 'Sikkim',
  'Tamil Nadu', 'Telangana', 'Tripura', 'Uttar Pradesh', 'Uttarakhand',
  'West Bengal', 'Andaman and Nicobar Islands', 'Chandigarh',
  'Dadra and Nagar Haveli and Daman and Diu', 'Delhi', 'Jammu and Kashmir',
  'Ladakh', 'Lakshadweep', 'Puducherry',
]

const TYPES = ['Home', 'Work', 'Other']

const EMPTY = {
  full_name: '',
  mobile: '',
  pincode: '',
  flat: '',
  area: '',
  landmark: '',
  city: '',
  state: '',
  type: 'Home',
}

// Quick checks in the browser so the user sees mistakes instantly.
// The server checks again, so this is only for convenience.
function validate(values) {
  if (values.full_name.trim().length < 2) return 'Enter your full name'
  if (!/^[6-9]\d{9}$/.test(values.mobile.trim())) {
    return 'Enter a valid 10-digit mobile number'
  }
  if (!/^[1-9]\d{5}$/.test(values.pincode.trim())) {
    return 'Enter a valid 6-digit PIN code'
  }
  if (!values.flat.trim()) return 'Enter your flat / house number'
  if (!values.area.trim()) return 'Enter your area / street'
  if (!values.city.trim()) return 'Enter your city'
  if (!values.state) return 'Choose a state'
  return ''
}

// initial: an existing address (when editing) or nothing (when adding).
// onSave:  async function that receives the form values.
// onCancel: called when the user clicks Cancel.
function AddressForm({ initial, onSave, onCancel }) {
  const [values, setValues] = useState(() => ({ ...EMPTY, ...initial }))
  const [error, setError] = useState('')
  const [saving, setSaving] = useState(false)

  function setField(name, value) {
    setValues((current) => ({ ...current, [name]: value }))
    setError('')
  }

  async function handleSubmit(event) {
    event.preventDefault()

    const problem = validate(values)
    if (problem) {
      setError(problem)
      return
    }

    setSaving(true)
    try {
      await onSave(values)
    } catch (err) {
      console.error(err)
      setError(err.message)
      setSaving(false)
    }
  }

  return (
    <form onSubmit={handleSubmit}>
      <label className="auth-field">
        <span>Full name</span>
        <input
          type="text"
          value={values.full_name}
          onChange={(e) => setField('full_name', e.target.value)}
        />
      </label>

      <label className="auth-field">
        <span>Mobile number</span>
        <input
          type="tel"
          inputMode="numeric"
          maxLength={10}
          value={values.mobile}
          onChange={(e) => setField('mobile', e.target.value.replace(/\D/g, ''))}
        />
      </label>

      <label className="auth-field">
        <span>PIN code</span>
        <input
          type="text"
          inputMode="numeric"
          maxLength={6}
          value={values.pincode}
          onChange={(e) => setField('pincode', e.target.value.replace(/\D/g, ''))}
        />
      </label>

      <label className="auth-field">
        <span>Flat / House no.</span>
        <input
          type="text"
          value={values.flat}
          onChange={(e) => setField('flat', e.target.value)}
        />
      </label>

      <label className="auth-field">
        <span>Area / Street</span>
        <input
          type="text"
          value={values.area}
          onChange={(e) => setField('area', e.target.value)}
        />
      </label>

      <label className="auth-field">
        <span>Landmark (optional)</span>
        <input
          type="text"
          value={values.landmark || ''}
          onChange={(e) => setField('landmark', e.target.value)}
        />
      </label>

      <label className="auth-field">
        <span>City</span>
        <input
          type="text"
          value={values.city}
          onChange={(e) => setField('city', e.target.value)}
        />
      </label>

      <label className="auth-field">
        <span>State</span>
        <select
          value={values.state}
          onChange={(e) => setField('state', e.target.value)}
        >
          <option value="">Select state</option>
          {STATES.map((state) => (
            <option key={state} value={state}>
              {state}
            </option>
          ))}
        </select>
      </label>

      <label className="auth-field">
        <span>Address type</span>
        <select
          value={values.type}
          onChange={(e) => setField('type', e.target.value)}
        >
          {TYPES.map((type) => (
            <option key={type} value={type}>
              {type}
            </option>
          ))}
        </select>
      </label>

      {error && <p>{error}</p>}

      <button type="submit" className="checkout-btn" disabled={saving}>
        {saving ? 'Saving...' : 'Save address'}
      </button>
      <button type="button" className="remove-btn" onClick={onCancel}>
        Cancel
      </button>
    </form>
  )
}

export default AddressForm