import react from '@vitejs/plugin-react'
import { defineConfig } from 'vite'

// Forward /api/* to the Flask server so the browser sees the API as the same
// origin as the page. That keeps the httpOnly session cookie first-party and
// avoids CORS in development. In production a reverse proxy does the same.
const apiProxy = {
  '/api': {
    target: 'http://127.0.0.1:5001',
    changeOrigin: true,
    rewrite: (path) => path.replace(/^\/api/, ''),
  },
}

// https://vite.dev/config/
export default defineConfig({
  plugins: [react()],
  server: { proxy: apiProxy },
  preview: { proxy: apiProxy },
  // Vitest: component tests run in a simulated browser (jsdom).
  test: {
    environment: 'jsdom',
    setupFiles: './src/test/setup.js',
  },
})
