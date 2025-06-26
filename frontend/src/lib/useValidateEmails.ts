import { useMutation } from '@tanstack/react-query'
import axios from 'axios'
import type { ValidateRequest, ValidateResponse } from '../types'

// Create axios instance with base configuration
const createApi = () => axios.create({
  baseURL: import.meta.env.VITE_API_URL || 'http://localhost:8000',
  headers: {
    'Content-Type': 'application/json',
  },
})

// Email validation mutation function
const validateEmails = async (request: ValidateRequest): Promise<ValidateResponse> => {
  const apiInstance = createApi()
  
  // Get JWT token from useAuth hook's getToken function
  // We'll get the token from the global auth state instead of duplicating logic
  const apiKey = import.meta.env.VITE_API_KEY
  if (!apiKey) {
    throw new Error('VITE_API_KEY environment variable is required')
  }

  try {
    // Get JWT token first
    const tokenResponse = await apiInstance.post<{ access_token: string }>('/api/token', { api_key: apiKey })
    const jwtToken = tokenResponse.data.access_token
    
    if (!jwtToken || typeof jwtToken !== 'string') {
      throw new Error('Invalid token received from server')
    }

    // Add authorization header for the validation request
    const response = await apiInstance.post<ValidateResponse>('/api/validate', request, {
      headers: {
        'Authorization': `Bearer ${jwtToken}`
      }
    })
    return response.data
  } catch (error) {
    console.error('Email validation error:', error)
    throw error
  }
}

// React Query hook for email validation
export const useValidateEmails = () => {
  return useMutation({
    mutationFn: (request: ValidateRequest) => validateEmails(request),
    onError: (error: Error | unknown) => {
      console.error('Email validation error:', error)
    },
  })
}

export { validateEmails }; 