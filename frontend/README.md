# Dot & Key: Frontend

React 19 + Vite single-page app. Setup, architecture and API docs are in the [main README](../README.md).

```bash
npm install
npm run dev      # http://localhost:5173 (proxies /api to the Flask server)
npm test         # component tests
npm run lint
npm run build
```

Set `VITE_API_URL` in `.env` (see `.env.example`) only if the API isn't reached through `/api`.
