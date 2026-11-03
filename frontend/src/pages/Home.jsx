import { Link } from 'react-router-dom'
import { products } from '../data/products'
import ProductCard from '../components/ProductCard'

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