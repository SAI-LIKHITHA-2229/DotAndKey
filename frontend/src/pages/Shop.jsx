import { products } from '../data/products'
import ProductCard from '../components/ProductCard'

function Shop() {
  return (
    <section className="featured">
      <h2>All Products</h2>
      <div className="product-grid">
        {products.map((product) => (
          <ProductCard key={product.id} product={product} />
        ))}
      </div>
    </section>
  )
}

export default Shop