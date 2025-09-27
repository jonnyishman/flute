import { render, screen, waitFor } from '@testing-library/react'
import { ThemeProvider } from '@mui/material/styles'
import CssBaseline from '@mui/material/CssBaseline'
import { describe, it, expect, vi, beforeEach } from 'vitest'
import { Provider } from 'jotai'
import BooksLandingPage from './BooksLandingPage'
import theme from '../theme'

// Mock the API client
vi.mock('../api', () => ({
  api: {
    books: {
      getSummaries: vi.fn(),
      getCount: vi.fn(() => Promise.resolve({ count: 1 }))
    }
  }
}))

// Mock the fetchBooks function
vi.mock('../data/booksService', () => ({
  fetchBooks: vi.fn(() => Promise.resolve({
    books: [
      {
        id: 'book-1',
        title: 'Test Book',
        coverArt: 'https://picsum.photos/300/400?random=1',
        wordCount: 100000,
        unknownWords: 500,
        learningWords: 300,
        knownWords: 99200,
        lastReadDate: '2024-01-01T00:00:00.000Z',
        readProgressRatio: 0.25,
        lastReadChapter: 5,
        totalChapters: 20,
      }
    ],
    nextPage: null,
  }))
}))

// Mock BookTile component
vi.mock('./BookTile', () => ({
  default: ({ book }: { book: any }) => (
    <div data-testid="book-tile">{book.title}</div>
  )
}))

describe('BooksLandingPage Smoke Tests', () => {
  const renderComponent = () => {
    return render(
      <Provider>
        <ThemeProvider theme={theme}>
          <CssBaseline />
          <BooksLandingPage />
        </ThemeProvider>
      </Provider>
    )
  }

  beforeEach(() => {
    vi.clearAllMocks()
  })

  it('renders without crashing', async () => {
    renderComponent()
    expect(screen.getByText('Your Library')).toBeInTheDocument()
    
    // Wait for async operations to complete
    await waitFor(() => {
      expect(screen.getByText('Test Book')).toBeInTheDocument()
    })
  })

  it('shows loading state initially', async () => {
    renderComponent()
    
    // Should show loading text initially
    expect(screen.getByText('Loading your books...')).toBeInTheDocument()
    
    // Wait for loading to complete
    await waitFor(() => {
      expect(screen.getByText('1 books in your collection')).toBeInTheDocument()
    })
  })

  it('renders the page header', async () => {
    renderComponent()
    
    expect(screen.getByText('Your Library')).toBeInTheDocument()
    expect(screen.getByText('Loading your books...')).toBeInTheDocument()
    
    // Wait for async operations to complete
    await waitFor(() => {
      expect(screen.getByText('Test Book')).toBeInTheDocument()
    })
  })

  it('loads and displays books after API call', async () => {
    renderComponent()
    
    // Wait for the books to load
    await waitFor(() => {
      expect(screen.getByText('Test Book')).toBeInTheDocument()
    })
    
    // Should show the total count
    await waitFor(() => {
      expect(screen.getByText('1 books in your collection')).toBeInTheDocument()
    })
  })

  it('displays sorting controls', async () => {
    renderComponent()
    
    // Wait for component to load
    await waitFor(() => {
      expect(screen.getByText('Test Book')).toBeInTheDocument()
    })
    
    // Check that sorting controls are present
    expect(screen.getByLabelText('Sort by')).toBeInTheDocument()
  })
})
