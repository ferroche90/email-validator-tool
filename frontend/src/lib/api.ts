import axios from 'axios'
import type { AxiosRequestHeaders } from 'axios'
import { obtainJwtToken } from './useAuth'

// Get API URL from environment or use default
const getApiUrl = () => {
  // In production, use the environment variable
  if (import.meta.env.VITE_API_URL) {
    return import.meta.env.VITE_API_URL
  }
  
  // In development, use localhost
  if (import.meta.env.DEV) {
    return 'http://localhost:8000'
  }
  
  // Fallback for production without env var
  return window.location.origin.replace('3000', '8000')
}

// Singleton Axios instance used across the SPA
const api = axios.create({
  baseURL: getApiUrl(),
  headers: {
    'Content-Type': 'application/json',
  },
  // Add timeout for production
  timeout: 30000,
})

// Attach Authorization header automatically
api.interceptors.request.use(async (config) => {
  try {
    const token = await obtainJwtToken()
    if (token) {
      config.headers = {
        ...(config.headers as Record<string, string> | undefined),
        Authorization: `Bearer ${token}`,
      } as AxiosRequestHeaders
    }
  } catch (err) {
    // If we fail to obtain a token we still let the request continue; backend
    // will reject unauthenticated calls where required.
    console.error('Failed to attach JWT token', err)
  }
  return config
})

// Add response interceptor for better error handling
api.interceptors.response.use(
  (response) => response,
  (error) => {
    // Log errors in development
    if (import.meta.env.DEV) {
      console.error('API Error:', error.response?.data || error.message)
    }
    return Promise.reject(error)
  }
)

export default api 