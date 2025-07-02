import React from 'react';
import { render, screen, fireEvent, waitFor } from '../test/test-utils';
import { describe, it, expect, vi, beforeEach } from 'vitest';
import { EmailChecker } from '../components/EmailChecker';

// Mock the useValidateEmails hook
const mockUseValidateEmails = vi.fn();
vi.mock('../lib/useValidateEmails', () => ({
  useValidateEmails: () => mockUseValidateEmails(),
}));

describe('EmailChecker', () => {
  beforeEach(() => {
    vi.clearAllMocks();
  });

  it('should render email input and validation button', () => {
    mockUseValidateEmails.mockReturnValue({
      mutate: vi.fn(),
      isPending: false,
      error: null,
      data: undefined,
    } as any);

    render(<EmailChecker />);

    expect(screen.getByLabelText(/Email Addresses/i)).toBeInTheDocument();
    expect(
      screen.getByRole('button', { name: /Validate/i })
    ).toBeInTheDocument();
  });

  it('should show loading state during validation', () => {
    mockUseValidateEmails.mockReturnValue({
      mutate: vi.fn(),
      isPending: true,
      error: null,
      data: undefined,
    } as any);

    render(<EmailChecker />);

    // Button should be disabled and show validating text
    expect(
      screen.getByRole('button', { name: /Validating.../i })
    ).toBeDisabled();
    // At least one validating text (button or progress label) should be rendered
    expect(screen.getAllByText(/Validating.../i).length).toBeGreaterThan(0);
  });

  it('should display error message when validation fails', () => {
    const mockError = new Error('API Error');
    mockUseValidateEmails.mockReturnValue({
      mutate: vi.fn(),
      isPending: false,
      error: mockError,
      data: undefined,
    } as any);

    render(<EmailChecker />);

    expect(screen.getByText(/Error: API Error/i)).toBeInTheDocument();
  });

  it('should display validation results table with 3 rows for 3 results', async () => {
    const mockData = {
      results: [
        { email: 'test1@example.com', status: 'valid', details: undefined },
        {
          email: 'test2@example.com',
          status: 'invalid_syntax',
          details: 'Invalid format',
        },
        {
          email: 'test3@example.com',
          status: 'disposable',
          details: 'Disposable email',
        },
      ],
    };

    mockUseValidateEmails.mockReturnValue({
      mutate: vi.fn(),
      isPending: false,
      error: null,
      data: mockData,
    } as any);

    render(<EmailChecker />);

    // Check that the results table is displayed
    expect(screen.getByText(/Validation Results/i)).toBeInTheDocument();

    // Check that all 3 emails are displayed in the table
    expect(screen.getByText('test1@example.com')).toBeInTheDocument();
    expect(screen.getByText('test2@example.com')).toBeInTheDocument();
    expect(screen.getByText('test3@example.com')).toBeInTheDocument();

    // Check that status badges are displayed (using translated text)
    expect(screen.getByText('Valid')).toBeInTheDocument();
    expect(screen.getByText('Invalid Syntax')).toBeInTheDocument();
    expect(screen.getByText('Disposable')).toBeInTheDocument();

    // Check that details are displayed
    expect(screen.getByText('Invalid format')).toBeInTheDocument();
    expect(screen.getByText('Disposable email')).toBeInTheDocument();
  });

  it('should call mutate when validation button is clicked', async () => {
    const mockMutate = vi.fn();
    mockUseValidateEmails.mockReturnValue({
      mutate: mockMutate,
      isPending: false,
      error: null,
      data: undefined,
    } as any);

    render(<EmailChecker />);

    const textarea = screen.getByLabelText(/Email Addresses/i);
    const button = screen.getByRole('button', { name: /Validate/i });

    // Enter email addresses
    fireEvent.change(textarea, {
      target: { value: 'test1@example.com\ntest2@example.com' },
    });

    // Click validate button
    fireEvent.click(button);

    expect(mockMutate).toHaveBeenCalledWith({
      emails: ['test1@example.com', 'test2@example.com'],
      enable_smtp: false,
      enable_catch_all: false,
    });
  });

  it('should toggle advanced options when clicked', async () => {
    render(<EmailChecker />);

    const advancedButton = screen.getByText(/Advanced/i);

    const smtpLabel = screen.getByText(/Enable SMTP verification/i);
    const catchAllLabel = screen.getByText(/Enable catch-all detection/i);

    // Advanced options should be hidden initially (not visible)
    expect(smtpLabel).not.toBeVisible();
    expect(catchAllLabel).not.toBeVisible();

    // Click the advanced button to show options
    fireEvent.click(advancedButton);

    await waitFor(() => {
      expect(smtpLabel).toBeVisible();
      expect(catchAllLabel).toBeVisible();
    });

    // Click again to hide options
    fireEvent.click(advancedButton);

    await waitFor(() => {
      expect(smtpLabel).not.toBeVisible();
      expect(catchAllLabel).not.toBeVisible();
    });
  });

  it('should include advanced options in validation request', () => {
    const mockMutate = vi.fn();
    mockUseValidateEmails.mockReturnValue({
      mutate: mockMutate,
      isPending: false,
      error: null,
      data: undefined,
    } as any);

    render(<EmailChecker />);

    const textarea = screen.getByLabelText(/Email Addresses/i);
    const advancedButton = screen.getByText(/Advanced/i);
    const button = screen.getByRole('button', { name: /Validate/i });

    // Enter some emails
    fireEvent.change(textarea, {
      target: { value: 'test@example.com\nanother@test.com' },
    });

    // Enable advanced options
    fireEvent.click(advancedButton);
    const smtpLabel = screen.getByText(/Enable SMTP verification/i);
    const catchAllLabel = screen.getByText(/Enable catch-all detection/i);
    fireEvent.click(smtpLabel);
    fireEvent.click(catchAllLabel);

    // Click validate
    fireEvent.click(button);

    expect(mockMutate).toHaveBeenCalledWith({
      emails: ['test@example.com', 'another@test.com'],
      enable_smtp: true,
      enable_catch_all: true,
    });
  });

  it('should show download CSV button when results are available', () => {
    const mockData = {
      results: [
        { email: 'test@example.com', status: 'valid', details: undefined },
      ],
    };

    mockUseValidateEmails.mockReturnValue({
      mutate: vi.fn(),
      isPending: false,
      error: null,
      data: mockData,
    } as any);

    render(<EmailChecker />);

    expect(
      screen.getByRole('button', { name: /Download CSV/i })
    ).toBeInTheDocument();
  });

  it('should not show download CSV button when no results', () => {
    mockUseValidateEmails.mockReturnValue({
      mutate: vi.fn(),
      isPending: false,
      error: null,
      data: undefined,
    } as any);

    render(<EmailChecker />);

    expect(
      screen.queryByRole('button', { name: /Download CSV/i })
    ).not.toBeInTheDocument();
  });
});
