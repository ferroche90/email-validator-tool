import { renderHook, waitFor } from '@testing-library/react'
import { describe, it, expect, vi, beforeEach } from 'vitest'
import { QueryClient, QueryClientProvider } from '@tanstack/react-query'
import { useValidateEmails } from '../lib/useValidateEmails'

// Mock axios
vi.mock('axios', () => ({
  default: {
    create: vi.fn(() => ({
      post: vi.fn(),
      interceptors: {
        request: {
          use: vi.fn(),
        },
      },
    })),
  },
}))

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

    const { default: axios } = await import('axios')
    const mockAxios = axios.create()
    vi.mocked(mockAxios.post).mockResolvedValue(mockResponse)

    const { result } = renderHook(() => useValidateEmails(), {
      wrapper: createWrapper(),
    })

    const mutation = result.current

    // Test mutation
    mutation.mutate({
      emails: ['test@example.com', 'invalid@email'],
      enable_smtp: false,
      enable_catch_all: false,
    })

    await waitFor(() => {
      expect(mutation.isPending).toBe(false)
    })

    expect(mutation.data).toEqual(mockResponse.data)
    expect(mutation.error).toBeNull()
  })

  it('should handle loading state', async () => {
    const { default: axios } = await import('axios')
    const mockAxios = axios.create()
    
    // Create a promise that doesn't resolve immediately
    let resolvePromise: (value: { data: { results: Array<{ email: string; status: string }> } }) => void
    const pendingPromise = new Promise((resolve) => {
      resolvePromise = resolve
    })
    
    vi.mocked(mockAxios.post).mockReturnValue(pendingPromise)

    const { result } = renderHook(() => useValidateEmails(), {
      wrapper: createWrapper(),
    })

    const mutation = result.current

    // Start mutation
    mutation.mutate({
      emails: ['test@example.com'],
      enable_smtp: false,
      enable_catch_all: false,
    })

    // Check loading state
    expect(mutation.isPending).toBe(true)

    // Resolve the promise
    resolvePromise!({
      data: {
        results: [{ email: 'test@example.com', status: 'valid' }],
      },
    })

    await waitFor(() => {
      expect(mutation.isPending).toBe(false)
    })
  })

  it('should handle error state', async () => {
    const { default: axios } = await import('axios')
    const mockAxios = axios.create()
    
    const mockError = new Error('Network error')
    vi.mocked(mockAxios.post).mockRejectedValue(mockError)

    const { result } = renderHook(() => useValidateEmails(), {
      wrapper: createWrapper(),
    })

    const mutation = result.current

    // Test mutation
    mutation.mutate({
      emails: ['test@example.com'],
      enable_smtp: false,
      enable_catch_all: false,
    })

    await waitFor(() => {
      expect(mutation.isPending).toBe(false)
    })

    expect(mutation.error).toBeDefined()
    expect((mutation.error as Error)?.message).toBe('Network error')
  })

  it('should handle API error response', async () => {
    const { default: axios } = await import('axios')
    const mockAxios = axios.create()
    
    const mockError = {
      response: {
        status: 500,
        data: { detail: 'Internal server error' },
      },
    }
    vi.mocked(mockAxios.post).mockRejectedValue(mockError)

    const { result } = renderHook(() => useValidateEmails(), {
      wrapper: createWrapper(),
    })

    const mutation = result.current

    // Test mutation
    mutation.mutate({
      emails: ['test@example.com'],
      enable_smtp: false,
      enable_catch_all: false,
    })

    await waitFor(() => {
      expect(mutation.isPending).toBe(false)
    })

    expect(mutation.error).toBeDefined()
  })
}) 