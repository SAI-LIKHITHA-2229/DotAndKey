import { request } from './client'

const JSON_HEADERS = { 'Content-Type': 'application/json' }

export function getAddresses() {
  return request('/addresses')
}

export function addAddress(address) {
  return request('/addresses', {
    method: 'POST',
    headers: JSON_HEADERS,
    body: JSON.stringify(address),
  })
}

export function updateAddress(id, address) {
  return request(`/addresses/${id}`, {
    method: 'PUT',
    headers: JSON_HEADERS,
    body: JSON.stringify(address),
  })
}

export function deleteAddress(id) {
  return request(`/addresses/${id}`, { method: 'DELETE' })
}