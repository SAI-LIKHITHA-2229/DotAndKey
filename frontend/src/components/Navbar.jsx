import { Link } from 'react-router-dom'

const navItems = [
  {
    to: '/',
    label: 'Home',
    icon: (
      <>
        <path d="M4 11.5 12 4l8 7.5" />
        <path d="M6 10v10h12V10" />
        <path d="M10 20v-6h4v6" />
      </>
    ),
  },
  {
    to: '/shop',
    label: 'Shop',
    icon: (
      <>
        <path d="M5 7h14l1 13H4z" />
        <path d="M8.5 7V5.5a3.5 3.5 0 0 1 7 0V7" />
      </>
    ),
  },
  {
    to: '/cart',
    label: 'Cart',
    icon: (
      <>
        <path d="M3 4h2l2.3 11.4a2 2 0 0 0 2 1.6h8.6a2 2 0 0 0 2-1.6L22 8H6" />
        <circle cx="9.5" cy="20" r="1.4" />
        <circle cx="17.5" cy="20" r="1.4" />
      </>
    ),
  },
  {
    to: '/account',
    label: 'Account',
    icon: (
      <>
        <circle cx="12" cy="8" r="3.5" />
        <path d="M5.5 20c0-3.6 2.9-6 6.5-6s6.5 2.4 6.5 6" />
      </>
    ),
  },
]

function Navbar() {
  return (
    <header className="navbar">
      <Link to="/" className="logo">
        <img src="/images/logo.png" alt="Dot & Key" />
      </Link>
      <nav className="nav-links">
        {navItems.map((item) => (
          <Link
            key={item.to}
            to={item.to}
            className="nav-link"
            aria-label={item.label}
          >
            <svg
              className="nav-icon"
              viewBox="0 0 24 24"
              fill="none"
              stroke="currentColor"
              strokeWidth="1.8"
              strokeLinecap="round"
              strokeLinejoin="round"
            >
              {item.icon}
            </svg>
            <span>{item.label}</span>
          </Link>
        ))}
      </nav>
    </header>
  )
}

export default Navbar