import { request } from './client'

const JSON_HEADERS = { 'Content-Type': 'application/json' }

export function addToCart(product, variant, image) {
  const name = variant ? `${product.name} (${variant})` : product.name

  return request('/cart', {
    method: 'POST',
    headers: JSON_HEADERS,
    body: JSON.stringify({
      product_name: name,
      price: product.price,
      image: image || product.image,
    }),
  })
}

export function getCart() {
  return request('/cart')
}

export function increaseItem(id) {
  return request(`/cart/${id}/increase`, { method: 'PUT' })
}

export function decreaseItem(id) {
  return request(`/cart/${id}/decrease`, { method: 'PUT' })
}

export function removeItem(id) {
  return request(`/cart/${id}`, { method: 'DELETE' })
}

// New: asks the server for all checkout numbers
// (discount, free shipping, gifts, payment methods with totals).
export function getCheckoutSummary() {
  return request('/checkout/summary')
}

// Changed: now sends the payment method id, the chosen option
// (like "Visa"), and the chosen free gifts.
export function placeOrder({ address, paymentMethod, paymentOption, gifts }) {
  return request('/orders', {
    method: 'POST',
    headers: JSON_HEADERS,
    body: JSON.stringify({
      address,
      payment_method: paymentMethod,
      payment_option: paymentOption,
      gifts,
    }),
  })
}

export function getOrders() {
  return request('/orders')
}