import './App.css'
import { EmailChecker } from './components/EmailChecker'
import { createTheme, ThemeProvider } from '@mui/material/styles'
import CssBaseline from '@mui/material/CssBaseline'
import Container from '@mui/material/Container'
import Box from '@mui/material/Box'
import Header from './components/Header'
import Typography from '@mui/material/Typography'
import { useTranslation } from 'react-i18next'

function App() {
  const theme = createTheme();
  const { t } = useTranslation(['common']);
  return (
    <ThemeProvider theme={theme}>
      <CssBaseline />
      <Header />
      <Container maxWidth="md" sx={{ py: 6 }}>
        {/* Hero / SEO friendly intro */}
        <Box textAlign="center" mb={6}>
          <Typography variant="h3" fontWeight="bold" gutterBottom>
            {t('hero.title')}
          </Typography>
          <Typography variant="subtitle1" color="text.secondary">
            {t('hero.subtitle')}
          </Typography>
        </Box>

        <EmailChecker />
      </Container>
    </ThemeProvider>
  )
}

export default App
