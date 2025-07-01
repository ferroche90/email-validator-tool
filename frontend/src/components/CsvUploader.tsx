import { useState } from 'react'
import { LinearProgress, Box, Typography, Button } from '@mui/material'
import Stack from '@mui/material/Stack'
import Papa from 'papaparse'
import type { ValidationResult } from '../types'
import { useTranslation } from 'react-i18next'

// Helper to split array into chunks of given size
const chunkArray = <T,>(array: T[], size: number): T[][] => {
  const chunks: T[][] = []
  for (let i = 0; i < array.length; i += size) {
    chunks.push(array.slice(i, i + size))
  }
  return chunks
}

interface Props {
  embedded?: boolean;
  onEmailsLoaded?: (emails: string[]) => void;
}

const CsvUploader = ({ embedded = false, onEmailsLoaded }: Props) => {
  const { t } = useTranslation(['common', 'validation'])
  const [isParsing, setIsParsing] = useState(false)
  const [error, setError] = useState<string | null>(null)
  const [loadedEmails, setLoadedEmails] = useState<string[]>([])
  const [isFileLoaded, setIsFileLoaded] = useState(false)

  const handleFileChange = async (e: React.ChangeEvent<HTMLInputElement>) => {
    const file = e.target.files?.[0]
    if (!file) return
    if (!file.name.match(/\.(csv|txt)$/i)) {
      setError(t('common:ui.invalidFile'))
      return
    }

    setError(null)
    setIsParsing(true)
    setLoadedEmails([])
    setIsFileLoaded(false)

    // Parse file with PapaParse (no header expected)
    Papa.parse<string[]>(file, {
      worker: true,
      skipEmptyLines: true,
      // eslint-disable-next-line @typescript-eslint/no-explicit-any
      complete: async (resultsParsed: any) => {
        const rows = resultsParsed.data as unknown as string[][]
        // Flatten and trim emails, skipping header if first row seems to be a header
        const flattened = rows.flat()
          .map((item) => (typeof item === 'string' ? item.trim() : ''))
          .filter((line) => line.length > 0)

        // If first line does not contain '@', treat it as header and remove it
        const startIndex = flattened.length > 0 && !flattened[0].includes('@') ? 1 : 0

        const emails: string[] = flattened.slice(startIndex)

        if (emails.length === 0) {
          setError(t('common:ui.noEmails'))
          setIsParsing(false)
          return
        }

        setLoadedEmails(emails)
        setIsFileLoaded(true)
        setIsParsing(false)
        
        // Notify parent component that emails are loaded
        if (onEmailsLoaded) {
          onEmailsLoaded(emails)
        }
      },
      // eslint-disable-next-line @typescript-eslint/no-explicit-any
      error: (err: any) => {
        setError(err.message)
        setIsParsing(false)
      },
    })
  }

  return (
    <Stack spacing={2} sx={!embedded ? { p: 4, bgcolor: 'background.paper', borderRadius: 1, boxShadow: 1 } : {}}>
      {!embedded && (
        <Typography variant="h6">{t('common:fileUpload.title')}</Typography>
      )}
      <Button variant="outlined" component="label" disabled={isParsing}>
        {t('common:fileUpload.selectFile')}
        <input
          hidden
          type="file"
          accept=".csv,.txt"
          onChange={handleFileChange}
        />
      </Button>

      {isFileLoaded && !isParsing && (
        <Typography variant="body2" color="text.secondary">
          {t('common:fileUpload.fileLoaded').replace('{{count}}', String(loadedEmails.length))}
        </Typography>
      )}

      {isParsing && (
        <Box sx={{ width: '100%' }}>
          <LinearProgress />
        </Box>
      )}

      {error && <Typography color="error">{error}</Typography>}
    </Stack>
  )
}

export default CsvUploader 