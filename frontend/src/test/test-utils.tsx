import React from 'react'
import { render, RenderOptions } from '@testing-library/react'
import { I18nextProvider } from 'react-i18next'
import i18n from '../i18n'
import { QueryClient, QueryClientProvider } from '@tanstack/react-query'
import type { ReactElement } from 'react'
import { vi } from 'vitest'

// Create a test query client
const createTestQueryClient = () =>
  new QueryClient({
    defaultOptions: {
      queries: {
        retry: false,
      },
      mutations: {
        retry: false,
      },
    },
  })

// Create a mock i18n instance for testing
const mockI18n = {
  ...i18n,
  changeLanguage: vi.fn(),
  language: 'en',
  on: vi.fn(),
  off: vi.fn(),
  t: (key: string, defaultValue?: string) => {
    // Simple translation function that returns the key or default value
    if (key.includes('common:app.authenticating')) return 'Authenticating...'
    if (key.includes('common:app.authError')) return 'Authentication Error'
    if (key.includes('common:app.retryAuth')) return 'Retry Authentication'
    if (key.includes('common:app.authenticated')) return 'Authenticated with JWT'
    if (key.includes('common:app.title')) return 'Email Validator'
    if (key.includes('common:email.inputLabel')) return 'Email Addresses (one per line)'
    if (key.includes('common:email.inputPlaceholder')) return 'Enter email addresses here...\nexample@domain.com\ntest@example.org'
    if (key.includes('common:ui.advanced')) return 'Advanced'
    if (key.includes('common:ui.download')) return 'Download'
    if (key.includes('common:ui.error')) return 'Error'
    if (key.includes('common:ui.loading')) return 'Loading...'
    if (key.includes('common:ui.validate')) return 'Validate'
    if (key.includes('common:ui.validating')) return 'Validating...'
    if (key.includes('common:options.enableSmtp')) return 'Enable SMTP verification'
    if (key.includes('common:options.enableCatchAll')) return 'Enable catch-all detection'
    if (key.includes('common:results.title')) return 'Validation Results'
    if (key.includes('common:results.downloadCsv')) return 'Download CSV'
    if (key.includes('common:results.table.email')) return 'Email'
    if (key.includes('common:results.table.status')) return 'Status'
    if (key.includes('common:results.table.details')) return 'Details'
    if (key.includes('validation:status.valid')) return 'Valid'
    if (key.includes('validation:status.invalid_syntax')) return 'Invalid Syntax'
    if (key.includes('validation:status.invalid_domain')) return 'Invalid Domain'
    if (key.includes('validation:status.invalid_mx')) return 'Invalid MX'
    if (key.includes('validation:status.invalid_smtp')) return 'Invalid SMTP'
    if (key.includes('validation:status.disposable')) return 'Disposable'
    if (key.includes('validation:status.role_account')) return 'Role Account'
    if (key.includes('validation:status.spamtrap')) return 'Spam Trap'
    if (key.includes('validation:status.abuse')) return 'Abuse'
    if (key.includes('validation:status.suppressed')) return 'Suppressed'
    if (key.includes('validation:status.on_bounce_list')) return 'On Bounce List'
    if (key.includes('validation:status.catch_all')) return 'Catch All'
    if (key.includes('validation:status.unknown_error')) return 'Unknown Error'
    return defaultValue || key
  },
}

interface CustomRenderOptions extends Omit<RenderOptions, 'wrapper'> {
  queryClient?: QueryClient
  wrapper?: React.ComponentType<{ children: React.ReactNode }>
}

const AllTheProviders = ({ children }: { children: React.ReactNode }) => {
  return (
    <I18nextProvider i18n={mockI18n as any}>
      <QueryClientProvider client={createTestQueryClient()}>
        {children}
      </QueryClientProvider>
    </I18nextProvider>
  )
}

const customRender = (
  ui: React.ReactElement,
  options?: CustomRenderOptions
) => {
  const { queryClient = createTestQueryClient(), ...renderOptions } = options || {}

  return render(ui, { wrapper: AllTheProviders, ...renderOptions })
}

export * from '@testing-library/react'
export { customRender as render }
export { mockI18n } 