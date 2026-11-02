import { Link } from 'react-router-dom'

function Home() {
  return (
    <section className="hero">
      <div className="hero-content">
        <h1>Skincare, Backed by Science</h1>
        <p>Dermat-approved formulas for glowing, healthy skin.</p>
        <Link to="/shop" className="shop-now-btn">Shop Now</Link>
      </div>
    </section>
  )
}

export default Home