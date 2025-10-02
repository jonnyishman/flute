import { useState, useEffect, useCallback } from 'react'
import { useParams, useNavigate } from 'react-router-dom'
import { useAtom } from 'jotai'
import {
  Box,
  AppBar,
  Toolbar,
  IconButton,
  Typography,
  LinearProgress,
  Drawer,
  List,
  ListItem,
  Slider,
  FormLabel,
  useTheme,
  useMediaQuery,
  Alert,
  Snackbar,
  CircularProgress,
  Fade,
} from '@mui/material'
import {
  ArrowBack,
  Settings as SettingsIcon,
  Close,
  KeyboardArrowLeft,
  KeyboardArrowRight,
} from '@mui/icons-material'
import { fetchBooks } from '../data/mockBooks'
import { Book } from '../types/book'
import { readerSettingsAtom, ReaderSettings } from '../store/atoms'
import useBookProgress from '../hooks/useBookProgress'
import { api } from '../api'

interface BookReaderProps {
  book?: Book
  chapter?: number
  onBackToLibrary?: () => void
}


interface BookReaderState {
  book: Book | null
  loading: boolean
  error: string | null
  chapterContent: string
  settingsOpen: boolean
  currentChapter: number
  showTransition: boolean
}

// Haptic feedback function
const triggerHapticFeedback = () => {
  if ('vibrate' in navigator && navigator.vibrate) {
    navigator.vibrate(50) // Brief haptic feedback
  }
}

const BookReader = ({ book: propBook, chapter: propChapter, onBackToLibrary }: BookReaderProps) => {
  const { bookId, chapterId } = useParams<{ bookId: string; chapterId: string }>()
  const navigate = useNavigate()
  const theme = useTheme()
  const isMobile = useMediaQuery(theme.breakpoints.down('md'))
  
  // Jotai atoms
  const [readerSettings, setReaderSettings] = useAtom(readerSettingsAtom)
  const { 
    updateBookProgress, 
    startReadingSession, 
    endReadingSession 
  } = useBookProgress()
  
  
  const [state, setState] = useState<BookReaderState>({
    book: propBook || null,
    loading: !propBook,
    error: null,
    chapterContent: '',
    settingsOpen: false,
    currentChapter: propChapter || (propBook?.lastReadChapter ?? 1),
    showTransition: false,
  })

  // Prevent body scroll when reader is mounted
  useEffect(() => {
    const originalOverflow = document.body.style.overflow
    const originalHeight = document.body.style.height
    document.body.style.overflow = 'hidden'
    document.body.style.height = '100%'

    return () => {
      document.body.style.overflow = originalOverflow
      document.body.style.height = originalHeight
    }
  }, [])

  // Start reading session when book and chapter are loaded
  useEffect(() => {
    if (state.book && !state.loading) {
      startReadingSession(state.book.id, state.currentChapter)
    }
  }, [state.book, state.currentChapter, state.loading, startReadingSession])

  // End reading session on unmount
  useEffect(() => {
    return () => {
      endReadingSession()
    }
  }, [endReadingSession])

  // Load book data if not provided via props
  useEffect(() => {
    if (!state.book && bookId) {
      let isMounted = true

      const loadBook = async () => {
        try {
          if (!isMounted) return
          setState(prev => ({ ...prev, loading: true, error: null }))

          const booksData = await fetchBooks(1, 150)
          if (!isMounted) return

          const foundBook = booksData.books.find(b => b.id === bookId)

          if (!foundBook) {
            if (!isMounted) return
            setState(prev => ({ ...prev, loading: false, error: 'Book not found' }))
            return
          }

          // Fetch chapter count from backend
          try {
            const chapterCountResponse = await api.books.getChapterCount(parseInt(bookId, 10))
            if (!isMounted) return

            setState(prev => ({
              ...prev,
              book: { ...foundBook, totalChapters: chapterCountResponse.count },
              loading: false,
              currentChapter: chapterId ? parseInt(chapterId, 10) : foundBook.lastReadChapter ?? 1
            }))
          } catch (chapterCountError) {
            console.error('Failed to load chapter count:', chapterCountError)
            if (!isMounted) return
            setState(prev => ({ ...prev, loading: false, error: 'Failed to load chapter count' }))
          }
        } catch (error) {
          console.error('Failed to load book:', error)
          if (!isMounted) return
          setState(prev => ({ ...prev, loading: false, error: 'Failed to load book' }))
        }
      }

      loadBook()

      return () => {
        isMounted = false
      }
    }
  }, [bookId, chapterId, state.book])

  // Load chapter content from API
  useEffect(() => {
    if (!state.book) return

    const book = state.book
    const chapter = state.currentChapter

    const loadChapter = async () => {
      try {
        setState(prev => ({ ...prev, showTransition: true }))

        const response = await api.books.getChapterWithHighlights(parseInt(book.id, 10), chapter)

        // Transition delay for smooth UI
        setTimeout(() => {
          setState(prev => ({
            ...prev,
            chapterContent: response.chapter.content,
            showTransition: false,
          }))
        }, 150)
      } catch (error) {
        console.error('Failed to load chapter:', error)
        setState(prev => ({
          ...prev,
          showTransition: false,
          error: 'Failed to load chapter content',
        }))
      }
    }

    loadChapter()
  }, [state.book, state.currentChapter])

  // Update URL when chapter changes
  useEffect(() => {
    if (state.book && bookId && chapterId) {
      const newChapterId = state.currentChapter.toString()
      if (newChapterId !== chapterId) {
        navigate(`/book/${bookId}/chapter/${newChapterId}`, { replace: true })
      }
    }
  }, [state.currentChapter, state.book, bookId, chapterId, navigate])

  const handleSettingChange = useCallback((setting: keyof ReaderSettings, value: number) => {
    setReaderSettings(prev => ({
      ...prev,
      [setting]: value
    }))
  }, [setReaderSettings])

  const handleBackToLibrary = useCallback(() => {
    if (onBackToLibrary) {
      onBackToLibrary()
    } else {
      navigate('/')
    }
  }, [navigate, onBackToLibrary])

  const changeChapter = useCallback((delta: number) => {
    if (!state.book) return
    
    const newChapter = state.currentChapter + delta
    if (newChapter >= 1 && newChapter <= state.book.totalChapters) {
      triggerHapticFeedback()
      setState(prev => ({ ...prev, currentChapter: newChapter }))
      // Update book progress when changing chapters
      updateBookProgress(state.book.id, newChapter)
    }
  }, [state.book, state.currentChapter, updateBookProgress])

  // Mobile swipe handlers removed - horizontal swiping now scrolls through text content
  // Chapter navigation on mobile is handled through the navigation buttons in the toolbar

  // Keyboard navigation
  useEffect(() => {
    const handleKeyDown = (e: KeyboardEvent) => {
      if (e.key === 'ArrowLeft' || e.key === 'h') {
        e.preventDefault()
        changeChapter(-1)
      } else if (e.key === 'ArrowRight' || e.key === 'l') {
        e.preventDefault()
        changeChapter(1)
      } else if (e.key === 'Escape') {
        e.preventDefault()
        handleBackToLibrary()
      }
    }

    window.addEventListener('keydown', handleKeyDown)
    return () => window.removeEventListener('keydown', handleKeyDown)
  }, [changeChapter, handleBackToLibrary])

  if (state.loading) {
    return (
      <Box
        sx={{
          display: 'flex',
          justifyContent: 'center',
          alignItems: 'center',
          height: { xs: '100dvh', fallbacks: ['100vh'] },
          flexDirection: 'column',
          gap: 2
        }}
      >
        <CircularProgress size={60} />
        <Typography variant="body1">Loading book...</Typography>
      </Box>
    )
  }

  if (state.error) {
    return (
      <Box
        sx={{
          display: 'flex',
          justifyContent: 'center',
          alignItems: 'center',
          height: { xs: '100dvh', fallbacks: ['100vh'] },
          flexDirection: 'column',
          gap: 2,
          p: 2
        }}
      >
        <Alert severity="error" sx={{ maxWidth: 400 }}>
          {state.error}
        </Alert>
        <IconButton onClick={handleBackToLibrary} size="large">
          <ArrowBack />
        </IconButton>
      </Box>
    )
  }

  if (!state.book) {
    return null
  }

  const progressPercentage = Math.round((state.currentChapter / state.book.totalChapters) * 100)

  return (
    <Box sx={{
      height: { xs: '100dvh', fallbacks: ['100vh'] },
      display: 'flex',
      flexDirection: 'column',
      position: 'relative',
      overflow: 'hidden'
    }}>
      {/* Skip navigation for screen readers */}
      <Box
        component="a"
        href="#main-content"
        sx={{
          position: 'absolute',
          left: '-9999px',
          '&:focus': {
            position: 'static',
            zIndex: 9999,
            p: 1,
            bgcolor: 'primary.main',
            color: 'primary.contrastText'
          }
        }}
      >
        Skip to main content
      </Box>

      {/* Control Panel */}
      <AppBar position="static" color="default" elevation={1}>
        <Toolbar sx={{ minHeight: { xs: 56, sm: 64 }, px: { xs: 1, sm: 3 } }}>
          {/* Back Button */}
          <IconButton
            edge="start"
            onClick={handleBackToLibrary}
            sx={{ mr: { xs: 1, sm: 2 } }}
            aria-label="Back to library"
          >
            <ArrowBack />
          </IconButton>

          {/* Navigation Controls */}
          <IconButton
            onClick={() => changeChapter(-1)}
            disabled={state.currentChapter <= 1}
            aria-label="Previous chapter"
            sx={{ mr: { xs: 1, sm: 1 } }}
          >
            <KeyboardArrowLeft />
          </IconButton>

          {/* Progress Section - Middle */}
          <Box sx={{
            flexGrow: 1,
            display: 'flex',
            flexDirection: 'column',
            alignItems: 'center',
            justifyContent: 'center',
            minWidth: 0,
            mx: { xs: 1, sm: 2 }
          }}>
            {/* Chapter Info - Always visible */}
            <Typography
              variant="body2"
              color="text.secondary"
              sx={{
                fontSize: { xs: '0.875rem', sm: '0.875rem' },
                fontWeight: { xs: 500, sm: 400 },
                whiteSpace: 'nowrap'
              }}
            >
              {isMobile ? `${state.currentChapter}/${state.book.totalChapters}` : `Chapter ${state.currentChapter} of ${state.book.totalChapters}`}
            </Typography>

            {/* Progress Bar - Hidden on xs screens */}
            <Box sx={{
              display: { xs: 'none', sm: 'flex' },
              alignItems: 'center',
              width: { sm: '150px', md: '200px' },
              mt: 0.5
            }}>
              <Typography
                variant="caption"
                sx={{ mr: 1 }}
                aria-hidden="true"
              >
                {progressPercentage}%
              </Typography>
              <LinearProgress
                variant="determinate"
                value={progressPercentage}
                sx={{
                  flexGrow: 1,
                  mr: 1,
                  height: 4,
                  borderRadius: 2
                }}
                aria-label={`Reading progress: ${progressPercentage}% complete`}
              />
              <Typography
                variant="caption"
                aria-hidden="true"
              >
                100%
              </Typography>
            </Box>
          </Box>

          <IconButton
            onClick={() => changeChapter(1)}
            disabled={state.currentChapter >= state.book.totalChapters}
            aria-label="Next chapter"
            sx={{ mr: { xs: 1, sm: 2 } }}
          >
            <KeyboardArrowRight />
          </IconButton>

          {/* Settings Button */}
          <IconButton
            edge="end"
            onClick={() => setState(prev => ({ ...prev, settingsOpen: true }))}
            aria-label="Open reading settings"
          >
            <SettingsIcon />
          </IconButton>
        </Toolbar>
      </AppBar>

      {/* Chapter Content */}
      <Box
        id="main-content"
        component="main"
        role="main"
        tabIndex={-1}
        sx={{
          flexGrow: 1,
          overflow: 'auto',
          overflowX: 'hidden',
          p: { xs: 2, md: 4 },
          maxWidth: '800px',
          margin: '0 auto',
          width: '100%',
          fontSize: `${readerSettings.fontSize}px`,
          lineHeight: readerSettings.lineSpacing,
          fontFamily: 'Georgia, serif',
          minHeight: 0,
          position: 'relative',
          WebkitOverflowScrolling: 'touch',
          scrollBehavior: 'smooth',
          ...(isMobile && {
            touchAction: 'pan-y',
          })
        }}
        aria-live="polite"
        aria-label={`Reading ${state.book.title}, Chapter ${state.currentChapter}`}
      >
        <Fade in={!state.showTransition}>
          <div>
            <Typography
              variant="h4"
              component="h1"
              gutterBottom
              sx={{ 
                mb: 4, 
                textAlign: 'center',
                fontSize: `${readerSettings.fontSize * 1.5}px`
              }}
            >
              {state.book.title}
            </Typography>
            
            <Typography
              variant="h5"
              component="h2"
              gutterBottom
              sx={{ 
                mb: 3, 
                color: 'text.secondary',
                textAlign: 'center',
                fontSize: `${readerSettings.fontSize * 1.25}px`
              }}
            >
              Chapter {state.currentChapter}
            </Typography>

            <Box sx={{ textAlign: 'justify' }}>
              {state.chapterContent.split('\n\n').map((paragraph, index) => (
                <Typography
                  key={`paragraph-${index}`}
                  paragraph
                  sx={{ 
                    mb: 2,
                    fontSize: `${readerSettings.fontSize}px`,
                    lineHeight: readerSettings.lineSpacing,
                  }}
                >
                  {paragraph}
                </Typography>
              ))}
            </Box>

            {/* Navigation hint for mobile */}
            {isMobile && (
              <Box sx={{ textAlign: 'center', mt: 4, color: 'text.secondary' }}>
                <Typography variant="caption">
                  Use chapter navigation buttons in the toolbar • Scroll horizontally through text
                </Typography>
              </Box>
            )}
          </div>
        </Fade>
      </Box>

      {/* Settings Drawer */}
      <Drawer
        anchor="right"
        open={state.settingsOpen}
        onClose={() => setState(prev => ({ ...prev, settingsOpen: false }))}
        PaperProps={{
          sx: { width: { xs: '100%', sm: 350 }, p: 2 }
        }}
      >
        <Box sx={{ display: 'flex', alignItems: 'center', mb: 3 }}>
          <Typography variant="h6" sx={{ flexGrow: 1 }}>
            Reading Settings
          </Typography>
          <IconButton 
            onClick={() => setState(prev => ({ ...prev, settingsOpen: false }))}
            aria-label="Close settings"
          >
            <Close />
          </IconButton>
        </Box>

        <List>
          <ListItem sx={{ flexDirection: 'column', alignItems: 'stretch' }}>
            <FormLabel component="legend" sx={{ mb: 2 }}>
              Font Size: {readerSettings.fontSize}px
            </FormLabel>
            <Slider
              value={readerSettings.fontSize}
              onChange={(_, value) => handleSettingChange('fontSize', value as number)}
              min={12}
              max={24}
              step={1}
              marks
              valueLabelDisplay="auto"
              aria-label="Font size"
            />
          </ListItem>

          <ListItem sx={{ flexDirection: 'column', alignItems: 'stretch' }}>
            <FormLabel component="legend" sx={{ mb: 2 }}>
              Line Spacing: {readerSettings.lineSpacing}
            </FormLabel>
            <Slider
              value={readerSettings.lineSpacing}
              onChange={(_, value) => handleSettingChange('lineSpacing', value as number)}
              min={1.2}
              max={2.5}
              step={0.1}
              marks
              valueLabelDisplay="auto"
              aria-label="Line spacing"
            />
          </ListItem>
        </List>

        <Box sx={{ mt: 3, p: 2, bgcolor: 'background.paper', borderRadius: 1 }}>
          <Typography variant="body2" color="text.secondary">
            Sample text with current settings:
          </Typography>
          <Typography 
            sx={{ 
              mt: 1, 
              fontSize: `${readerSettings.fontSize}px`,
              lineHeight: readerSettings.lineSpacing,
              fontFamily: 'Georgia, serif'
            }}
          >
            The quick brown fox jumps over the lazy dog. This text shows how your reading experience will look with the current font size and line spacing settings.
          </Typography>
        </Box>

        <Box sx={{ mt: 2, p: 2, bgcolor: 'info.light', borderRadius: 1 }}>
          <Typography variant="body2" color="info.contrastText">
            <strong>Keyboard shortcuts:</strong><br />
            • Arrow keys or H/L: Navigate chapters<br />
            • Escape: Return to library
          </Typography>
        </Box>
      </Drawer>

      {/* Error notification */}
      <Snackbar
        open={!!state.error}
        autoHideDuration={6000}
        onClose={() => setState(prev => ({ ...prev, error: null }))}
      >
        <Alert severity="error" onClose={() => setState(prev => ({ ...prev, error: null }))}>
          {state.error}
        </Alert>
      </Snackbar>
    </Box>
  )
}

export default BookReader
