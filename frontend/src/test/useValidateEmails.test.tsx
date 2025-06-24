import { renderHook, waitFor, act } from '@testing-library/react'
import { describe, it, expect, vi, beforeEach } from 'vitest'
import { QueryClient, QueryClientProvider } from '@tanstack/react-query'
import { useValidateEmails } from '../lib/useValidateEmails'

const createWrapper = () => {
  const queryClient = new QueryClient({
    defaultOptions: {
      queries: { retry: false },
      mutations: { retry: false },
    },
  })
  
  return ({ children }: { children: React.ReactNode }) => (
    <QueryClientProvider client={queryClient}>{children}</QueryClientProvider>
  )
}

describe('useValidateEmails', () => {
  beforeEach(() => {
    vi.clearAllMocks()
  })

  it('should handle successful validation', async () => {
    const mockResponse = {
      data: {
        results: [
          { email: 'test@example.com', status: 'valid', details: null },
          { email: 'invalid@email', status: 'invalid_syntax', details: 'Invalid format' },
        ],
      },
    }

    const mockApi = {
      post: vi.fn().mockResolvedValue(mockResponse),
      interceptors: {
        request: {
          use: vi.fn(),
        },
      },
    } as any

    const { result } = renderHook(() => useValidateEmails(mockApi), {
      wrapper: createWrapper(),
    })

    // Test mutation
    act(() => {
      result.current.mutate({
        emails: ['test@example.com', 'invalid@email'],
        enable_smtp: false,
        enable_catch_all: false,
      })
    })

    await waitFor(() => {
      expect(result.current.isPending).toBe(false)
    })

    await waitFor(() => {
      expect(result.current.data).toEqual(mockResponse.data)
    })
    expect(result.current.error).toBeNull()
  })

  it('should handle loading state', async () => {
    // Create a promise that doesn't resolve immediately
    let resolvePromise: (value: { data: { results: Array<{ email: string; status: string }> } }) => void
    const pendingPromise = new Promise((resolve) => {
      resolvePromise = resolve
    })
    
    const mockApi = {
      post: vi.fn().mockReturnValue(pendingPromise),
      interceptors: {
        request: {
          use: vi.fn(),
        },
      },
    } as any

    const { result } = renderHook(() => useValidateEmails(mockApi), {
      wrapper: createWrapper(),
    })

    // Start mutation
    act(() => {
      result.current.mutate({
        emails: ['test@example.com'],
        enable_smtp: false,
        enable_catch_all: false,
      })
    })

    // Wait for the loading state to be reflected
    await waitFor(() => {
      expect(result.current.isPending).toBe(true)
    })

    // Resolve the promise
    act(() => {
      resolvePromise!({
        data: {
          results: [{ email: 'test@example.com', status: 'valid' }],
        },
      })
    })

    await waitFor(() => {
      expect(result.current.isPending).toBe(false)
    })
  })

  it('should handle error state', async () => {
    const mockError = new Error('Network error')
    const mockApi = {
      post: vi.fn().mockRejectedValue(mockError),
      interceptors: {
        request: {
          use: vi.fn(),
        },
      },
    } as any

    const { result } = renderHook(() => useValidateEmails(mockApi), {
      wrapper: createWrapper(),
    })

    // Test mutation
    act(() => {
      result.current.mutate({
        emails: ['test@example.com'],
        enable_smtp: false,
        enable_catch_all: false,
      })
    })

    await waitFor(() => {
      expect(result.current.isPending).toBe(false)
    })

    await waitFor(() => {
      expect(result.current.error).toBeDefined()
    })
    expect((result.current.error as Error)?.message).toBe('Network error')
  })

  it('should handle API error response', async () => {
    const mockError = {
      response: {
        status: 500,
        data: { detail: 'Internal server error' },
      },
    }
    const mockApi = {
      post: vi.fn().mockRejectedValue(mockError),
      interceptors: {
        request: {
          use: vi.fn(),
        },
      },
    } as any

    const { result } = renderHook(() => useValidateEmails(mockApi), {
      wrapper: createWrapper(),
    })

    // Test mutation
    act(() => {
      result.current.mutate({
        emails: ['test@example.com'],
        enable_smtp: false,
        enable_catch_all: false,
      })
    })

    await waitFor(() => {
      expect(result.current.isPending).toBe(false)
    })

    expect(result.current.error).toBeDefined()
  })
}) 