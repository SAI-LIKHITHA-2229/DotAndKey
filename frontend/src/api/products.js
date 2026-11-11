import { request } from './client'

export function getProducts() {
  return request('/products')
}
