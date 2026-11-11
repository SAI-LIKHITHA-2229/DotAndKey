import { useEffect, useState } from 'react'
import { getProducts } from '../api/products'

// The catalog rarely changes, so fetch it once and share it between pages.
let catalogRequest = null

function loadCatalog() {
  if (!catalogRequest) {
    catalogRequest = getProducts().catch((error) => {
      catalogRequest = null // let the next page try again
      throw error
    })
  }
  return catalogRequest
}

export function useProducts() {
  const [state, setState] = useState({ products: [], loading: true, error: '' })

  useEffect(() => {
    let ignore = false

    loadCatalog()
      .then((products) => {
        if (!ignore) setState({ products, loading: false, error: '' })
      })
      .catch((err) => {
        console.error(err)
        if (!ignore) {
          setState({
            products: [],
            loading: false,
            error: "Couldn't load products. Is the server running?",
          })
        }
      })

    return () => {
      ignore = true
    }
  }, [])

  return state
}
