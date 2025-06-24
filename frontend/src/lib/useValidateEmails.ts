import { useMutation } from '@tanstack/react-query'
import axios from 'axios'
import type { ValidateRequest, ValidateResponse } from '../types'

// Create axios instance with base configuration
const api = axios.create({
  baseURL: import.meta.env.VITE_API_URL || 'http://localhost:8000',
  headers: {
    'Content-Type': 'application/json',
  },
})

// Add request interceptor for Authorization
api.interceptors.request.use((config) => {
  const token = import.meta.env.VITE_API_TOKEN
  if (token && token.trim() !== '') {
    config.headers.Authorization = `Bearer ${token}`
  }
  return config
})

// Email validation mutation function
const validateEmails = async (request: ValidateRequest): Promise<ValidateResponse> => {
  const response = await api.post<ValidateResponse>('/api/validate', request)
  return response.data
}

// React Query hook for email validation
export const useValidateEmails = () => {
  const mutation = useMutation({
    mutationFn: validateEmails,
    onError: (error: any) => {
      console.error('Email validation error:', error)
    },
  })

  return {
    mutate: mutation.mutate,
    isPending: mutation.isPending,
    error: mutation.error,
    data: mutation.data,
  }
} 