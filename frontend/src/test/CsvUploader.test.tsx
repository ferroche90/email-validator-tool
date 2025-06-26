import React from 'react'
import '@testing-library/jest-dom'
import { describe, it, expect, vi, beforeEach } from 'vitest'
import { render, fireEvent, waitFor } from '@testing-library/react'

// Mock external UI library
vi.mock('@mui/material', () => {
  return {
    LinearProgress: (props: any) => <div data-testid="progress" {...props} />,
    Box: (props: any) => <div data-testid="box" {...props} />,
    Typography: (props: any) => <span {...props} />,
    Button: (props: any) => <button {...props} />,
  }
})

// Mock Papa.parse to synchronously parse CSV for the test environment
vi.mock('papaparse', async () => {
  const actual: any = await vi.importActual('papaparse')
  return {
    default: {
      parse: (file: File, options: any) => {
        const text = (file as any).textContent as string
        const rows = text.split(/\r?\n/).filter(Boolean).map((line) => [line])
        options.complete({ data: rows })
      },
    },
  }
})

import CsvUploader from '../components/CsvUploader'
import * as validateModule from '../lib/useValidateEmails'

// Mock validateEmails to resolve with dummy data
vi.spyOn(validateModule, 'validateEmails').mockImplementation(async (req) => {
  return {
    results: req.emails.map((email) => ({ email, status: 'valid', details: null })),
  }
})

describe('CsvUploader', () => {
  beforeEach(() => {
    document.body.innerHTML = ''
  })

  it('parses CSV, calls API in chunks, and shows download button', async () => {
    const { getByText } = render(<CsvUploader />)

    // Create fake file with 3 emails
    const csvContent = 'a@example.com\n b@example.com\n c@example.com\n'
    const file = new File([csvContent], 'emails.csv', { type: 'text/csv' })
    // For our mocked Papa.parse we pass textContent
    ;(file as any).textContent = csvContent

    // Query the file input directly
    const fileInput = document.querySelector('input[type="file"]') as HTMLInputElement
    expect(fileInput).toBeTruthy()

    await fireEvent.change(fileInput, { target: { files: [file] } })

    await waitFor(() => {
      expect(validateModule.validateEmails).toHaveBeenCalled()
    })

    await waitFor(() => {
      expect(getByText(/download/i)).toBeInTheDocument()
    })
  })
}) 