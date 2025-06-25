import '@testing-library/jest-dom'
import { vi } from 'vitest'

// Mock fetch globally
global.fetch = vi.fn()

// Mock environment variables for testing
vi.stubEnv('VITE_API_URL', 'http://localhost:8000')
vi.stubEnv('VITE_API_KEY', 'test_api_key') 