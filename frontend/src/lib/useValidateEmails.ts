import { useMutation } from '@tanstack/react-query';
import axios from 'axios';
import type { ValidateRequest, ValidateResponse } from '../types';
import { obtainJwtToken } from './useAuth';

// Create axios instance with base configuration
const createApi = () =>
  axios.create({
    baseURL: import.meta.env.VITE_API_URL || 'http://localhost:8000',
    headers: {
      'Content-Type': 'application/json',
    },
  });

// Email validation mutation function
const validateEmails = async (
  request: ValidateRequest
): Promise<ValidateResponse> => {
  const apiInstance = createApi();

  try {
    // Obtain (and refresh if needed) the JWT using the shared auth helper
    const jwtToken = await obtainJwtToken();

    // Add authorization header for the validation request
    const response = await apiInstance.post<ValidateResponse>(
      '/api/validate',
      request,
      {
        headers: {
          Authorization: `Bearer ${jwtToken}`,
        },
      }
    );
    return response.data;
  } catch (error) {
    console.error('Email validation error:', error);
    throw error;
  }
};

// React Query hook for email validation
export const useValidateEmails = () => {
  return useMutation({
    mutationFn: (request: ValidateRequest) => validateEmails(request),
    onError: (error: Error | unknown) => {
      console.error('Email validation error:', error);
    },
  });
};

export { validateEmails };
