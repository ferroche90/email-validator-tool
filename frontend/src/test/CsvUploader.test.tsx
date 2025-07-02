import React from 'react';
import '@testing-library/jest-dom';
import { describe, it, expect, vi, beforeEach } from 'vitest';
import { fireEvent, waitFor } from '@testing-library/react';
import { render } from './test-utils';

// Mock external UI library
vi.mock('@mui/material', () => {
  return {
    LinearProgress: (props: any) => <div data-testid="progress" {...props} />,
    Box: (props: any) => <div data-testid="box" {...props} />,
    Typography: (props: any) => <span {...props} />,
    Button: (props: any) => <button {...props} />,
  };
});

// Mock Papa.parse to synchronously parse CSV for the test environment
vi.mock('papaparse', async () => {
  return {
    default: {
      parse: (file: File, options: any) => {
        const text = (file as any).textContent as string;
        const rows = text
          .split(/\r?\n/)
          .filter(Boolean)
          .map(line => [line]);
        options.complete({ data: rows });
      },
    },
  };
});

import CsvUploader from '../components/CsvUploader';

describe('CsvUploader', () => {
  beforeEach(() => {
    document.body.innerHTML = '';
  });

  it('parses CSV and shows loaded count', async () => {
    const mockOnEmailsLoaded = vi.fn();
    const { getByText } = render(
      <CsvUploader onEmailsLoaded={mockOnEmailsLoaded} />
    );

    // Create fake file with 3 emails
    const csvContent = 'a@example.com\n b@example.com\n c@example.com\n';
    const file = new File([csvContent], 'emails.csv', { type: 'text/csv' });
    // For our mocked Papa.parse we pass textContent
    (file as any).textContent = csvContent;

    // Query the file input directly
    const fileInput = document.querySelector(
      'input[type="file"]'
    ) as HTMLInputElement;
    expect(fileInput).toBeTruthy();

    await fireEvent.change(fileInput, { target: { files: [file] } });

    // Wait for the parsing to complete
    await waitFor(() => {
      expect(getByText('3 emails loaded from file')).toBeInTheDocument();
    });

    // Check that the callback was called with the parsed emails
    expect(mockOnEmailsLoaded).toHaveBeenCalledWith([
      'a@example.com',
      'b@example.com',
      'c@example.com',
    ]);
  });
});
