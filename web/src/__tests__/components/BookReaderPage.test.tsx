import { render, screen, fireEvent, waitFor, act } from '@testing-library/react'
import { BrowserRouter } from 'react-router-dom'
import { ThemeProvider, createTheme } from '@mui/material'
import BookReaderPage from '../../components/BookReaderPage'
import * as bookApi from '../../data/bookApi'

// Mock the book API
jest.mock('../../data/bookApi')
const mockBookApi = bookApi as jest.Mocked<typeof bookApi>

// Mock useParams
const mockNavigate = jest.fn()
jest.mock('react-router-dom', () => ({
  ...jest.requireActual('react-router-dom'),
  useParams: () => ({ bookId: '1' }),
  useNavigate: () => mockNavigate,
}))

// Mock localStorage
const localStorageMock = (() => {
  let store: Record<string, string> = {}
  return {
    getItem: (key: string) => store[key] || null,
    setItem: (key: string, value: string) => { store[key] = value },
    clear: () => { store = {} },
  }
})()
Object.defineProperty(window, 'localStorage', { value: localStorageMock })

const mockBook = {
  id: 1,
  title: 'Test Book',
  author: 'Test Author',
  description: 'Test Description',
  total_chapters: 2,
  created_at: new Date().toISOString(),
  chapters: [
    {
      id: 1,
      chapter_number: 1,
      title: 'Chapter 1',
      content: 'This is the first chapter content.',
      word_count: 100,
    },
    {
      id: 2,
      chapter_number: 2,
      title: 'Chapter 2',
      content: 'This is the second chapter content.',
      word_count: 150,
    },
  ],
}

const theme = createTheme()

const renderComponent = () => {
  return render(
    <BrowserRouter>
      <ThemeProvider theme={theme}>
        <BookReaderPage />
      </ThemeProvider>
    </BrowserRouter>
  )
}

describe('BookReaderPage', () => {
  beforeEach(() => {
    localStorageMock.clear()
    mockNavigate.mockClear()
    mockBookApi.fetchBookWithChapters.mockResolvedValue(mockBook)
  })

  it('should render loading state initially', async () => {
    renderComponent()
    
    expect(screen.getByRole('progressbar')).toBeInTheDocument()
  })

  it('should load and display book content', async () => {
    renderComponent()
    
    await waitFor(() => {
      expect(screen.getByText('Test Book by Test Author')).toBeInTheDocument()
    })
    
    expect(screen.getByText('Chapter 1')).toBeInTheDocument()
    expect(screen.getByText('This is the first chapter content.')).toBeInTheDocument()
    expect(screen.getByText('Chapter 1 of 2')).toBeInTheDocument()
  })

  it('should navigate between chapters', async () => {
    renderComponent()
    
    await waitFor(() => {
      expect(screen.getByText('Chapter 1')).toBeInTheDocument()
    })
    
    // Find and click next chapter button
    const nextButton = screen.getByLabelText('next chapter')
    fireEvent.click(nextButton)
    
    await waitFor(() => {
      expect(screen.getByText('Chapter 2')).toBeInTheDocument()
      expect(screen.getByText('This is the second chapter content.')).toBeInTheDocument()
      expect(screen.getByText('Chapter 2 of 2')).toBeInTheDocument()
    })
  })

  it('should handle back navigation', async () => {
    renderComponent()
    
    await waitFor(() => {
      expect(screen.getByText('Chapter 1')).toBeInTheDocument()
    })
    
    const backButton = screen.getByLabelText('back to library')
    fireEvent.click(backButton)
    
    expect(mockNavigate).toHaveBeenCalledWith('/')
  })

  it('should open settings modal', async () => {
    renderComponent()
    
    await waitFor(() => {
      expect(screen.getByText('Chapter 1')).toBeInTheDocument()
    })
    
    const settingsButton = screen.getByLabelText('reading settings')
    fireEvent.click(settingsButton)
    
    expect(screen.getByText('Reading Settings')).toBeInTheDocument()
  })

  it('should handle keyboard navigation', async () => {
    renderComponent()
    
    await waitFor(() => {
      expect(screen.getByText('Chapter 1')).toBeInTheDocument()
    })
    
    // Press arrow right to go to next chapter
    fireEvent.keyDown(document.body, { key: 'ArrowRight' })
    
    await waitFor(() => {
      expect(screen.getByText('Chapter 2')).toBeInTheDocument()
    })
    
    // Press arrow left to go back
    fireEvent.keyDown(document.body, { key: 'ArrowLeft' })
    
    await waitFor(() => {
      expect(screen.getByText('Chapter 1')).toBeInTheDocument()
    })
  })

  it('should persist reading progress', async () => {
    renderComponent()
    
    await waitFor(() => {
      expect(screen.getByText('Chapter 1')).toBeInTheDocument()
    })
    
    // Navigate to chapter 2
    const nextButton = screen.getByLabelText('next chapter')
    fireEvent.click(nextButton)
    
    await waitFor(() => {
      expect(screen.getByText('Chapter 2')).toBeInTheDocument()
    })
    
    // Check that progress was saved to localStorage
    const savedProgress = JSON.parse(localStorageMock.getItem('flute-progress-1') || '{}')
    expect(savedProgress.currentChapter).toBe(2)
  })

  it('should handle API errors', async () => {
    mockBookApi.fetchBookWithChapters.mockRejectedValue(new Error('API Error'))
    
    renderComponent()
    
    await waitFor(() => {
      expect(screen.getByText('Failed to load book content')).toBeInTheDocument()
    })
  })

  it('should display progress percentage', async () => {
    renderComponent()
    
    await waitFor(() => {
      expect(screen.getByText('Chapter 1')).toBeInTheDocument()
    })
    
    expect(screen.getByText('50%')).toBeInTheDocument()
    
    // Navigate to chapter 2
    const nextButton = screen.getByLabelText('next chapter')
    fireEvent.click(nextButton)
    
    await waitFor(() => {
      expect(screen.getByText('100%')).toBeInTheDocument()
    })
  })

  it('should disable navigation buttons at boundaries', async () => {
    renderComponent()
    
    await waitFor(() => {
      expect(screen.getByText('Chapter 1')).toBeInTheDocument()
    })
    
    // Should not have previous button on first chapter
    const prevButtons = screen.queryAllByLabelText('previous chapter')
    expect(prevButtons).toHaveLength(0)
    
    // Navigate to last chapter
    const nextButton = screen.getByLabelText('next chapter')
    fireEvent.click(nextButton)
    
    await waitFor(() => {
      expect(screen.getByText('Chapter 2')).toBeInTheDocument()
    })
    
    // Should not have next button on last chapter
    const nextButtons = screen.queryAllByLabelText('next chapter')
    expect(nextButtons).toHaveLength(0)
  })
})