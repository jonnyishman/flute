import { useState, useEffect, useRef, useCallback, useMemo } from 'react'
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
  Fade,
} from '@mui/material'
import {
  ArrowBack,
  Settings,
  ChevronLeft,
  ChevronRight,
  KeyboardArrowUp,
  KeyboardArrowDown,
} from '@mui/icons-material'
import { Book, Chapter, ReaderSettings } from '../types/reader'
import { fetchBookWithChapters } from '../data/bookApi'
import { useReaderSettings, useReadingProgress } from '../hooks/usePersistedState'
import { useDebouncedCallback } from '../hooks/useDebounce'
import ReaderSettingsModal from './ReaderSettingsModal'
import ErrorBoundary from './ErrorBoundary'
import {
  SWIPE_THRESHOLD,
  KEYBOARD_SHORTCUTS,
  MOBILE_BREAKPOINT,
  READER_LAYOUT,
  ANIMATION_DURATION,
  SCROLL_POSITION_SAVE_DEBOUNCE
} from '../constants/reader'

const BookReaderPage = () => {
  const { bookId } = useParams<{ bookId: string }>()
  const navigate = useNavigate()
  const theme = useTheme()
  const isMobile = useMediaQuery(theme.breakpoints.down(MOBILE_BREAKPOINT))
  const scrollContainerRef = useRef<HTMLDivElement>(null)
  
  // State management
  const [book, setBook] = useState<Book | null>(null)
  const [currentChapter, setCurrentChapter] = useState<Chapter | null>(null)
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState<string | null>(null)
  const [settingsOpen, setSettingsOpen] = useState(false)
  
  // Custom hooks
  const [settings, setSettings] = useReaderSettings()
  const [progress, setProgress] = useReadingProgress(bookId || '')

  // Memoized values
  const currentChapterNumber = currentChapter?.chapter_number || progress.currentChapter
  const totalChapters = book?.total_chapters || 0
  const progressPercentage = totalChapters > 0 ? (currentChapterNumber / totalChapters) * 100 : 0

  // Debounced scroll position saving
  const debouncedSaveScrollPosition = useDebouncedCallback((position: number) => {
    setProgress(prev => ({
      ...prev,
      scrollPosition: position,
      lastReadDate: new Date().toISOString()
    }))
  }, SCROLL_POSITION_SAVE_DEBOUNCE)

  // Memoized touch handlers to prevent unnecessary re-renders
  const touchHandlers = useMemo(() => {
    if (!isMobile) return {}

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
      if (Math.abs(deltaX) > Math.abs(deltaY) && Math.abs(deltaX) > SWIPE_THRESHOLD) {
        if (deltaX > 0) {
          handlePreviousChapter()
        } else {
          handleNextChapter()
        }
      }
    }

    return { handleTouchStart, handleTouchEnd }
  }, [isMobile, currentChapterNumber, totalChapters])

  // Load book data
  useEffect(() => {
    const loadBook = async () => {
      if (!bookId) return

      setLoading(true)
      setError(null)
      
      try {
        const bookData = await fetchBookWithChapters(bookId)
        setBook(bookData)
        
        // Load current chapter
        const targetChapterNumber = progress.currentChapter
        const targetChapter = bookData.chapters?.find(
          ch => ch.chapter_number === targetChapterNumber
        ) || bookData.chapters?.[0]
        
        if (targetChapter) {
          setCurrentChapter(targetChapter)
        }
      } catch (err) {
        setError('Failed to load book content')
        console.error('Error loading book:', err)
      } finally {
        setLoading(false)
      }
    }

    loadBook()
  }, [bookId, progress.currentChapter])

  // Restore scroll position for desktop after chapter loads
  useEffect(() => {
    if (!isMobile && currentChapter && scrollContainerRef.current) {
      const container = scrollContainerRef.current
      // Small delay to ensure content is rendered
      setTimeout(() => {
        container.scrollTop = progress.scrollPosition
      }, 100)
    }
  }, [currentChapter, isMobile, progress.scrollPosition])

  // Touch event listeners setup
  useEffect(() => {
    if (!isMobile || !touchHandlers.handleTouchStart) return

    const container = scrollContainerRef.current
    if (container) {
      const { handleTouchStart, handleTouchEnd } = touchHandlers
      
      container.addEventListener('touchstart', handleTouchStart, { passive: true })
      container.addEventListener('touchend', handleTouchEnd, { passive: true })
      
      return () => {
        container.removeEventListener('touchstart', handleTouchStart)
        container.removeEventListener('touchend', handleTouchEnd)
      }
    }
  }, [isMobile, touchHandlers])

  // Scroll position tracking for desktop
  useEffect(() => {
    if (isMobile || !scrollContainerRef.current) return

    const container = scrollContainerRef.current
    
    const handleScroll = () => {
      debouncedSaveScrollPosition(container.scrollTop)
    }

    container.addEventListener('scroll', handleScroll, { passive: true })
    
    return () => {
      container.removeEventListener('scroll', handleScroll)
    }
  }, [isMobile, debouncedSaveScrollPosition])

  // Keyboard navigation
  useEffect(() => {
    const handleKeyDown = (e: KeyboardEvent) => {
      // Don't interfere when modal is open or user is typing
      if (settingsOpen || e.target !== document.body) return

      if (KEYBOARD_SHORTCUTS.NEXT_CHAPTER.includes(e.key)) {
        e.preventDefault()
        handleNextChapter()
      } else if (KEYBOARD_SHORTCUTS.PREVIOUS_CHAPTER.includes(e.key)) {
        e.preventDefault()
        handlePreviousChapter()
      } else if (KEYBOARD_SHORTCUTS.TOGGLE_SETTINGS.includes(e.key)) {
        e.preventDefault()
        setSettingsOpen(true)
      } else if (KEYBOARD_SHORTCUTS.GO_BACK.includes(e.key)) {
        e.preventDefault()
        handleBack()
      }
    }

    document.addEventListener('keydown', handleKeyDown)
    
    return () => {
      document.removeEventListener('keydown', handleKeyDown)
    }
  }, [settingsOpen, currentChapterNumber, totalChapters])

  // Navigation functions
  const handleBack = useCallback(() => {
    navigate('/')
  }, [navigate])

  const handlePreviousChapter = useCallback(() => {
    if (currentChapterNumber > 1 && book?.chapters) {
      const prevChapter = book.chapters.find(
        ch => ch.chapter_number === currentChapterNumber - 1
      )
      if (prevChapter) {
        setCurrentChapter(prevChapter)
        setProgress(prev => ({
          ...prev,
          currentChapter: currentChapterNumber - 1,
          scrollPosition: 0, // Reset scroll position for new chapter
          lastReadDate: new Date().toISOString()
        }))
      }
    }
  }, [currentChapterNumber, book, setProgress])

  const handleNextChapter = useCallback(() => {
    if (currentChapterNumber < totalChapters && book?.chapters) {
      const nextChapter = book.chapters.find(
        ch => ch.chapter_number === currentChapterNumber + 1
      )
      if (nextChapter) {
        setCurrentChapter(nextChapter)
        setProgress(prev => ({
          ...prev,
          currentChapter: currentChapterNumber + 1,
          scrollPosition: 0, // Reset scroll position for new chapter
          lastReadDate: new Date().toISOString()
        }))
      }
    }
  }, [currentChapterNumber, totalChapters, book, setProgress])

  // Handle settings change
  const handleSettingsChange = useCallback((newSettings: ReaderSettings) => {
    setSettings(newSettings)
  }, [setSettings])

  if (!bookId) {
    return (
      <Box sx={{ p: 3 }}>
        <Alert severity="error">Book ID is required</Alert>
      </Box>
    )
  }

  return (
    <ErrorBoundary>
      <Box sx={{ height: 'calc(100vh - 64px)', display: 'flex', flexDirection: 'column' }}>
        {/* Control Panel */}
        <Paper elevation={1} sx={{ p: 2, display: 'flex', alignItems: 'center', gap: 2 }}>
          <IconButton onClick={handleBack} aria-label="back to library">
            <ArrowBack />
          </IconButton>

          <Box sx={{ flexGrow: 1, mx: 2 }}>
            <Box sx={{ display: 'flex', justifyContent: 'space-between', mb: 1 }}>
              <Typography variant="body2" color="text.secondary">
                Chapter {currentChapterNumber} of {totalChapters}
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
            {book && (
              <Typography variant="caption" color="text.secondary" sx={{ mt: 0.5 }}>
                {book.title} by {book.author}
              </Typography>
            )}
          </Box>

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
            backgroundColor: 'background.paper',
          }}
        >
          {loading && (
            <Box sx={{ 
              display: 'flex', 
              justifyContent: 'center', 
              alignItems: 'center', 
              height: '100%' 
            }}>
              <CircularProgress />
            </Box>
          )}

          {error && (
            <Box sx={{ p: 3 }}>
              <Alert severity="error">{error}</Alert>
            </Box>
          )}

          {currentChapter && !loading && (
            <Fade in timeout={ANIMATION_DURATION.CHAPTER_TRANSITION}>
              <Box
                sx={{
                  p: READER_LAYOUT.CONTENT_PADDING / 8,
                  maxWidth: READER_LAYOUT.MAX_CONTENT_WIDTH,
                  mx: 'auto',
                  minHeight: isMobile ? '100%' : 'auto',
                  display: 'flex',
                  flexDirection: 'column',
                  justifyContent: isMobile ? 'flex-start' : 'flex-start',
                }}
              >
                {currentChapter.title && (
                  <Typography 
                    variant="h4" 
                    component="h1" 
                    gutterBottom 
                    sx={{ 
                      mb: 4,
                      fontWeight: 'bold',
                      color: 'primary.main'
                    }}
                  >
                    {currentChapter.title}
                  </Typography>
                )}
                
                <Typography
                  component="div"
                  sx={{
                    fontSize: `${settings.fontSize}px`,
                    lineHeight: settings.lineSpacing,
                    whiteSpace: 'pre-line',
                    userSelect: 'text',
                    '& h1, & h2, & h3, & h4, & h5, & h6': {
                      marginTop: theme.spacing(3),
                      marginBottom: theme.spacing(2),
                      fontWeight: 'bold',
                    },
                    '& h1': { fontSize: `${settings.fontSize * 2}px` },
                    '& h2': { fontSize: `${settings.fontSize * 1.75}px` },
                    '& h3': { fontSize: `${settings.fontSize * 1.5}px` },
                    '& p': {
                      marginBottom: theme.spacing(2),
                    },
                  }}
                >
                  {currentChapter.content}
                </Typography>

                {/* Word count info */}
                <Box sx={{ mt: 4, pt: 2, borderTop: 1, borderColor: 'divider' }}>
                  <Typography variant="caption" color="text.secondary">
                    Word count: {currentChapter.word_count.toLocaleString()}
                  </Typography>
                </Box>
              </Box>
            </Fade>
          )}

          {/* Mobile Chapter Navigation Buttons */}
          {isMobile && currentChapter && !loading && (
            <>
              {currentChapterNumber > 1 && (
                <IconButton
                  onClick={handlePreviousChapter}
                  sx={{
                    position: 'absolute',
                    left: 16,
                    top: '50%',
                    transform: 'translateY(-50%)',
                    backgroundColor: 'background.paper',
                    boxShadow: 2,
                    width: READER_LAYOUT.MOBILE_BUTTON_SIZE,
                    height: READER_LAYOUT.MOBILE_BUTTON_SIZE,
                    '&:hover': {
                      backgroundColor: 'background.paper',
                      boxShadow: 4,
                    },
                  }}
                  aria-label="previous chapter"
                >
                  <ChevronLeft />
                </IconButton>
              )}

              {currentChapterNumber < totalChapters && (
                <IconButton
                  onClick={handleNextChapter}
                  sx={{
                    position: 'absolute',
                    right: 16,
                    top: '50%',
                    transform: 'translateY(-50%)',
                    backgroundColor: 'background.paper',
                    boxShadow: 2,
                    width: READER_LAYOUT.MOBILE_BUTTON_SIZE,
                    height: READER_LAYOUT.MOBILE_BUTTON_SIZE,
                    '&:hover': {
                      backgroundColor: 'background.paper',
                      boxShadow: 4,
                    },
                  }}
                  aria-label="next chapter"
                >
                  <ChevronRight />
                </IconButton>
              )}
            </>
          )}
        </Box>

        {/* Desktop Chapter Navigation */}
        {!isMobile && currentChapter && !loading && (
          <Paper elevation={1} sx={{ p: 1, display: 'flex', justifyContent: 'center', gap: 2 }}>
            <IconButton
              onClick={handlePreviousChapter}
              disabled={currentChapterNumber <= 1}
              aria-label="previous chapter"
              size="small"
            >
              <ChevronLeft />
            </IconButton>
            
            <Box sx={{ display: 'flex', alignItems: 'center', px: 2 }}>
              <Typography variant="body2" sx={{ mr: 2 }}>
                Chapter Navigation
              </Typography>
              <Typography variant="caption" color="text.secondary">
                Use arrow keys or click buttons
              </Typography>
            </Box>
            
            <IconButton
              onClick={handleNextChapter}
              disabled={currentChapterNumber >= totalChapters}
              aria-label="next chapter"
              size="small"
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
    </ErrorBoundary>
  )
}

export default BookReaderPage