import { useState } from 'react'
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
import BooksLandingPage from './components/BooksLandingPage'
import BookReader from './components/BookReader'
import PWABadge from './PWABadge.tsx'
import { Book } from './types/book'

function App() {
  const [currentView, setCurrentView] = useState<'library' | 'reader'>('library')
  const [selectedBook, setSelectedBook] = useState<Book | null>(null)
  const [selectedChapter, setSelectedChapter] = useState<number>(1)

  const handleBookClick = (book: Book) => {
    setSelectedBook(book)
    setSelectedChapter(book.lastReadChapter)
    setCurrentView('reader')
  }

  const handleBackToLibrary = () => {
    setCurrentView('library')
    setSelectedBook(null)
  }

  if (currentView === 'reader' && selectedBook) {
    return (
      <BookReader 
        book={selectedBook}
        chapter={selectedChapter}
        onBackToLibrary={handleBackToLibrary}
      />
    )
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

export default App
