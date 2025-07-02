import React from 'react';
import { screen, fireEvent } from '@testing-library/react';
import { render } from './test-utils';
import LanguageSwitcher from '../components/LanguageSwitcher';
import { describe, it, expect, beforeEach, vi } from 'vitest';
import '@testing-library/jest-dom';

// Mock i18next
const mockChangeLanguage = vi.fn();
const mockI18n = {
  changeLanguage: mockChangeLanguage,
  language: 'en',
};

vi.mock('react-i18next', async () => {
  const actual = await vi.importActual('react-i18next');
  return {
    ...actual,
    useTranslation: () => ({
      t: (key: string) => key,
      i18n: mockI18n,
    }),
  };
});

// Reset mock before each test
beforeEach(() => {
  mockChangeLanguage.mockClear();
});

describe('LanguageSwitcher', () => {
  beforeEach(() => {
    vi.clearAllMocks();
  });

  it('should render language buttons', () => {
    render(<LanguageSwitcher />);

    expect(screen.getByText('EN')).toBeInTheDocument();
    expect(screen.getByText('ES')).toBeInTheDocument();
  });

  it('should call changeLanguage when clicking on a language button', () => {
    render(<LanguageSwitcher />);

    const spanishButton = screen.getByText('ES');
    fireEvent.click(spanishButton);

    expect(mockChangeLanguage).toHaveBeenCalledWith('es');
  });

  it('should call changeLanguage with "en" when clicking English button', () => {
    // Set initial language to Spanish so clicking EN triggers a change
    mockI18n.language = 'es';

    render(<LanguageSwitcher />);

    const englishButton = screen.getByText('EN');
    fireEvent.click(englishButton);

    expect(mockChangeLanguage).toHaveBeenCalledWith('en');
  });
});
