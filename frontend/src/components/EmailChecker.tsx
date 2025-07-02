import { useState } from 'react';
import {
  Cog6ToothIcon,
  DocumentArrowDownIcon,
} from '@heroicons/react/24/outline';
import { useTranslation } from 'react-i18next';
import { useValidateEmails } from '../lib/useValidateEmails';
import { useAuth } from '../lib/useAuth';
import type { ValidationResult, ValidateResponse } from '../types';
import Box from '@mui/material/Box';
import Stack from '@mui/material/Stack';
import Typography from '@mui/material/Typography';
import Button from '@mui/material/Button';
import TextField from '@mui/material/TextField';
import Alert from '@mui/material/Alert';
import CircularProgress from '@mui/material/CircularProgress';
import Collapse from '@mui/material/Collapse';
import FormControlLabel from '@mui/material/FormControlLabel';
import Checkbox from '@mui/material/Checkbox';
import Paper from '@mui/material/Paper';
import TableContainer from '@mui/material/TableContainer';
import Table from '@mui/material/Table';
import TableHead from '@mui/material/TableHead';
import TableRow from '@mui/material/TableRow';
import TableCell from '@mui/material/TableCell';
import TableBody from '@mui/material/TableBody';
import Chip from '@mui/material/Chip';
import LinearProgress from '@mui/material/LinearProgress';
import CsvUploader from './CsvUploader';
import TablePagination from '@mui/material/TablePagination';

export const EmailChecker = () => {
  const { t } = useTranslation(['common', 'validation']);
  const [emails, setEmails] = useState('');
  const [showAdvanced, setShowAdvanced] = useState(false);
  const [enableSmtp, setEnableSmtp] = useState(false);
  const [enableCatchAll, setEnableCatchAll] = useState(false);
  const [csvEmails, setCsvEmails] = useState<string[]>([]);
  const [page, setPage] = useState(0);
  const rowsPerPage = 12;

  const {
    isAuthenticated,
    isLoading: authLoading,
    error: authError,
    refreshToken,
  } = useAuth();
  const { mutate, isPending, error, data } = useValidateEmails();
  const validationData = data as ValidateResponse | undefined;
  const typedError = error as Error | null;

  const handleValidate = () => {
    setPage(0);
    const emailList = [
      ...emails
        .split('\n')
        .map(email => email.trim())
        .filter(email => email.length > 0),
      ...csvEmails,
    ];

    if (emailList.length === 0) return;

    mutate({
      emails: emailList,
      enable_smtp: enableSmtp,
      enable_catch_all: enableCatchAll,
    });
  };

  const handleCsvEmailsLoaded = (emails: string[]) => {
    setCsvEmails(emails);
  };

  const handleDownloadCSV = () => {
    if (!validationData?.results) return;
    const csvContent = [
      'Email,Status,Details',
      ...validationData.results.map(
        (result: ValidationResult) =>
          `"${result.email}","${result.status}","${result.details || ''}"`
      ),
    ].join('\n');

    const blob = new Blob([csvContent], { type: 'text/csv;charset=utf-8;' });
    const link = document.createElement('a');
    const url = URL.createObjectURL(blob);
    link.setAttribute('href', url);
    link.setAttribute('download', 'email-validation-results.csv');
    link.style.visibility = 'hidden';
    document.body.appendChild(link);
    link.click();
    document.body.removeChild(link);
  };

  const handleChangePage = (_: unknown, newPage: number) => {
    setPage(newPage);
  };

  // Show loading state while authenticating
  if (authLoading) {
    return (
      <Stack
        sx={{ minHeight: '60vh' }}
        alignItems="center"
        justifyContent="center"
      >
        <CircularProgress />
        <Typography sx={{ mt: 2 }}>{t('common:app.authenticating')}</Typography>
      </Stack>
    );
  }

  // Show authentication error
  if (authError) {
    return (
      <Stack sx={{ maxWidth: 600, mx: 'auto', p: 4 }} spacing={2}>
        <Alert severity="error" variant="outlined">
          {t('common:app.authError')}: {authError}
        </Alert>
        <Button variant="contained" color="error" onClick={refreshToken}>
          {t('common:app.retryAuth')}
        </Button>
      </Stack>
    );
  }

  return (
    <Stack spacing={4} sx={{ maxWidth: 900, mx: 'auto', p: 3 }}>
      {/* Optionally show auth status; hidden per feedback */}

      <Paper elevation={3} sx={{ p: 4 }}>
        <Typography variant="h5" fontWeight="bold" mb={3}>
          {t('common:app.title')}
        </Typography>

        {/* Email Input */}
        <Stack spacing={2} mb={3}>
          <TextField
            label={t('common:email.inputLabel')}
            placeholder={t('common:email.inputPlaceholder') as string}
            multiline
            minRows={6}
            value={emails}
            onChange={e => setEmails(e.target.value)}
            fullWidth
          />
        </Stack>

        {/* Advanced Options */}
        <Box mb={3}>
          <Button
            size="small"
            startIcon={<Cog6ToothIcon className="w-4 h-4" />}
            onClick={() => setShowAdvanced(!showAdvanced)}
          >
            {t('common:ui.advanced')}
          </Button>
          <Collapse in={showAdvanced}>
            <Stack direction="row" spacing={2} mt={2}>
              <FormControlLabel
                control={
                  <Checkbox
                    checked={enableSmtp}
                    onChange={e => setEnableSmtp(e.target.checked)}
                  />
                }
                label={t('common:options.enableSmtp')}
              />
              <FormControlLabel
                control={
                  <Checkbox
                    checked={enableCatchAll}
                    onChange={e => setEnableCatchAll(e.target.checked)}
                  />
                }
                label={t('common:options.enableCatchAll')}
              />
            </Stack>
          </Collapse>
        </Box>

        {/* Action Buttons */}
        <Stack
          direction="row"
          spacing={2}
          justifyContent="space-between"
          alignItems="center"
        >
          <CsvUploader embedded onEmailsLoaded={handleCsvEmailsLoaded} />
          <Stack direction="row" spacing={2}>
            <Button
              variant="contained"
              onClick={handleValidate}
              disabled={
                isPending ||
                (!emails.trim() && csvEmails.length === 0) ||
                !isAuthenticated
              }
              startIcon={isPending ? <CircularProgress size={18} /> : undefined}
            >
              {isPending ? t('common:ui.validating') : t('common:ui.validate')}
            </Button>
          </Stack>
        </Stack>

        {/* Error Display */}
        {typedError && (
          <Alert sx={{ mt: 2 }} severity="error">
            {t('common:ui.error')}: {typedError.message}
          </Alert>
        )}
      </Paper>

      {/* Progress Bar - Full Width */}
      {isPending && (
        <Box sx={{ width: '100%', mt: 2 }}>
          <LinearProgress />
          <Typography variant="body2" sx={{ mt: 1, textAlign: 'center' }}>
            {t('common:ui.validating')}
          </Typography>
        </Box>
      )}

      {/* Results Table */}
      {validationData?.results && (
        <Paper elevation={3} sx={{ p: 4 }}>
          <Stack
            direction="row"
            justifyContent="space-between"
            alignItems="center"
            mb={2}
          >
            <Typography variant="h6">{t('common:results.title')}</Typography>
            <Button
              variant="outlined"
              startIcon={<DocumentArrowDownIcon className="w-4 h-4" />}
              onClick={handleDownloadCSV}
            >
              {t('common:results.downloadCsv')}
            </Button>
          </Stack>

          <TableContainer>
            <Table size="small">
              <TableHead>
                <TableRow>
                  <TableCell>{t('common:results.table.email')}</TableCell>
                  <TableCell>{t('common:results.table.status')}</TableCell>
                  <TableCell>{t('common:results.table.details')}</TableCell>
                </TableRow>
              </TableHead>
              <TableBody>
                {validationData.results
                  .slice(page * rowsPerPage, page * rowsPerPage + rowsPerPage)
                  .map((result: ValidationResult, index: number) => (
                    <TableRow key={index}>
                      <TableCell>{result.email}</TableCell>
                      <TableCell>
                        <Chip
                          label={t(
                            `validation:status.${result.status}`,
                            result.status
                          )}
                          color={
                            result.status === 'valid'
                              ? 'success'
                              : result.status === 'unknown_error' ||
                                  result.status === 'temporary_error'
                                ? 'warning'
                                : 'error'
                          }
                          variant="outlined"
                        />
                      </TableCell>
                      <TableCell>{result.details ?? '-'}</TableCell>
                    </TableRow>
                  ))}
              </TableBody>
            </Table>
            <TablePagination
              component="div"
              count={validationData.results.length}
              page={page}
              onPageChange={handleChangePage}
              rowsPerPage={rowsPerPage}
              rowsPerPageOptions={[rowsPerPage]}
            />
          </TableContainer>
        </Paper>
      )}
    </Stack>
  );
};
