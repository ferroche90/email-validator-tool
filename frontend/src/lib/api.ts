import axios from 'axios'
import { obtainJwtToken } from './useAuth'

// Singleton Axios instance used across the SPA
const api = axios.create({
  baseURL: import.meta.env.VITE_API_URL || 'http://localhost:8000',
  headers: {
    'Content-Type': 'application/json',
  },
})

// Attach Authorization header automatically
api.interceptors.request.use(async (config) => {
  try {
    const token = await obtainJwtToken()
    if (token) {
      config.headers = {
        ...(config.headers as Record<string, string> | undefined),
        Authorization: `Bearer ${token}`,
      } as any
    }
  } catch (err) {
    // If we fail to obtain a token we still let the request continue; backend
    // will reject unauthenticated calls where required.
    console.error('Failed to attach JWT token', err)
  }
  return config
})

export default api 