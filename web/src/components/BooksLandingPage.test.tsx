import { render, screen, waitFor } from '@testing-library/react'
import { ThemeProvider } from '@mui/material/styles'
import CssBaseline from '@mui/material/CssBaseline'
import { describe, it, expect, vi, beforeEach } from 'vitest'
import BooksLandingPage from './BooksLandingPage'
import theme from '../theme'

// Mock the fetchBooks function
vi.mock('../data/mockBooks', () => ({
  fetchBooks: vi.fn(() => Promise.resolve({
    books: [
      {
        id: '1',
        title: 'Test Book',
        author: 'Test Author',
        coverImage: 'test-cover.jpg',
        progress: 25,
        genres: ['Fiction'],
        lastRead: '2024-01-01'
      }
    ],
    hasMore: false,
    totalCount: 1
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
      <ThemeProvider theme={theme}>
        <CssBaseline />
        <BooksLandingPage />
      </ThemeProvider>
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

  it('handles empty state when no books are loaded', async () => {
    // Mock empty response
    const { fetchBooks } = await import('../data/mockBooks')
    vi.mocked(fetchBooks).mockResolvedValueOnce({
      books: [],
      hasMore: false,
      totalCount: 0,
      nextPage: null
    })
    
    renderComponent()
    
    await waitFor(() => {
      expect(screen.getByText('No books found')).toBeInTheDocument()
    })
    
    expect(screen.getByText('Start building your library by uploading your first book!')).toBeInTheDocument()
  })
})
