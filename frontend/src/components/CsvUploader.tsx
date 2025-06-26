import { useState } from 'react'
import { LinearProgress, Box, Typography, Button } from '@mui/material'
import Papa from 'papaparse'
import { validateEmails } from '../lib/useValidateEmails'
import type { ValidationResult, ValidateResponse } from '../types'
import { useTranslation } from 'react-i18next'

// Helper to split array into chunks of given size
const chunkArray = <T,>(array: T[], size: number): T[][] => {
  const chunks: T[][] = []
  for (let i = 0; i < array.length; i += size) {
    chunks.push(array.slice(i, i + size))
  }
  return chunks
}

const CsvUploader = () => {
  const { t } = useTranslation(['common', 'validation'])
  const [progress, setProgress] = useState(0)
  const [isProcessing, setIsProcessing] = useState(false)
  const [results, setResults] = useState<ValidationResult[]>([])
  const [error, setError] = useState<string | null>(null)

  const handleFileChange = async (e: React.ChangeEvent<HTMLInputElement>) => {
    const file = e.target.files?.[0]
    if (!file) return
    if (!file.name.match(/\.(csv|txt)$/i)) {
      setError(t('common:ui.invalidFile'))
      return
    }

    setError(null)
    setIsProcessing(true)
    setProgress(0)
    setResults([])

    // Parse file with PapaParse (no header expected)
    Papa.parse<string[]>(file, {
      worker: true,
      skipEmptyLines: true,
      // eslint-disable-next-line @typescript-eslint/no-explicit-any
      complete: async (resultsParsed: any) => {
        const rows = resultsParsed.data as unknown as string[][]
        // Flatten and trim emails
        const emails: string[] = rows
          .flat()
          .map((item) => (typeof item === 'string' ? item.trim() : ''))
          .filter((email) => email.length > 0)

        if (emails.length === 0) {
          setError(t('common:ui.noEmails'))
          setIsProcessing(false)
          return
        }

        const chunks = chunkArray(emails, 500)
        const totalChunks = chunks.length
        let completed = 0
        const allResults: ValidationResult[] = []

        await Promise.allSettled(
          chunks.map(async (chunk) => {
            try {
              const response: ValidateResponse = await validateEmails({
                emails: chunk,
                enable_smtp: false,
                enable_catch_all: false,
              })
              allResults.push(...response.results)
            } catch (err) {
              console.error(err)
              // Push error results for each email in chunk
              chunk.forEach((email) => {
                allResults.push({ email, status: 'unknown_error', details: 'API error' })
              })
            } finally {
              completed += 1
              setProgress(Math.round((completed / totalChunks) * 100))
            }
          }),
        )

        setResults(allResults)
        setIsProcessing(false)
        setProgress(100)
      },
      // eslint-disable-next-line @typescript-eslint/no-explicit-any
      error: (err: any) => {
        setError(err.message)
        setIsProcessing(false)
      },
    })
  }

  const handleDownloadCSV = () => {
    if (results.length === 0) return
    const csvContent = [
      'Email,Status,Details',
      ...results.map((r) => `"${r.email}","${r.status}","${r.details || ''}"`),
    ].join('\n')
    const blob = new Blob([csvContent], { type: 'text/csv;charset=utf-8;' })
    const url = URL.createObjectURL(blob)
    const link = document.createElement('a')
    link.href = url
    link.download = 'email-validation-results.csv'
    link.click()
    URL.revokeObjectURL(url)
  }

  return (
    <div className="bg-white rounded-lg shadow-md p-6 space-y-4">
      <Typography variant="h6">{t('common:fileUpload.title')}</Typography>
      <input
        type="file"
        accept=".csv,.txt"
        onChange={handleFileChange}
        disabled={isProcessing}
      />

      {isProcessing && (
        <Box sx={{ width: '100%' }}>
          <LinearProgress variant="determinate" value={progress} />
          <Typography variant="body2" sx={{ mt: 1 }}>{`${progress}%`}</Typography>
        </Box>
      )}

      {results.length > 0 && (
        <Button variant="contained" onClick={handleDownloadCSV}>
          {t('common:fileUpload.download')}
        </Button>
      )}

      {error && <Typography color="error">{error}</Typography>}
    </div>
  )
}

export default CsvUploader 