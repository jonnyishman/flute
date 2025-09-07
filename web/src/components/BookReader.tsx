import { useState, useEffect } from 'react'
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
  ListItemText,
  Slider,
  FormLabel,
  useTheme,
  useMediaQuery,
} from '@mui/material'
import {
  ArrowBack,
  Settings as SettingsIcon,
  Close,
} from '@mui/icons-material'
import { Book } from '../types/book'

interface BookReaderProps {
  book: Book
  chapter?: number
  onBackToLibrary: () => void
}

interface ReaderSettings {
  fontSize: number
  lineSpacing: number
}

// Mock chapter data
const generateChapterContent = (bookId: string, chapterNumber: number): string => {
  const paragraphs = Math.floor(Math.random() * 20) + 30 // 30-50 paragraphs per chapter
  const sentences = [
    "The ancient oak tree stood majestically in the center of the village square, its gnarled branches reaching toward the cloudy sky.",
    "She carefully opened the leather-bound book, and the smell of old parchment filled her nostrils.",
    "The sound of footsteps echoed through the empty corridor, growing louder with each passing moment.",
    "Golden sunlight streamed through the tall windows, casting dancing shadows on the worn wooden floor.",
    "He paused at the crossroads, unsure which path would lead him to his destination.",
    "The distant mountains were shrouded in morning mist, their peaks barely visible through the haze.",
    "Her fingers traced the intricate patterns carved into the stone wall, feeling the history beneath her touch.",
    "The old man's eyes twinkled with wisdom as he began to tell his story.",
    "Rain drummed steadily against the windowpane, creating a soothing rhythm that lulled her to sleep.",
    "The market square bustled with activity as vendors called out their wares to passing customers.",
  ]
  
  const content = Array.from({ length: paragraphs }, () => {
    const sentenceCount = Math.floor(Math.random() * 5) + 3 // 3-8 sentences per paragraph
    const paragraphSentences = Array.from({ length: sentenceCount }, () => 
      sentences[Math.floor(Math.random() * sentences.length)]
    )
    return paragraphSentences.join(' ')
  })
  
  return content.join('\n\n')
}

const BookReader = ({ book, chapter = book.lastReadChapter, onBackToLibrary }: BookReaderProps) => {
  const theme = useTheme()
  const isMobile = useMediaQuery(theme.breakpoints.down('md'))
  
  const [settingsOpen, setSettingsOpen] = useState(false)
  const [currentChapter, setCurrentChapter] = useState(chapter)
  const [chapterContent, setChapterContent] = useState('')
  const [scrollPosition, setScrollPosition] = useState(0)
  
  // Load settings from localStorage
  const [settings, setSettings] = useState<ReaderSettings>(() => {
    const saved = localStorage.getItem('flute-reader-settings')
    return saved ? JSON.parse(saved) : { fontSize: 16, lineSpacing: 1.6 }
  })

  // Save settings to localStorage whenever they change
  useEffect(() => {
    localStorage.setItem('flute-reader-settings', JSON.stringify(settings))
  }, [settings])

  // Load chapter content
  useEffect(() => {
    const content = generateChapterContent(book.id, currentChapter)
    setChapterContent(content)
  }, [book.id, currentChapter])

  const handleSettingChange = (setting: keyof ReaderSettings, value: number) => {
    setSettings(prev => ({ ...prev, [setting]: value }))
  }

  const progressPercentage = Math.round((currentChapter / book.totalChapters) * 100)

  const handleTouchStart = (e: React.TouchEvent) => {
    if (!isMobile) return
    setScrollPosition(e.touches[0].clientX)
  }

  const handleTouchEnd = (e: React.TouchEvent) => {
    if (!isMobile) return
    const endPosition = e.changedTouches[0].clientX
    const diff = scrollPosition - endPosition
    
    // Swipe threshold of 50px
    if (Math.abs(diff) > 50) {
      if (diff > 0 && currentChapter < book.totalChapters) {
        // Swipe left - next chapter
        setCurrentChapter(prev => prev + 1)
      } else if (diff < 0 && currentChapter > 1) {
        // Swipe right - previous chapter
        setCurrentChapter(prev => prev - 1)
      }
    }
  }

  return (
    <Box sx={{ height: '100vh', display: 'flex', flexDirection: 'column' }}>
      {/* Control Panel */}
      <AppBar position="static" color="default" elevation={1}>
        <Toolbar>
          {/* Back Button */}
          <IconButton 
            edge="start" 
            onClick={onBackToLibrary}
            sx={{ mr: 2 }}
          >
            <ArrowBack />
          </IconButton>

          {/* Progress Section - Middle */}
          <Box sx={{ flexGrow: 1, display: 'flex', flexDirection: 'column', alignItems: 'center' }}>
            <Typography variant="body2" color="text.secondary">
              Chapter {currentChapter} of {book.totalChapters}
            </Typography>
            <Box sx={{ display: 'flex', alignItems: 'center', width: '200px', mt: 0.5 }}>
              <Typography variant="caption" sx={{ mr: 1 }}>
                {progressPercentage}%
              </Typography>
              <LinearProgress
                variant="determinate"
                value={progressPercentage}
                sx={{ flexGrow: 1, mr: 1, height: 4, borderRadius: 2 }}
              />
              <Typography variant="caption">
                100%
              </Typography>
            </Box>
          </Box>

          {/* Settings Button */}
          <IconButton 
            edge="end" 
            onClick={() => setSettingsOpen(true)}
          >
            <SettingsIcon />
          </IconButton>
        </Toolbar>
      </AppBar>

      {/* Chapter Content */}
      <Box
        component="main"
        sx={{
          flexGrow: 1,
          overflow: isMobile ? 'hidden' : 'auto',
          p: { xs: 2, md: 4 },
          maxWidth: '800px',
          margin: '0 auto',
          width: '100%',
          fontSize: `${settings.fontSize}px`,
          lineHeight: settings.lineSpacing,
          fontFamily: 'Georgia, serif',
          ...(isMobile && {
            touchAction: 'pan-y',
          })
        }}
        onTouchStart={handleTouchStart}
        onTouchEnd={handleTouchEnd}
      >
        <Typography
          variant="h4"
          component="h1"
          gutterBottom
          sx={{ 
            mb: 4, 
            textAlign: 'center',
            fontSize: `${settings.fontSize * 1.5}px`
          }}
        >
          {book.title}
        </Typography>
        
        <Typography
          variant="h5"
          component="h2"
          gutterBottom
          sx={{ 
            mb: 3, 
            color: 'text.secondary',
            textAlign: 'center',
            fontSize: `${settings.fontSize * 1.25}px`
          }}
        >
          Chapter {currentChapter}
        </Typography>

        <Box sx={{ textAlign: 'justify' }}>
          {chapterContent.split('\n\n').map((paragraph, index) => (
            <Typography
              key={index}
              paragraph
              sx={{ 
                mb: 2,
                fontSize: `${settings.fontSize}px`,
                lineHeight: settings.lineSpacing,
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
              Swipe left for next chapter, right for previous
            </Typography>
          </Box>
        )}
      </Box>

      {/* Settings Drawer */}
      <Drawer
        anchor="right"
        open={settingsOpen}
        onClose={() => setSettingsOpen(false)}
        PaperProps={{
          sx: { width: { xs: '100%', sm: 350 }, p: 2 }
        }}
      >
        <Box sx={{ display: 'flex', alignItems: 'center', mb: 3 }}>
          <Typography variant="h6" sx={{ flexGrow: 1 }}>
            Reading Settings
          </Typography>
          <IconButton onClick={() => setSettingsOpen(false)}>
            <Close />
          </IconButton>
        </Box>

        <List>
          <ListItem sx={{ flexDirection: 'column', alignItems: 'stretch' }}>
            <FormLabel component="legend" sx={{ mb: 2 }}>
              Font Size: {settings.fontSize}px
            </FormLabel>
            <Slider
              value={settings.fontSize}
              onChange={(_, value) => handleSettingChange('fontSize', value as number)}
              min={12}
              max={24}
              step={1}
              marks
              valueLabelDisplay="auto"
            />
          </ListItem>

          <ListItem sx={{ flexDirection: 'column', alignItems: 'stretch' }}>
            <FormLabel component="legend" sx={{ mb: 2 }}>
              Line Spacing: {settings.lineSpacing}
            </FormLabel>
            <Slider
              value={settings.lineSpacing}
              onChange={(_, value) => handleSettingChange('lineSpacing', value as number)}
              min={1.2}
              max={2.5}
              step={0.1}
              marks
              valueLabelDisplay="auto"
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
              fontSize: `${settings.fontSize}px`,
              lineHeight: settings.lineSpacing,
              fontFamily: 'Georgia, serif'
            }}
          >
            The quick brown fox jumps over the lazy dog. This text shows how your reading experience will look with the current font size and line spacing settings.
          </Typography>
        </Box>
      </Drawer>
    </Box>
  )
}

export default BookReader