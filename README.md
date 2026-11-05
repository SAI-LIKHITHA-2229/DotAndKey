# Dot & Key: Skincare E-commerce Store

A full-stack e-commerce web app for a skincare brand. You can browse products, pick shades and variants, manage a cart, save delivery addresses, and check out with discounts, free gifts and several payment methods.

The React single-page frontend talks to a Flask REST API. Logins are kept in httpOnly cookies, and every pricing rule (discounts, shipping, gifts, prepaid offers) is enforced **on the server**, so the browser can't change what an order costs.

![CI](https://github.com/SAI-LIKHITHA-2229/DotAndKey/actions/workflows/ci.yml/badge.svg)

## Features

- **Accounts:** register and sign in. Passwords are hashed with Werkzeug. Sessions last 12 hours, the app logs you out automatically when one expires, and logging out ends the session on the server.
- **Catalog:** 16 products and 70+ variants, with variant labels or colour swatches. Hovering a variant previews its image and its cart state.
- **Cart:** each user has their own cart, with quantity controls (capped at 10 per item). An item already in the cart shows "Added · Go to cart" instead of being added twice. Prices always come from the current catalog.
- **Checkout:**
  - 20% store-wide discount
  - Free shipping from ₹1000; below that, a ₹70 fee and a "shop for ₹X more" prompt
  - One free gift for every ₹1000
  - An extra 5% off for prepaid methods (card, wallet, netbanking)
- **Address book:** add, edit and delete addresses, validated on both client and server (Indian mobile numbers, PIN codes and states).
- **Orders:** order history with order status and payment status stored on the server. Orders are placed in a single locked database transaction.
- **Accessibility:** product details open in a proper dialog that keeps keyboard focus inside it. Every control can be used with the keyboard and shows a visible focus ring.

## Tech stack

| Layer    | Technology |
|----------|------------|
| Frontend | React 19, React Router 7, Vite, plain CSS |
| Backend  | Python, Flask 3 (app factory and blueprints), PyJWT, Flask-Limiter, Flask-CORS |
| Database | SQLite (WAL mode, foreign keys, versioned migrations) |
| Servers  | Flask dev server (development); Waitress or Gunicorn (production) |
| Quality  | pytest (70 tests), Vitest + Testing Library (17 tests), ESLint, GitHub Actions CI |

## Architecture

```
Browser ── React SPA (Vite, :5173) ──── /api/* (same origin) ───► Vite proxy ───► Flask API (:5001)
                                         httpOnly session cookie                   │
                                                                                   ├─ auth       /register /login /me /logout
 src/pages/      Home, Shop, Cart, Payment, Account, Login                         ├─ catalog    /products  (products.json)
 src/context/    AuthContext (session), CartContext (in-cart state)                ├─ cart       /cart ...  (per user)
 src/hooks/      useProducts, useAddToCart                                         ├─ addresses  /addresses ...
 src/api/        fetch client (cookie + X-Requested-With)                          ├─ orders     /checkout/summary /orders
                                                                                   └─ SQLite     cart.db (migrated on startup)
```

The backend is an application factory (`api.create_app`) with one blueprint per area. Pricing rules live in `api/pricing.py`, input checks in `api/validation.py`, schema migrations in `api/db.py`, and security headers in `api/security.py`.

### Security decisions

- **Server-side pricing:** carts store only `product_id`, `variant` and quantity. Names, prices and images are looked up in the catalog every time the cart, checkout or an order is built, so a tampered or stale price can never be charged.
- **Sessions:**
  - The login token lives in an **httpOnly, SameSite=Lax cookie** (also `Secure` in production). Page JavaScript can't read it, so an XSS attack can't steal it.
  - Every request checks that the user still exists.
  - **Logout revokes the token server-side**, by bumping the user's `token_version`.
- **CSRF protection:** writes authenticated by cookie must send an `X-Requested-With` header. Other websites can't add that header without passing CORS.
- **Brute-force protection:**
  - `/login` is rate-limited to 10 attempts per minute and 50 per hour per IP; `/register` to 10 per hour.
  - A failed login takes the same time and returns the same message whether the username exists or not, so usernames can't be discovered.
- **Data isolation:** every cart, address and order query is filtered by the logged-in user, and foreign keys tie each row to a real user.
- **Input validation:**
  - Every query is parameterized, which prevents SQL injection.
  - Malformed bodies and wrong field types get a clear 400 instead of crashing.
  - Field lengths and formats are checked, and request bodies are limited to 32 KB.
- **Hardening:**
  - Responses carry a locked-down Content-Security-Policy, `nosniff`, `X-Frame-Options: DENY` and `Referrer-Policy`, plus HSTS in production.
  - Per-user responses aren't cached.
  - Errors are JSON and never expose stack traces.
  - Production refuses to start without `SECRET_KEY`.

## Getting started

### Prerequisites

Python 3.10+ and Node.js 20.19+ (or 22.12+).

### 1. Backend

```bash
cd backend
python -m venv .venv
# Windows: .venv\Scripts\activate    macOS/Linux: source .venv/bin/activate
pip install -r requirements.txt
python app.py                # development server on http://127.0.0.1:5001
```

The SQLite database (`backend/cart.db`) is created and migrated to the latest schema automatically on startup.

### 2. Frontend

```bash
cd frontend
npm install
npm run dev                  # http://localhost:5173
```

Open http://localhost:5173 and create an account. In development, Vite forwards `/api` to the Flask server ([`vite.config.js`](frontend/vite.config.js)), so no frontend `.env` is needed. See [`frontend/.env.example`](frontend/.env.example) if the API lives elsewhere.

### Running in production

```bash
cd backend
export APP_ENV=production SECRET_KEY="$(python -c 'import secrets; print(secrets.token_hex(32))')"
python serve.py              # Waitress (Windows or Linux)
# or: gunicorn -w 4 wsgi:app # Linux
```

Serve the built frontend (`npm run build` → `frontend/dist`) and the API from the **same domain** behind an HTTPS reverse proxy, with `/api/` forwarded to the API. Set `TRUST_PROXY=1` so rate limiting sees real client IPs. If you run several server processes, set `RATELIMIT_STORAGE_URI` to a shared store such as Redis.

### Configuration

The backend reads environment variables; [`backend/.env.example`](backend/.env.example) documents every one.

| Variable                | Default                                       | Purpose |
|-------------------------|-----------------------------------------------|---------|
| `APP_ENV`               | `development`                                 | `production` requires `SECRET_KEY`, makes cookies Secure and adds HSTS |
| `SECRET_KEY`            | insecure dev key                              | Signs session tokens; use 32+ random bytes |
| `DATABASE_PATH`         | `backend/cart.db`                             | SQLite file |
| `CORS_ORIGINS`          | `http://localhost:5173,http://127.0.0.1:5173` | Origins allowed to call the API cross-origin |
| `HOST` / `PORT`         | `0.0.0.0` / `5001`                            | Where `serve.py` listens |
| `TRUST_PROXY`           | `0`                                           | Number of reverse proxies in front of the API |
| `SESSION_COOKIE_SECURE` | `true` in production                          | Send the session cookie over HTTPS only |
| `RATELIMIT_ENABLED`     | `true`                                        | Turn login/register rate limits on or off |
| `RATELIMIT_STORAGE_URI` | `memory://`                                   | Where rate-limit counters are kept |

## API reference

All request and response bodies are JSON. 🔒 means the endpoint needs a session: the `dk_session` cookie set by `/login`, or an `Authorization: Bearer <token>` header for API clients. Writes authenticated by cookie also need `X-Requested-With: XMLHttpRequest`.

| Method | Endpoint                 | Description |
|--------|--------------------------|-------------|
| GET    | `/health`                | Health check |
| POST   | `/register`              | Create an account `{username, password}` (rate-limited) |
| POST   | `/login`                 | Sets the session cookie; returns `{username, expires_at}` (rate-limited) |
| GET    | `/me` 🔒                 | The current session `{username, expires_at}` |
| POST   | `/logout`                | Ends the session on the server and clears the cookie |
| GET    | `/products`              | Product catalog with variants |
| GET    | `/cart` 🔒               | The current user's cart, priced from the catalog |
| POST   | `/cart` 🔒               | Add an item `{product_id, variant}` |
| PUT    | `/cart/<id>/increase` 🔒 | Quantity +1 (max 10) |
| PUT    | `/cart/<id>/decrease` 🔒 | Quantity −1 (removes the item at 0) |
| DELETE | `/cart/<id>` 🔒          | Remove an item |
| GET    | `/addresses` 🔒          | Saved addresses |
| POST   | `/addresses` 🔒          | Add an address (max 10) |
| PUT    | `/addresses/<id>` 🔒     | Update an address |
| DELETE | `/addresses/<id>` 🔒     | Delete an address |
| GET    | `/checkout/summary` 🔒   | Totals, shipping, gifts and payment methods |
| POST   | `/orders` 🔒             | Place an order `{address_id, payment_method, payment_option, gifts}` |
| GET    | `/orders` 🔒             | Order history with `status` and `payment_status` |

## Testing

```bash
cd backend
pip install -r requirements-dev.txt
python -m pytest             # 70 tests: auth and sessions, rate limits, validation,
                             # cart pricing, migrations, checkout, orders, security headers
cd ../frontend
npm test                     # 17 component tests (Vitest + Testing Library)
npm run lint
npm run build
```

GitHub Actions runs all of these on every push and pull request ([`.github/workflows/ci.yml`](.github/workflows/ci.yml)).

## Project structure

```
backend/
  api/
    __init__.py       create_app(): config, CORS, rate limiting, blueprints, error handlers
    config.py         settings from environment variables
    db.py             SQLite connection and versioned migrations
    auth.py           register, login, me, logout, login_required
    catalog.py        product catalog and lookups
    pricing.py        discounts, shipping, gifts, payment methods
    cart.py           cart endpoints
    addresses.py      address book and validation
    orders.py         checkout summary and orders
    validation.py     safe JSON body and field helpers
    security.py       security headers and proxy support
    extensions.py     rate limiter
  app.py              development entry point (python app.py)
  serve.py, wsgi.py   production entry points (Waitress / Gunicorn)
  products.json       product catalog (single source of truth)
  tests/              pytest suite
frontend/
  src/api/            HTTP client and endpoint wrappers
  src/components/     Navbar, ProductCard, ProductModal, VariantPicker, AddressForm, RequireAuth
  src/context/        AuthContext, CartContext
  src/hooks/          useProducts, useAddToCart
  src/pages/          Home, Shop, Cart, Payment, Account, Login
  src/**/*.test.jsx   component tests
```

The original HTML/CSS/JS version of the site is preserved under the Git tag [`legacy-v1`](https://github.com/SAI-LIKHITHA-2229/DotAndKey/tree/legacy-v1/legacy).

## Disclaimer

This is an **unofficial portfolio project** built for learning. It is not affiliated with, endorsed by or selling for Dot & Key. Product names, logos and images belong to their respective owners and are used only to make the demo realistic. No real orders are fulfilled, and the payment step is a demo: any 4-digit PIN is accepted and no money is charged. Prepaid orders are recorded with `payment_status = "demo_paid"`.
