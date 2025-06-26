import React from 'react'
import { screen, fireEvent } from '@testing-library/react'
import { render, mockI18n } from './test-utils'
import LanguageSwitcher from '../components/LanguageSwitcher'
import { describe, it, expect, beforeEach, vi } from 'vitest'
import '@testing-library/jest-dom'

describe('LanguageSwitcher', () => {
  beforeEach(() => {
    vi.clearAllMocks()
  })

  it('renders language buttons with flag icons', () => {
    render(<LanguageSwitcher />)
    
    // Check for flag emojis
    expect(screen.getByText('🇺🇸')).toBeInTheDocument()
    expect(screen.getByText('🇪🇸')).toBeInTheDocument()
    
    // Check for language codes (visible on larger screens)
    expect(screen.getByText('EN')).toBeInTheDocument()
    expect(screen.getByText('ES')).toBeInTheDocument()
  })

  it('shows English as active language by default', () => {
    render(<LanguageSwitcher />)
    
    const englishButton = screen.getByTitle('English')
    const spanishButton = screen.getByTitle('Español')
    
    // English button should have active styling
    expect(englishButton).toHaveClass('bg-blue-100', 'text-blue-700')
    
    // Spanish button should have inactive styling
    expect(spanishButton).toHaveClass('bg-gray-100', 'text-gray-700')
  })

  it('calls changeLanguage when clicking on a language button', () => {
    render(<LanguageSwitcher />)
    
    const spanishButton = screen.getByTitle('Español')
    fireEvent.click(spanishButton)
    
    expect(mockI18n.changeLanguage).toHaveBeenCalledWith('es')
  })

  it('calls changeLanguage with "en" when clicking English button', () => {
    render(<LanguageSwitcher />)
    
    const englishButton = screen.getByTitle('English')
    fireEvent.click(englishButton)
    
    expect(mockI18n.changeLanguage).toHaveBeenCalledWith('en')
  })

  it('has proper accessibility attributes', () => {
    render(<LanguageSwitcher />)
    
    const englishButton = screen.getByTitle('English')
    const spanishButton = screen.getByTitle('Español')
    
    expect(englishButton).toHaveAttribute('title', 'English')
    expect(spanishButton).toHaveAttribute('title', 'Español')
  })

  it('maintains English labels in RTL context', () => {
    // Set document direction to RTL
    document.documentElement.dir = 'rtl'
    
    render(<LanguageSwitcher />)
    
    // Even in RTL, we expect English labels
    expect(screen.getByTitle('English')).toBeInTheDocument()
    expect(screen.getByTitle('Español')).toBeInTheDocument()
    
    // Clean up
    document.documentElement.dir = 'ltr'
  })
}) 