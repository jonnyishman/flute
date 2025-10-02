import { describe, it, expect, vi, beforeEach } from 'vitest'
import { render, screen, waitFor } from '@testing-library/react'
import { MemoryRouter, Route, Routes } from 'react-router-dom'
import BookReader from './BookReader'
import { api } from '../api'

vi.mock('../api', () => ({
  api: {
    books: {
      getChapterWithHighlights: vi.fn(),
      getChapterCount: vi.fn(),
    },
  },
}))

vi.mock('../data/mockBooks', () => ({
  fetchBooks: vi.fn(),
}))

vi.mock('../hooks/useBookProgress', () => ({
  default: () => ({
    updateBookProgress: vi.fn(),
    startReadingSession: vi.fn(),
    endReadingSession: vi.fn(),
  }),
}))

describe('BookReader', () => {
  beforeEach(() => {
    vi.clearAllMocks()
  })

  it('renders loading state initially', () => {
    render(
      <MemoryRouter initialEntries={['/book/1/chapter/1']}>
        <Routes>
          <Route path="/book/:bookId/chapter/:chapterId" element={<BookReader />} />
        </Routes>
      </MemoryRouter>
    )

    expect(screen.getByText('Loading book...')).toBeInTheDocument()
  })

  it('loads and displays chapter content from API', async () => {
    const mockBook = {
      id: '1',
      title: 'Test Book',
      coverArt: '/test.jpg',
      wordCount: 1000,
      unknownWords: 100,
      learningWords: 50,
      knownWords: 850,
      lastReadDate: '2025-01-01',
      readProgressRatio: 0.5,
      totalChapters: 10,
      lastReadChapter: 1,
    }

    const mockChapterResponse = {
      chapter: {
        id: 1,
        chapter_number: 1,
        content: 'This is the test chapter content.',
        word_count: 6,
      },
      term_highlights: [],
    }

    const mockChapterCountResponse = {
      count: 10,
    }

    vi.mocked(api.books.getChapterWithHighlights).mockResolvedValue(mockChapterResponse)
    vi.mocked(api.books.getChapterCount).mockResolvedValue(mockChapterCountResponse)

    render(
      <MemoryRouter>
        <BookReader book={mockBook} chapter={1} />
      </MemoryRouter>
    )

    await waitFor(() => {
      expect(screen.getByText('Test Book')).toBeInTheDocument()
    })

    await waitFor(
      () => {
        expect(screen.getByText('This is the test chapter content.')).toBeInTheDocument()
      },
      { timeout: 3000 }
    )

    expect(api.books.getChapterWithHighlights).toHaveBeenCalledWith(1, 1)
  })

  it('handles API errors gracefully', async () => {
    const mockBook = {
      id: '1',
      title: 'Test Book',
      coverArt: '/test.jpg',
      wordCount: 1000,
      unknownWords: 100,
      learningWords: 50,
      knownWords: 850,
      lastReadDate: '2025-01-01',
      readProgressRatio: 0.5,
      totalChapters: 10,
      lastReadChapter: 1,
    }

    vi.mocked(api.books.getChapterWithHighlights).mockRejectedValue(new Error('API Error'))

    render(
      <MemoryRouter>
        <BookReader book={mockBook} chapter={1} />
      </MemoryRouter>
    )

    await waitFor(
      () => {
        expect(screen.getByText('Failed to load chapter content')).toBeInTheDocument()
      },
      { timeout: 3000 }
    )
  })

  it('loads book from URL parameters', async () => {
    const { fetchBooks } = await import('../data/mockBooks')

    const mockBook = {
      id: '1',
      title: 'URL Loaded Book',
      coverArt: '/url-test.jpg',
      wordCount: 2000,
      unknownWords: 200,
      learningWords: 100,
      knownWords: 1700,
      lastReadDate: '2025-01-01',
      readProgressRatio: 0.3,
      totalChapters: 15,
      lastReadChapter: 5,
    }

    const mockChapterResponse = {
      chapter: {
        id: 1,
        chapter_number: 3,
        content: 'Content loaded from URL parameters.',
        word_count: 5,
      },
      term_highlights: [],
    }

    const mockChapterCountResponse = {
      count: 15,
    }

    vi.mocked(fetchBooks).mockResolvedValue({
      books: [mockBook],
      hasMore: false,
      nextPage: null,
      totalCount: 1,
    })
    vi.mocked(api.books.getChapterWithHighlights).mockResolvedValue(mockChapterResponse)
    vi.mocked(api.books.getChapterCount).mockResolvedValue(mockChapterCountResponse)

    render(
      <MemoryRouter initialEntries={['/book/1/chapter/3']}>
        <Routes>
          <Route path="/book/:bookId/chapter/:chapterId" element={<BookReader />} />
        </Routes>
      </MemoryRouter>
    )

    // Should show loading initially
    expect(screen.getByText('Loading book...')).toBeInTheDocument()

    // Should load book data and chapter count
    await waitFor(() => {
      expect(fetchBooks).toHaveBeenCalled()
      expect(api.books.getChapterCount).toHaveBeenCalledWith(1)
    })

    // Should display book title and chapter content
    await waitFor(() => {
      expect(screen.getByText('URL Loaded Book')).toBeInTheDocument()
    })

    await waitFor(
      () => {
        expect(screen.getByText('Content loaded from URL parameters.')).toBeInTheDocument()
      },
      { timeout: 3000 }
    )

    // Verify API calls were made with correct parameters
    expect(api.books.getChapterWithHighlights).toHaveBeenCalledWith(1, 3)
  })
})
