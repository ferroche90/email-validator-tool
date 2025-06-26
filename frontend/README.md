# Email Validator Frontend

React + TypeScript + Vite frontend for the Email Validator Tool.

## Features

- **Modern React 19**: Latest React features with hooks
- **TypeScript**: Full type safety
- **Vite**: Fast development and build
- **Tailwind CSS**: Utility-first styling
- **Internationalization**: Support for EN and ES
- **JWT Authentication**: Automatic token management
- **CSV Upload**: Bulk email validation
- **Real-time Validation**: Live email checking

## Quick Start

### Prerequisites

- Node.js 18+
- pnpm (recommended) or npm

### Installation

1. **Install dependencies**:
   ```bash
   pnpm install
   ```

2. **Set up environment**:
   ```bash
   cp ../infra/env/frontend.example.env .env
   # Edit .env with your API configuration
   ```

3. **Start development server**:
   ```bash
   pnpm dev
   ```

4. **Build for production**:
   ```bash
   pnpm build
   ```

## Environment Variables

| Variable | Default | Description |
|----------|---------|-------------|
| `VITE_API_URL` | `http://localhost:8000` | Backend API URL |
| `VITE_API_KEY` | `test_admin_api_key` | API key for authentication |

## Project Structure

```
src/
├── components/     # React components
│   ├── EmailChecker.tsx    # Main email validation interface
│   ├── CsvUploader.tsx     # CSV file upload and processing
│   └── LanguageSwitcher.tsx # Language selection
├── lib/           # Utilities and hooks
│   ├── api.ts     # Axios instance with JWT interceptor
│   ├── useAuth.ts # Authentication hook
│   └── useValidateEmails.ts # Email validation hook
├── types/         # TypeScript definitions
├── i18n/          # Internationalization
│   └── locales/   # Translation files (EN, ES)
└── test/          # Test files
```

## Development

### Available Scripts

```bash
# Start development server
pnpm dev

# Build for production
pnpm build

# Preview production build
pnpm preview

# Run tests
pnpm test

# Run tests in watch mode
pnpm test:watch

# Lint code
pnpm lint

# Type check
pnpm type-check
```

### Testing

Tests use Vitest and React Testing Library:

```bash
# Run all tests
pnpm test

# Run tests with coverage
pnpm test:coverage

# Run specific test file
pnpm test EmailChecker.test.tsx
```

### Code Quality

```bash
# Lint code
pnpm lint

# Fix linting issues
pnpm lint:fix

# Type check
pnpm type-check
```

## Internationalization

The app supports multiple languages:

- **English (EN)**: Default language
- **Spanish (ES)**: Secondary language

Translation files are located in `src/i18n/locales/`.

## Authentication

The frontend automatically handles JWT authentication:

1. Uses `VITE_API_KEY` to get JWT token from `/api/token`
2. Automatically refreshes tokens before expiration
3. Injects JWT token in all API requests
4. Handles authentication errors gracefully

## API Integration

The frontend communicates with the backend via:

- **Email Validation**: `POST /api/validate`
- **Authentication**: `POST /api/token`
- **Health Check**: `GET /health`

All requests include JWT authentication headers automatically.

## Deployment

### Build for Production

```bash
pnpm build
```

This creates a `dist/` directory with optimized static files.

### Serve Static Files

The `dist/` directory can be served by any static file server:

- **Nginx**: Configure to serve `dist/` directory
- **Apache**: Place files in web root
- **CDN**: Upload to CDN for global distribution
- **Docker**: Use nginx:alpine to serve files

### Environment Configuration

For production, update `.env` with:

```env
VITE_API_URL=https://your-api-domain.com
VITE_API_KEY=your-production-api-key
```

## Contributing

1. Follow the existing code style
2. Add tests for new features
3. Update translations for UI changes
4. Ensure TypeScript types are correct
