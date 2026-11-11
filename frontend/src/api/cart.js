import { request } from './client'

const JSON_HEADERS = { 'Content-Type': 'application/json' }

// The name a product (and chosen variant) is stored under in the cart.
export function cartItemName(product, variant) {
  return variant ? `${product.name} (${variant})` : product.name
}

// Only says which product/variant to add; the server looks up the
// name, price and image itself so they can't be tampered with.
export function addToCart(product, variant) {
  return request('/cart', {
    method: 'POST',
    headers: JSON_HEADERS,
    body: JSON.stringify({ product_id: product.id, variant: variant || null }),
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

// Asks the server for all checkout numbers
// (discount, free shipping, gifts, payment methods with totals).
export function getCheckoutSummary() {
  return request('/checkout/summary')
}

// Changed: sends the saved address id instead of typed text.
export function placeOrder({ addressId, paymentMethod, paymentOption, gifts }) {
  return request('/orders', {
    method: 'POST',
    headers: JSON_HEADERS,
    body: JSON.stringify({
      address_id: addressId,
      payment_method: paymentMethod,
      payment_option: paymentOption,
      gifts,
    }),
  })
}

export function getOrders() {
  return request('/orders')
}