import React from 'react'
import { screen } from '@testing-library/react'
import { render } from './test-utils'
import { EmailChecker } from '../components/EmailChecker'
import { describe, it, expect } from 'vitest'
import '@testing-library/jest-dom'

describe('i18n Integration', () => {
  it('should render translated text correctly', () => {
    render(<EmailChecker />)
    
    // Check that the main title is translated
    expect(screen.getByText('Email Validator')).toBeInTheDocument()
    
    // Check that the email input label is translated
    expect(screen.getByText('Email Addresses (one per line)')).toBeInTheDocument()
    
    // Check that the validate button is translated
    expect(screen.getByRole('button', { name: 'Validate' })).toBeInTheDocument()
  })

  it('should show authentication status in English', () => {
    render(<EmailChecker />)
    
    // The component should show authentication loading state
    expect(screen.getByText('Authenticating...')).toBeInTheDocument()
  })
}) 