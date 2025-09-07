import { useState, useEffect, useRef } from 'react'
import { useParams, useNavigate } from 'react-router-dom'
import {
  Box,
  IconButton,
  Typography,
  LinearProgress,
  Paper,
  useTheme,
  useMediaQuery,
  CircularProgress,
  Alert,
} from '@mui/material'
import {
  ArrowBack,
  Settings,
  ChevronLeft,
  ChevronRight,
} from '@mui/icons-material'
import { BookPage, ReaderSettings } from '../types/reader'
import { fetchBookPage, getBookTotalPages } from '../data/mockBookPages'
import ReaderSettingsModal from './ReaderSettingsModal'

const STORAGE_KEY = 'flute-reader-settings'

const BookReaderPage = () => {
  const { bookId } = useParams<{ bookId: string }>()
  const navigate = useNavigate()
  const theme = useTheme()
  const isMobile = useMediaQuery(theme.breakpoints.down('md'))
  const scrollContainerRef = useRef<HTMLDivElement>(null)
  
  // State management
  const [currentPage, setCurrentPage] = useState(1)
  const [totalPages, setTotalPages] = useState(0)
  const [pageContent, setPageContent] = useState<BookPage | null>(null)
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState<string | null>(null)
  const [settingsOpen, setSettingsOpen] = useState(false)
  const [settings, setSettings] = useState<ReaderSettings>({
    fontSize: 16,
    lineSpacing: 1.5
  })

  // Load settings from localStorage
  useEffect(() => {
    const savedSettings = localStorage.getItem(STORAGE_KEY)
    if (savedSettings) {
      try {
        setSettings(JSON.parse(savedSettings))
      } catch (e) {
        console.error('Failed to load reader settings:', e)
      }
    }
  }, [])

  // Initialize page data
  useEffect(() => {
    if (bookId) {
      setTotalPages(getBookTotalPages(bookId))
      // Load saved progress or start at page 1
      const savedProgress = localStorage.getItem(`flute-progress-${bookId}`)
      if (savedProgress) {
        try {
          const progress = JSON.parse(savedProgress)
          setCurrentPage(progress.currentPage || 1)
        } catch (e) {
          console.error('Failed to load progress:', e)
        }
      }
    }
  }, [bookId])

  // Load page content when current page changes
  useEffect(() => {
    const loadPage = async () => {
      if (!bookId) return

      setLoading(true)
      setError(null)
      
      try {
        const page = await fetchBookPage(bookId, currentPage)
        setPageContent(page)
        
        // Save progress
        const progress = {
          currentPage,
          lastReadDate: new Date().toISOString()
        }
        localStorage.setItem(`flute-progress-${bookId}`, JSON.stringify(progress))
      } catch (err) {
        setError('Failed to load page content')
        console.error('Error loading page:', err)
      } finally {
        setLoading(false)
      }
    }

    loadPage()
  }, [bookId, currentPage])

  // Handle settings change
  const handleSettingsChange = (newSettings: ReaderSettings) => {
    setSettings(newSettings)
    localStorage.setItem(STORAGE_KEY, JSON.stringify(newSettings))
  }

  // Navigation functions
  const handleBack = () => {
    navigate('/')
  }

  const handlePreviousPage = () => {
    if (currentPage > 1) {
      setCurrentPage(currentPage - 1)
    }
  }

  const handleNextPage = () => {
    if (currentPage < totalPages) {
      setCurrentPage(currentPage + 1)
    }
  }

  // Touch/swipe handlers for mobile
  useEffect(() => {
    if (!isMobile) return

    let startX = 0
    let startY = 0

    const handleTouchStart = (e: TouchEvent) => {
      startX = e.touches[0].clientX
      startY = e.touches[0].clientY
    }

    const handleTouchEnd = (e: TouchEvent) => {
      if (!e.changedTouches[0]) return

      const endX = e.changedTouches[0].clientX
      const endY = e.changedTouches[0].clientY
      const deltaX = endX - startX
      const deltaY = endY - startY

      // Only trigger swipe if horizontal movement is greater than vertical
      if (Math.abs(deltaX) > Math.abs(deltaY) && Math.abs(deltaX) > 50) {
        if (deltaX > 0) {
          // Swipe right - previous page
          handlePreviousPage()
        } else {
          // Swipe left - next page
          handleNextPage()
        }
      }
    }

    const container = scrollContainerRef.current
    if (container) {
      container.addEventListener('touchstart', handleTouchStart)
      container.addEventListener('touchend', handleTouchEnd)
      
      return () => {
        container.removeEventListener('touchstart', handleTouchStart)
        container.removeEventListener('touchend', handleTouchEnd)
      }
    }
  }, [isMobile, currentPage, totalPages])

  const progressPercentage = totalPages > 0 ? (currentPage / totalPages) * 100 : 0

  if (!bookId) {
    return (
      <Box sx={{ p: 3 }}>
        <Alert severity="error">Book ID is required</Alert>
      </Box>
    )
  }

  return (
    <Box sx={{ height: 'calc(100vh - 64px)', display: 'flex', flexDirection: 'column' }}>
      {/* Control Panel */}
      <Paper elevation={1} sx={{ p: 2, display: 'flex', alignItems: 'center', gap: 2 }}>
        {/* Back Button */}
        <IconButton onClick={handleBack} aria-label="back to library">
          <ArrowBack />
        </IconButton>

        {/* Progress Indicator */}
        <Box sx={{ flexGrow: 1, mx: 2 }}>
          <Box sx={{ display: 'flex', justifyContent: 'space-between', mb: 1 }}>
            <Typography variant="body2" color="text.secondary">
              Page {currentPage} of {totalPages}
            </Typography>
            <Typography variant="body2" color="text.secondary">
              {Math.round(progressPercentage)}%
            </Typography>
          </Box>
          <LinearProgress
            variant="determinate"
            value={progressPercentage}
            sx={{ height: 6, borderRadius: 3 }}
          />
        </Box>

        {/* Settings Button */}
        <IconButton onClick={() => setSettingsOpen(true)} aria-label="reading settings">
          <Settings />
        </IconButton>
      </Paper>

      {/* Content Area */}
      <Box
        ref={scrollContainerRef}
        sx={{
          flexGrow: 1,
          overflow: isMobile ? 'hidden' : 'auto',
          position: 'relative',
        }}
      >
        {loading && (
          <Box sx={{ display: 'flex', justifyContent: 'center', alignItems: 'center', height: '100%' }}>
            <CircularProgress />
          </Box>
        )}

        {error && (
          <Box sx={{ p: 3 }}>
            <Alert severity="error">{error}</Alert>
          </Box>
        )}

        {pageContent && !loading && (
          <Box
            sx={{
              p: 3,
              maxWidth: '800px',
              mx: 'auto',
              minHeight: '100%',
              display: 'flex',
              flexDirection: 'column',
              justifyContent: isMobile ? 'flex-start' : 'center',
            }}
          >
            <Typography
              sx={{
                fontSize: `${settings.fontSize}px`,
                lineHeight: settings.lineSpacing,
                whiteSpace: 'pre-line',
                userSelect: 'text',
              }}
            >
              {pageContent.content}
            </Typography>
          </Box>
        )}

        {/* Mobile Navigation Buttons */}
        {isMobile && pageContent && !loading && (
          <>
            {currentPage > 1 && (
              <IconButton
                onClick={handlePreviousPage}
                sx={{
                  position: 'absolute',
                  left: 16,
                  top: '50%',
                  transform: 'translateY(-50%)',
                  backgroundColor: 'background.paper',
                  boxShadow: 2,
                  '&:hover': {
                    backgroundColor: 'background.paper',
                    boxShadow: 4,
                  },
                }}
                aria-label="previous page"
              >
                <ChevronLeft />
              </IconButton>
            )}

            {currentPage < totalPages && (
              <IconButton
                onClick={handleNextPage}
                sx={{
                  position: 'absolute',
                  right: 16,
                  top: '50%',
                  transform: 'translateY(-50%)',
                  backgroundColor: 'background.paper',
                  boxShadow: 2,
                  '&:hover': {
                    backgroundColor: 'background.paper',
                    boxShadow: 4,
                  },
                }}
                aria-label="next page"
              >
                <ChevronRight />
              </IconButton>
            )}
          </>
        )}
      </Box>

      {/* Desktop Navigation */}
      {!isMobile && pageContent && !loading && (
        <Paper elevation={1} sx={{ p: 1, display: 'flex', justifyContent: 'center', gap: 2 }}>
          <IconButton
            onClick={handlePreviousPage}
            disabled={currentPage <= 1}
            aria-label="previous page"
          >
            <ChevronLeft />
          </IconButton>
          <Typography variant="body2" sx={{ display: 'flex', alignItems: 'center', px: 2 }}>
            Page navigation
          </Typography>
          <IconButton
            onClick={handleNextPage}
            disabled={currentPage >= totalPages}
            aria-label="next page"
          >
            <ChevronRight />
          </IconButton>
        </Paper>
      )}

      {/* Settings Modal */}
      <ReaderSettingsModal
        open={settingsOpen}
        onClose={() => setSettingsOpen(false)}
        settings={settings}
        onSettingsChange={handleSettingsChange}
      />
    </Box>
  )
}

export default BookReaderPage