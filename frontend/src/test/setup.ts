import '@testing-library/jest-dom'
import { vi } from 'vitest'
import type { AxiosInstance } from 'axios'

// Extend expect with Jest DOM matchers
import { expect } from 'vitest'
import * as matchers from '@testing-library/jest-dom/matchers'

expect.extend(matchers)

// Mock fetch globally
global.fetch = vi.fn()

// Mock environment variables for testing
vi.stubEnv('VITE_API_URL', 'http://localhost:8000')
vi.stubEnv('VITE_API_KEY', 'test_api_key')

// Mock axios before any imports
vi.mock('axios', () => ({
  default: {
    create: vi.fn(() => ({
      post: vi.fn().mockResolvedValue({
        data: { access_token: 'mock-jwt-token' }
      }),
      interceptors: {
        request: {
          use: vi.fn()
        }
      }
    }))
  }
}))

// Mock the JWT token response
const mockAxios = await import('axios')
const mockAxiosInstance = {
  post: vi.fn().mockResolvedValue({
    data: { access_token: 'mock-jwt-token' }
  }),
  interceptors: {
    request: {
      use: vi.fn()
    }
  }
} as unknown as AxiosInstance

vi.mocked(mockAxios.default.create).mockReturnValue(mockAxiosInstance) 