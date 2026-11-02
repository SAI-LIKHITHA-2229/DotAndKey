const API_URL = import.meta.env.VITE_API_URL

export async function addToCart(product, variant, image) {
  const name = variant ? `${product.name} (${variant})` : product.name

  const response = await fetch(`${API_URL}/cart`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({
      product_name: name,
      price: product.price,
      image: image || product.image,
    }),
  })

  if (!response.ok) {
    throw new Error(`Add to cart failed: HTTP ${response.status}`)
  }

  return response.json()
}