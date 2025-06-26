import { useMutation } from '@tanstack/react-query'
import api from './api'
import type { ValidateRequest, ValidateResponse } from '../types'

// Email validation mutation function – relies on global axios instance that
// automatically injects JWT tokens via an interceptor.
const validateEmails = async (request: ValidateRequest): Promise<ValidateResponse> => {
  try {
    const response = await api.post<ValidateResponse>('/api/validate', request)
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