import { useState, useEffect } from 'react'
import axios from 'axios'

interface AuthState {
  isAuthenticated: boolean
  isLoading: boolean
  error: string | null
}

// JWT token management
let jwtToken: string | null = null
let tokenExpiry: number | null = null

// Get JWT token from API key
const getJWTToken = async (): Promise<string> => {
  // Check if we have a valid token
  if (jwtToken && tokenExpiry && Date.now() < tokenExpiry) {
    return jwtToken
  }

  const apiKey = import.meta.env.VITE_API_KEY
  if (!apiKey) {
    throw new Error('VITE_API_KEY environment variable is required')
  }

  const api = axios.create({
    baseURL: import.meta.env.VITE_API_URL || 'http://localhost:8000',
    headers: {
      'Content-Type': 'application/json',
    },
  })

  try {
    const response = await api.post<{ access_token: string }>('/api/token', { api_key: apiKey })
    const newToken = response.data.access_token
    
    if (!newToken || typeof newToken !== 'string') {
      throw new Error('Invalid token received from server')
    }
    
    jwtToken = newToken
    
    // Set token expiry (60 minutes from now)
    tokenExpiry = Date.now() + (60 * 60 * 1000)
    
    return jwtToken
  } catch (error) {
    console.error('Failed to get JWT token:', error)
    throw new Error('Authentication failed')
  }
}

// Hook for authentication state
export const useAuth = () => {
  const [authState, setAuthState] = useState<AuthState>({
    isAuthenticated: false,
    isLoading: true,
    error: null,
  })

  useEffect(() => {
    const initializeAuth = async () => {
      try {
        await getJWTToken()
        setAuthState({
          isAuthenticated: true,
          isLoading: false,
          error: null,
        })
      } catch (error) {
        setAuthState({
          isAuthenticated: false,
          isLoading: false,
          error: error instanceof Error ? error.message : 'Authentication failed',
        })
      }
    }

    initializeAuth()
  }, [])

  const refreshToken = async () => {
    setAuthState(prev => ({ ...prev, isLoading: true, error: null }))
    try {
      await getJWTToken()
      setAuthState({
        isAuthenticated: true,
        isLoading: false,
        error: null,
      })
    } catch (error) {
      setAuthState({
        isAuthenticated: false,
        isLoading: false,
        error: error instanceof Error ? error.message : 'Token refresh failed',
      })
    }
  }

  return {
    ...authState,
    refreshToken,
    getToken: () => jwtToken,
  }
} 