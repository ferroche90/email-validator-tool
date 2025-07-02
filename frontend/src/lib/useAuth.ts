import { useState, useEffect } from 'react';
import axios from 'axios';

interface AuthState {
  isAuthenticated: boolean;
  isLoading: boolean;
  error: string | null;
}

// JWT token management
let jwtToken: string | null = null;
let tokenExpiry: number | null = null;

// Get JWT token from API key
const getJWTToken = async (): Promise<string> => {
  // Check if we have a valid token
  if (jwtToken && tokenExpiry && Date.now() < tokenExpiry) {
    return jwtToken;
  }

  // Base Axios instance (same host in production, localhost in dev)
  const api = axios.create({
    baseURL: import.meta.env.VITE_API_URL || 'http://localhost:8000',
    headers: {
      'Content-Type': 'application/json',
    },
    withCredentials: true, // allow cookies if backend ever relies on them
  });

  try {
    let newToken: string | undefined;

    if (import.meta.env.DEV) {
      // ----------------------------
      // Local development: keep the existing API-key flow so that developers
      // can test with unrestricted roles without having to rebuild the
      // backend.
      // ----------------------------

      const apiKey = import.meta.env.VITE_API_KEY;
      if (!apiKey) {
        throw new Error(
          'VITE_API_KEY environment variable is required in development mode'
        );
      }

      const response = await api.post<{ access_token: string }>('/api/token', {
        api_key: apiKey,
      });
      newToken = response.data.access_token;
    } else {
      // ----------------------------
      // Production: obtain an anonymous *public* token (no API key needed)
      // ----------------------------
      const response = await api.post<{ access_token: string }>(
        '/api/public-token'
      );
      newToken = response.data.access_token;
    }

    if (!newToken || typeof newToken !== 'string') {
      throw new Error('Invalid token received from server');
    }

    jwtToken = newToken;

    // Token validity is aligned with backend default (60 min)
    tokenExpiry = Date.now() + 60 * 60 * 1000;

    return jwtToken;
  } catch (error) {
    console.error('Failed to get JWT token:', error);
    throw new Error('Authentication failed');
  }
};

// Expose the token-fetching utility so other modules (e.g. Axios interceptor)
// can request a fresh JWT without duplicating logic.
export const obtainJwtToken = async (): Promise<string> => getJWTToken();

// Hook for authentication state
export const useAuth = () => {
  const [authState, setAuthState] = useState<AuthState>({
    isAuthenticated: false,
    isLoading: true,
    error: null,
  });

  useEffect(() => {
    const initializeAuth = async () => {
      try {
        await getJWTToken();
        setAuthState({
          isAuthenticated: true,
          isLoading: false,
          error: null,
        });
      } catch (error) {
        setAuthState({
          isAuthenticated: false,
          isLoading: false,
          error:
            error instanceof Error ? error.message : 'Authentication failed',
        });
      }
    };

    initializeAuth();
  }, []);

  const refreshToken = async () => {
    setAuthState(prev => ({ ...prev, isLoading: true, error: null }));
    try {
      await getJWTToken();
      setAuthState({
        isAuthenticated: true,
        isLoading: false,
        error: null,
      });
    } catch (error) {
      setAuthState({
        isAuthenticated: false,
        isLoading: false,
        error: error instanceof Error ? error.message : 'Token refresh failed',
      });
    }
  };

  return {
    ...authState,
    refreshToken,
    getToken: () => jwtToken,
  };
};
