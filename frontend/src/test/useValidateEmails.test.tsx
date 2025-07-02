import React from 'react';
import { renderHook, waitFor, act } from '@testing-library/react';
import { describe, it, expect, vi, beforeEach } from 'vitest';
import { QueryClient, QueryClientProvider } from '@tanstack/react-query';
import { useValidateEmails } from '../lib/useValidateEmails';
import axios from 'axios';

// Mock axios
vi.mock('axios');
const mockedAxios = vi.mocked(axios);

// Mock the API module with both default and named export, and interceptors
vi.mock('../lib/api', () => ({
  __esModule: true,
  default: {
    post: vi.fn(),
    interceptors: { request: { use: vi.fn() } },
  },
  api: {
    post: vi.fn(),
    interceptors: { request: { use: vi.fn() } },
  },
}));

// Mock the obtainJwtToken function
vi.mock('../lib/useAuth', () => ({
  obtainJwtToken: vi.fn().mockResolvedValue('mock-jwt-token'),
}));

const createWrapper = () => {
  const queryClient = new QueryClient({
    defaultOptions: {
      queries: { retry: false },
      mutations: { retry: false },
    },
  });

  return ({ children }: { children: React.ReactNode }) => (
    <QueryClientProvider client={queryClient}>{children}</QueryClientProvider>
  );
};

describe('useValidateEmails', () => {
  beforeEach(() => {
    vi.clearAllMocks();
    // Mock environment variables
    vi.stubEnv('VITE_API_KEY', 'test_api_key');
    vi.stubEnv('VITE_API_URL', 'http://localhost:8000');
  });

  it('should handle successful validation', async () => {
    const mockValidationResponse = {
      data: {
        results: [
          { email: 'test@example.com', status: 'valid', details: null },
          {
            email: 'invalid@email',
            status: 'invalid_syntax',
            details: 'Invalid format',
          },
        ],
      },
    };

    // Mock axios.create to return a mock instance
    const mockAxiosInstance = {
      post: vi.fn().mockResolvedValueOnce(mockValidationResponse), // Only validation call
    };
    (mockedAxios.create as any).mockReturnValue(mockAxiosInstance);

    const { result } = renderHook(() => useValidateEmails(), {
      wrapper: createWrapper(),
    });

    // Test mutation
    act(() => {
      result.current.mutate({
        emails: ['test@example.com', 'invalid@email'],
        enable_smtp: false,
        enable_catch_all: false,
      });
    });

    await waitFor(() => {
      expect(result.current.isPending).toBe(false);
    });

    await waitFor(() => {
      expect(result.current.data).toEqual(mockValidationResponse.data);
    });
    expect(result.current.error).toBeNull();

    // Verify the API call
    expect(mockAxiosInstance.post).toHaveBeenCalledTimes(1);
    expect(mockAxiosInstance.post).toHaveBeenCalledWith(
      '/api/validate',
      {
        emails: ['test@example.com', 'invalid@email'],
        enable_smtp: false,
        enable_catch_all: false,
      },
      {
        headers: {
          Authorization: 'Bearer mock-jwt-token',
        },
      }
    );
  });

  it('should handle loading state', async () => {
    // Create promises that don't resolve immediately
    let resolveTokenPromise: (value: {
      data: { access_token: string };
    }) => void;
    let resolveValidationPromise: (value: {
      data: { results: Array<{ email: string; status: string }> };
    }) => void;

    const pendingTokenPromise = new Promise(resolve => {
      resolveTokenPromise = resolve;
    });

    const pendingValidationPromise = new Promise(resolve => {
      resolveValidationPromise = resolve;
    });

    const mockAxiosInstance = {
      post: vi
        .fn()
        .mockReturnValueOnce(pendingTokenPromise)
        .mockReturnValueOnce(pendingValidationPromise),
    };
    (mockedAxios.create as any).mockReturnValue(mockAxiosInstance);

    const { result } = renderHook(() => useValidateEmails(), {
      wrapper: createWrapper(),
    });

    // Start mutation
    act(() => {
      result.current.mutate({
        emails: ['test@example.com'],
        enable_smtp: false,
        enable_catch_all: false,
      });
    });

    // Wait for the loading state to be reflected
    await waitFor(() => {
      expect(result.current.isPending).toBe(true);
    });

    // Resolve the promises
    act(() => {
      resolveTokenPromise!({ data: { access_token: 'mock-jwt-token' } });
      resolveValidationPromise!({
        data: {
          results: [{ email: 'test@example.com', status: 'valid' }],
        },
      });
    });

    await waitFor(() => {
      expect(result.current.isPending).toBe(false);
    });
  });

  it('should handle error state', async () => {
    const mockError = new Error('Network error');

    const mockAxiosInstance = {
      post: vi.fn().mockRejectedValue(mockError),
    };
    (mockedAxios.create as any).mockReturnValue(mockAxiosInstance);

    const { result } = renderHook(() => useValidateEmails(), {
      wrapper: createWrapper(),
    });

    // Test mutation
    act(() => {
      result.current.mutate({
        emails: ['test@example.com'],
        enable_smtp: false,
        enable_catch_all: false,
      });
    });

    await waitFor(() => {
      expect(result.current.isPending).toBe(false);
    });

    await waitFor(() => {
      expect(result.current.error).toBeDefined();
    });
    expect((result.current.error as Error)?.message).toBe('Network error');
  });

  it('should handle API error response', async () => {
    const mockError = {
      response: {
        status: 500,
        data: { detail: 'Internal server error' },
      },
    };

    const mockAxiosInstance = {
      post: vi.fn().mockRejectedValue(mockError),
    };
    (mockedAxios.create as any).mockReturnValue(mockAxiosInstance);

    const { result } = renderHook(() => useValidateEmails(), {
      wrapper: createWrapper(),
    });

    // Test mutation
    act(() => {
      result.current.mutate({
        emails: ['test@example.com'],
        enable_smtp: false,
        enable_catch_all: false,
      });
    });

    await waitFor(() => {
      expect(result.current.isPending).toBe(false);
    });

    expect(result.current.error).toBeDefined();
  });

  it('should handle missing API key', async () => {
    // Reconfigure the existing obtainJwtToken mock to throw the expected error
    const { obtainJwtToken } = await import('../lib/useAuth');
    vi.mocked(obtainJwtToken).mockRejectedValue(
      new Error(
        'VITE_API_KEY environment variable is required in development mode'
      )
    );

    // Ensure axios.create returns a dummy object – it will not be used
    const mockAxiosInstance = { post: vi.fn() };
    (mockedAxios.create as any).mockReturnValue(mockAxiosInstance);

    const { result } = renderHook(() => useValidateEmails(), {
      wrapper: createWrapper(),
    });

    // Test mutation
    act(() => {
      result.current.mutate({
        emails: ['test@example.com'],
        enable_smtp: false,
        enable_catch_all: false,
      });
    });

    await waitFor(() => {
      expect(result.current.isPending).toBe(false);
    });

    const errorMessage = (result.current.error as Error | undefined)?.message;
    expect(errorMessage).toBeDefined();
    expect(errorMessage).toContain(
      'VITE_API_KEY environment variable is required in development mode'
    );
  });

  it('should return the correct structure', () => {
    const { result } = renderHook(() => useValidateEmails(), {
      wrapper: createWrapper(),
    });

    expect(result.current).toHaveProperty('mutate');
    expect(result.current).toHaveProperty('isPending');
    expect(result.current).toHaveProperty('error');
    expect(result.current).toHaveProperty('data');
  });
});
