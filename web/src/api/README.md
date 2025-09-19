# API Middleware Module

This module provides a centralized API client for communicating with the backend, with TypeScript typing and automatic error handling.

## Features

- TypeScript interfaces for all API endpoints
- Centralized error handling with automatic error display
- Consistent API for all endpoints
- Request/response typing
- Network error handling

## Usage

### Basic Usage

```typescript
import { api } from '@/api'

// Health check
const health = await api.health.check()

// Create a book
const bookResponse = await api.books.create({
  title: 'My Book',
  language_id: 1,
  chapters: ['Chapter 1', 'Chapter 2'],
})

// Get book summaries
const summaries = await api.books.getSummaries({
  language_id: 1,
  page: 1,
  per_page: 20,
})

// Create a term
const termResponse = await api.terms.create({
  term: 'example',
  language_id: 1,
  status: LearningStatus.LEARNING,
})

// Update a term
await api.terms.update(123, {
  status: LearningStatus.KNOWN,
  translation: 'ejemplo',
})
```

### Error Handling

Errors are automatically displayed to users via MUI Snackbar notifications. The API client will:
- Display backend error messages
- Show network error messages
- Log errors to console for debugging

### Enabling Notistack Integration

To enable the full error handling with MUI overlays:

1. Install notistack (already added to package.json):
```bash
npm install
```

2. Update `web/src/api/client.ts`:
- Uncomment the import: `import { enqueueSnackbar } from 'notistack'`
- Remove the temporary `enqueueSnackbar` function

3. Update `web/src/api/ApiProvider.tsx`:
- Uncomment all the notistack-related imports and code
- Remove the temporary passthrough implementation

4. Wrap your app with the ApiProvider:
```tsx
import { ApiProvider } from '@/api'

function App() {
  return (
    <ApiProvider>
      {/* Your app content */}
    </ApiProvider>
  )
}
```

## API Endpoints

### Health Check
- `api.health.check()` - Check if the API is running

### Books
- `api.books.create(request)` - Create a new book
- `api.books.getSummaries(request)` - Get paginated book summaries

### Terms
- `api.terms.create(request)` - Create a new term
- `api.terms.update(termId, request)` - Update an existing term

## TypeScript Types

All request and response types are defined in `types.ts`:
- `CreateBookRequest` / `CreateBookResponse`
- `BookSummariesRequest` / `BookSummariesResponse`
- `CreateTermRequest` / `TermIdResponse`
- `UpdateTermRequest`
- `LearningStatus` enum
- `SortOption` enum
- `SortOrder` enum

## Testing

Run tests with:
```bash
npm run test:run
```

Tests cover:
- All API endpoints
- Error handling scenarios
- Network errors
- Response parsing
- URL building with query parameters