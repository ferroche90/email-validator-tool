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

// Add request interceptor for Authorization
const addAuthInterceptor = (api: ReturnType<typeof axios.create>) => {
  api.interceptors.request.use((config) => {
    const token = import.meta.env.VITE_API_TOKEN
    if (token && token.trim() !== '') {
      config.headers.Authorization = `Bearer ${token}`
    }
    return config
  })
}

// Email validation mutation function
const validateEmails = async (request: ValidateRequest, api?: ReturnType<typeof axios.create>): Promise<ValidateResponse> => {
  const apiInstance = api || createApi()
  if (!api) {
    addAuthInterceptor(apiInstance)
  }
  const response = await apiInstance.post<ValidateResponse>('/api/validate', request)
  return response.data
}

// React Query hook for email validation
export const useValidateEmails = (api?: ReturnType<typeof axios.create>) => {
  return useMutation({
    mutationFn: (request: ValidateRequest) => validateEmails(request, api),
    onError: (error: Error | unknown) => {
      console.error('Email validation error:', error)
    },
  })
} 