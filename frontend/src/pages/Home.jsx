import { Link } from 'react-router-dom'
import ProductCard from '../components/ProductCard'
import { useProducts } from '../hooks/useProducts'

const RECOMMENDED_NAMES = [
  'Sunscreen',
  'Face Toner',
  'Body Care',
  'Moisturizer',
  'Face Serum',
  'Face Wash',
  'Face Mask',
  'Strawberry Dew Tinted Sunscreen SPF 50+ PA++++ With New-Age UV Filters',
]

function Home() {
  const { products, loading, error } = useProducts()
  const recommended = products.filter((product) =>
    RECOMMENDED_NAMES.includes(product.name)
  )

  return (
    <>
      <section className="hero">
        <div className="hero-content">
          <h1>Skincare, Backed by Science</h1>
          <p>Dermat-approved formulas for glowing, healthy skin.</p>
          <Link to="/shop" className="shop-now-btn">
            Shop Now
          </Link>
        </div>
      </section>

      <section className="banners">
        <img
          src="/images/banner-offer.jpg"
          alt="Upto 20% off and free gifts"
          className="banner-img"
        />
        <img
          src="/images/banner-bestsellers.jpg"
          alt="Bestsellers you loved"
          className="banner-img"
        />
      </section>

      <section className="bestsellers">
        <h2>Our Recommendations</h2>
        {loading && <p>Loading products...</p>}
        {error && <p className="auth-error">{error}</p>}
        <div className="product-grid">
          {recommended.map((product) => (
            <ProductCard key={product.id} product={product} />
          ))}
        </div>
      </section>
    </>
  )
}

export default Home