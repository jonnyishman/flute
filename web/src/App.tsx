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
import PWABadge from './PWABadge.tsx'
import { Book } from './types/book'

function LibraryPage() {
  const navigate = useNavigate()

  const handleBookClick = (book: Book) => {
    navigate(`/book/${book.id}/chapter/${book.lastReadChapter}`)
  }

  return (
    <Box sx={{ flexGrow: 1, minHeight: '100vh', bgcolor: 'background.default' }}>
      <AppBar position="static">
        <Toolbar>
          <MenuBook sx={{ mr: 2 }} />
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
    <Router>
      <Routes>
        <Route path="/" element={<LibraryPage />} />
        <Route path="/book/:bookId/chapter/:chapterId" element={<BookReader />} />
      </Routes>
    </Router>
  )
}

export default App
