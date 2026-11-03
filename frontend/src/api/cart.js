import { request } from './client'

export function addToCart(product, variant, image) {
  const name = variant ? `${product.name} (${variant})` : product.name

  return request('/cart', {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
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