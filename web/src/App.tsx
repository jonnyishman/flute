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
import PWABadge from './PWABadge.tsx'

function App() {
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

      <BooksLandingPage />

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
