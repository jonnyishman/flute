import { useState, useEffect, useCallback } from 'react'
import {
  Container,
  Grid2 as Grid,
  Typography,
  Box,
  CircularProgress,
  Alert,
  Skeleton,
} from '@mui/material'
import { useAtom } from 'jotai'
import { Book } from '../types/book'
import { SortOptions } from '../types/sorting'
import { fetchBooks } from '../data/booksService'
import { api } from '../api'
import { bookSortOptionsAtom } from '../store/atoms'
import BookTile from './BookTile'
import BooksSortControls from './BooksSortControls'

// Default language ID - in a real app this would come from user settings
const DEFAULT_LANGUAGE_ID = 1

interface BooksLandingPageProps {
  onBookClick?: (book: Book) => void
}

const BooksLandingPage = ({ onBookClick }: BooksLandingPageProps) => {
  const [books, setBooks] = useState<Book[]>([])
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState<string | null>(null)
  const [hasMore, setHasMore] = useState(true)
  const [currentPage, setCurrentPage] = useState(1)
  const [totalCount, setTotalCount] = useState(0)
  const [sortOptions, setSortOptions] = useAtom(bookSortOptionsAtom)

  // Function to fetch total book count
  const fetchTotalBookCount = useCallback(async () => {
    try {
      const response = await api.books.getCount({ language_id: DEFAULT_LANGUAGE_ID })
      return response.count
    } catch (err) {
      console.error('Error fetching book count:', err)
      return 0
    }
  }, [])

  // Function to load more books
  const loadBooks = useCallback(async (page: number, reset: boolean = false) => {
    if (loading) return

    setLoading(true)
    setError(null)

    try {
      const response = await fetchBooks(page, 12, sortOptions)

      if (reset) {
        setBooks(response.books)
      } else {
        setBooks(prevBooks => [...prevBooks, ...response.books])
      }

      // Use the hasMore from the response (based on whether we got a full page)
      setHasMore(response.hasMore)
      setCurrentPage(page)
    } catch (err) {
      setError('Failed to load books. Please try again.')
      console.error('Error loading books:', err)
    } finally {
      setLoading(false)
    }
  }, [loading, sortOptions])

  // Fetch total book count once on mount
  useEffect(() => {
    fetchTotalBookCount().then(count => {
      setTotalCount(count)
    })
  }, [fetchTotalBookCount])

  // Initial load
  useEffect(() => {
    loadBooks(1, true)
  // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [])

  // Reload books when sort options change
  useEffect(() => {
    loadBooks(1, true)
  // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [sortOptions])

  // Handle sort change
  const handleSortChange = (newSortOptions: SortOptions) => {
    setSortOptions(newSortOptions)
  }

  // Endless scroll implementation with throttling
  useEffect(() => {
    let timeoutId: NodeJS.Timeout

    const handleScroll = () => {
      clearTimeout(timeoutId)
      timeoutId = setTimeout(() => {
        if (
          window.innerHeight + document.documentElement.scrollTop
          >= document.documentElement.offsetHeight - 1000 // Load more when 1000px from bottom
          && hasMore
          && !loading
        ) {
          loadBooks(currentPage + 1)
        }
      }, 100) // Throttle scroll events to fire at most every 100ms
    }

    window.addEventListener('scroll', handleScroll)
    return () => {
      window.removeEventListener('scroll', handleScroll)
      clearTimeout(timeoutId)
    }
  }, [hasMore, loading, currentPage, loadBooks])

  // Skeleton loader for initial load
  const renderSkeletons = () => (
    <Grid container spacing={{ xs: 2, sm: 3 }}>
      {Array.from({ length: 12 }, (_, i) => (
        <Grid size={{ xs: 12, sm: 6, md: 4, lg: 3 }} key={`skeleton-${i}`}>
          <Box>
            <Skeleton variant="rectangular" height={200} sx={{ borderRadius: 1 }} />
            <Skeleton variant="text" height={32} sx={{ mt: 1 }} />
            <Skeleton variant="text" height={24} />
            <Skeleton variant="rectangular" height={6} sx={{ mt: 1, borderRadius: 3 }} />
            <Box display="flex" gap={1} mt={1}>
              <Skeleton variant="rounded" width={60} height={24} />
              <Skeleton variant="rounded" width={70} height={24} />
              <Skeleton variant="rounded" width={65} height={24} />
            </Box>
            <Skeleton variant="text" height={20} sx={{ mt: 1 }} />
          </Box>
        </Grid>
      ))}
    </Grid>
  )

  return (
    <Container maxWidth="xl" sx={{ px: { xs: 2, sm: 3, md: 4 }, py: { xs: 2, sm: 4 } }}>
      {/* Header */}
      <Box mb={4}>
        <Box display="flex" justifyContent="space-between" alignItems="flex-start" mb={2} flexDirection={{ xs: 'column', sm: 'row' }} gap={{ xs: 2, sm: 0 }}>
          <Typography variant="h3" component="h1" fontWeight="bold" sx={{ fontSize: { xs: '1.75rem', sm: '2rem', md: '3rem' } }}>
            Your Library
          </Typography>
          <BooksSortControls sortOptions={sortOptions} onSortChange={handleSortChange} />
        </Box>
        <Typography variant="subtitle1" color="text.secondary">
          {totalCount > 0 ? `${totalCount} books in your collection` : 'Loading your books...'}
        </Typography>
      </Box>

      {/* Error Message */}
      {error && (
        <Alert severity="error" sx={{ mb: 3 }}>
          {error}
        </Alert>
      )}

      {/* Books Grid */}
      {books.length === 0 && loading ? (
        renderSkeletons()
      ) : (
        <Grid container spacing={{ xs: 2, sm: 3 }}>
          {books.map((book) => (
            <Grid size={{ xs: 12, sm: 6, md: 4, lg: 3 }} key={book.id}>
              <BookTile book={book} onClick={onBookClick} />
            </Grid>
          ))}
        </Grid>
      )}

      {/* Loading Indicator for Pagination */}
      {hasMore && books.length > 0 && (
        <Box display="flex" justifyContent="center" mt={4}>
          <CircularProgress />
        </Box>
      )}

      {/* End of Results Message */}
      {!hasMore && books.length > 0 && (
        <Box textAlign="center" mt={4}>
          <Typography variant="body2" color="text.secondary">
            You've reached the end of your library!
          </Typography>
        </Box>
      )}

      {/* Empty State */}
      {books.length === 0 && !loading && !error && (
        <Box textAlign="center" py={8}>
          <Typography variant="h5" color="text.secondary" gutterBottom>
            No books found
          </Typography>
          <Typography variant="body1" color="text.secondary">
            Start building your library by uploading your first book!
          </Typography>
        </Box>
      )}
    </Container>
  )
}

export default BooksLandingPage