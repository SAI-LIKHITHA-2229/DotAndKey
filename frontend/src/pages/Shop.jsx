import ProductCard from '../components/ProductCard'
import { useProducts } from '../hooks/useProducts'

function Shop() {
  const { products, loading, error } = useProducts()

  return (
    <section className="featured">
      <h2>All Products</h2>
      {loading && <p>Loading products...</p>}
      {error && <p className="auth-error">{error}</p>}
      <div className="product-grid">
        {products.map((product) => (
          <ProductCard key={product.id} product={product} />
        ))}
      </div>
    </section>
  )
}

export default Shop
