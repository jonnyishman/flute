import {
  AppBar,
  Toolbar,
  Typography,
  Button,
  Box,
  Fab,
} from '@mui/material'
import {
  Add,
  MenuBook,
} from '@mui/icons-material'
import { BrowserRouter as Router, Routes, Route, useNavigate } from 'react-router-dom'
import BooksLandingPage from './components/BooksLandingPage'
import BookReader from './components/BookReader'
import BookUpload from './components/BookUpload'
import LanguageChooser from './components/LanguageChooser'
import PWABadge from './PWABadge.tsx'
import { Book } from './types/book'
import StoreProvider from './store/StoreProvider'
import useBookProgress from './hooks/useBookProgress'
import { ApiProvider } from './api'

function LibraryPage() {
  const navigate = useNavigate()
  const { getBookProgress } = useBookProgress()

  const handleBookClick = (book: Book) => {
    // Use stored progress if available, otherwise use book's default
    const progress = getBookProgress(book.id)
    const lastChapter = progress?.lastChapter ?? book.lastReadChapter
    navigate(`/book/${book.id}/chapter/${lastChapter}`)
  }

  return (
    <Box sx={{ flexGrow: 1, minHeight: '100vh', bgcolor: 'background.default' }}>
      <AppBar position="static">
        <Toolbar>
          <LanguageChooser />
          <MenuBook sx={{ mr: 2, ml: 1 }} />
          <Typography variant="h6" component="div" sx={{ flexGrow: 1 }}>
            Flute - Your Reading Companion
          </Typography>
          <Button color="inherit">Profile</Button>
          <Button color="inherit">Settings</Button>
        </Toolbar>
      </AppBar>

      <BooksLandingPage onBookClick={handleBookClick} />

      <PWABadge />

      {/* Floating Action Button for adding books */}
      <Fab
        color="primary"
        aria-label="add book"
        onClick={() => navigate('/upload')}
        sx={{
          position: 'fixed',
          bottom: 16,
          right: 16,
        }}
      >
        <Add />
      </Fab>
    </Box>
  )
}

function App() {
  return (
    <ApiProvider>
      <StoreProvider>
        <Router>
          <Routes>
            <Route path="/" element={<LibraryPage />} />
            <Route path="/upload" element={<BookUpload />} />
            <Route path="/book/:bookId/chapter/:chapterId" element={<BookReader />} />
          </Routes>
        </Router>
      </StoreProvider>
    </ApiProvider>
  )
}

export default App
