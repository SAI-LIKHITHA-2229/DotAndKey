import { products } from './data/products'
import ProductCard from './components/ProductCard'

function App() {
  return (
    <div>
      <h1>Dot & Key</h1>
      <div className="product-grid">
        {products.map((product) => (
          <ProductCard key={product.id} product={product} />
        ))}
      </div>
    </div>
  )
}

export default App

