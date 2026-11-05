# Dot & Key: Skincare E-commerce Store

A full-stack e-commerce web app for a skincare brand. You can browse products, pick shades and variants, manage a cart, save delivery addresses, and check out with discounts, free gifts and several payment methods.

The React single-page frontend talks to a Flask REST API secured with JWT. All pricing rules (discounts, shipping, gifts, prepaid offers) are enforced **on the server**, so the browser cannot change what an order costs.

![CI](https://github.com/SAI-LIKHITHA-2229/DotAndKey/actions/workflows/ci.yml/badge.svg)

## Features

- **Accounts:** register and sign in. Passwords are hashed with Werkzeug, sessions use JWTs that expire after 12 hours, and the app logs you out automatically when a token expires.
- **Catalog:** 16 products and 70+ variants, with variant labels or colour swatches. Hovering a variant previews its image and its cart state.
- **Cart:** each user has their own cart, with quantity controls (capped at 10 per item). An item already in the cart shows "Added · Go to cart" instead of being added twice.
- **Checkout:**
  - 20% store-wide discount
  - Free shipping from ₹1000; below that, a ₹70 fee and a "shop for ₹X more" prompt
  - One free gift for every ₹1000
  - An extra 5% off for prepaid methods (card, wallet, netbanking)
- **Address book:** add, edit and delete addresses, validated on both client and server (Indian mobile numbers, PIN codes and states).
- **Orders:** order history with status and delivery details. Orders are placed in a single database transaction.

## Tech stack

| Layer    | Technology |
|----------|------------|
| Frontend | React 19, React Router 7, Vite, plain CSS |
| Backend  | Python, Flask 3, Flask-CORS, PyJWT |
| Database | SQLite (WAL mode) |
| Quality  | pytest (backend), ESLint (frontend), GitHub Actions CI |

## Architecture

```
React SPA (Vite, :5173)                    Flask REST API (:5001)
 ├─ pages/       Home, Shop, Cart,   HTTP   ├─ /register, /login      → JWT
 │               Payment, Account,   JSON   ├─ /products              → catalog (products.json)
 │               Login               ─────► ├─ /cart, /addresses      → JWT required, per user
 ├─ context/     Auth + Cart state          ├─ /checkout/summary      → server-side pricing
 ├─ hooks/       useProducts,               └─ /orders                → transactional checkout
 │               useAddToCart                          │
 └─ api/         fetch client                       SQLite (cart.db)
                 (adds Bearer token)
```

### Security decisions

- **Server-side pricing:** the client sends only `product_id` and `variant`. The server looks up the name, price and image in its catalog, and calculates totals itself.
- **Data isolation:** every cart, address and order query is filtered by the user id taken from the JWT. One user can't read or change another user's data.
- **Account safety:** passwords are stored only as salted hashes. A failed login returns the same message for an unknown user and a wrong password, so attackers can't find out which usernames exist.
- **Input validation:**
  - Every query is parameterized, which prevents SQL injection.
  - Field lengths and formats are checked.
  - Request bodies are limited to 32 KB.
- **Errors and CORS:** errors are returned as JSON and never expose stack traces. CORS is limited to the configured frontend origins.
- **Secret key:** the app refuses to start in production without `SECRET_KEY`.

## Getting started

### Prerequisites

Python 3.10+ and Node.js 20.19+ (or 22.12+).

### 1. Backend

```bash
cd backend
python -m venv .venv
# Windows: .venv\Scripts\activate    macOS/Linux: source .venv/bin/activate
pip install -r requirements.txt
python app.py                # http://127.0.0.1:5001
```

The SQLite database (`backend/cart.db`) and its tables are created automatically.

### 2. Frontend

```bash
cd frontend
cp .env.example .env         # optional; defaults to http://127.0.0.1:5001
npm install
npm run dev                  # http://localhost:5173
```

Open http://localhost:5173 and create an account.

### Configuration

The backend reads environment variables (see [`backend/.env.example`](backend/.env.example)):

| Variable        | Default                                        | Purpose |
|-----------------|------------------------------------------------|---------|
| `APP_ENV`       | `development`                                  | `production` requires `SECRET_KEY` |
| `SECRET_KEY`    | insecure dev key                               | Signs JWTs; use 32+ random bytes |
| `CORS_ORIGINS`  | `http://localhost:5173,http://127.0.0.1:5173`  | Allowed frontend origins |
| `DATABASE_PATH` | `backend/cart.db`                              | SQLite file |
| `PORT`          | `5001`                                         | API port |

## API reference

All request and response bodies are JSON. 🔒 means the endpoint needs an `Authorization: Bearer <token>` header.

| Method | Endpoint                        | Description |
|--------|---------------------------------|-------------|
| GET    | `/health`                       | Health check |
| POST   | `/register`                     | Create an account `{username, password}` |
| POST   | `/login`                        | Returns `{token, username}` |
| GET    | `/products`                     | Product catalog with variants |
| GET    | `/cart` 🔒                      | Current user's cart |
| POST   | `/cart` 🔒                      | Add an item `{product_id, variant}` |
| PUT    | `/cart/<id>/increase` 🔒        | Quantity +1 (max 10) |
| PUT    | `/cart/<id>/decrease` 🔒        | Quantity −1 (removes the item at 0) |
| DELETE | `/cart/<id>` 🔒                 | Remove an item |
| GET    | `/addresses` 🔒                 | Saved addresses |
| POST   | `/addresses` 🔒                 | Add an address (max 10) |
| PUT    | `/addresses/<id>` 🔒            | Update an address |
| DELETE | `/addresses/<id>` 🔒            | Delete an address |
| GET    | `/checkout/summary` 🔒          | Totals, shipping, gifts and payment methods |
| POST   | `/orders` 🔒                    | Place an order `{address_id, payment_method, payment_option, gifts}` |
| GET    | `/orders` 🔒                    | Order history |

## Testing

```bash
cd backend
pip install -r requirements-dev.txt
python -m pytest             # 25 tests: auth, cart, pricing, addresses, orders

cd ../frontend
npm run lint
npm run build
```

GitHub Actions runs all of these on every push and pull request ([`.github/workflows/ci.yml`](.github/workflows/ci.yml)).

## Project structure

```
backend/
  app.py              Flask API (routes, validation, pricing)
  products.json       Product catalog (single source of truth)
  tests/              pytest suite
frontend/
  src/api/            HTTP client and endpoint wrappers
  src/components/     Navbar, ProductCard, ProductModal, VariantPicker, AddressForm
  src/context/        AuthContext, CartContext
  src/hooks/          useProducts, useAddToCart
  src/pages/          Home, Shop, Cart, Payment, Account, Login
```

The original HTML/CSS/JS version of the site is preserved under the Git tag [`legacy-v1`](https://github.com/SAI-LIKHITHA-2229/DotAndKey/tree/legacy-v1/legacy).

## Disclaimer

This is an **unofficial portfolio project** built for learning. It is not affiliated with, endorsed by or selling for Dot & Key. Product names, logos and images belong to their respective owners and are used only to make the demo realistic. No real orders are fulfilled, and the payment step is a demo: any 4-digit PIN is accepted and no money is charged. Prepaid orders are recorded with `payment_status = "demo_paid"`.
