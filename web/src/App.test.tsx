import { render, screen } from '@testing-library/react'
import { ThemeProvider } from '@mui/material/styles'
import CssBaseline from '@mui/material/CssBaseline'
import { describe, it, expect, vi } from 'vitest'
import App from './App'
import theme from './theme'

// Mock the BooksLandingPage component to avoid API calls in smoke tests
vi.mock('./components/BooksLandingPage', () => ({
  default: () => <div data-testid="books-landing-page">Books Landing Page</div>
}))

// Mock the PWABadge component
vi.mock('./PWABadge', () => ({
  default: () => <div data-testid="pwa-badge">PWA Badge</div>
}))

describe('App Smoke Tests', () => {
  const renderApp = () => {
    return render(
      <ThemeProvider theme={theme}>
        <CssBaseline />
        <App />
      </ThemeProvider>
    )
  }

  it('renders without crashing', () => {
    renderApp()
    expect(screen.getByText('Flute - Your Reading Companion')).toBeInTheDocument()
  })

  it('renders the app bar with title', () => {
    renderApp()
    expect(screen.getByText('Flute - Your Reading Companion')).toBeInTheDocument()
    expect(screen.getByText('Profile')).toBeInTheDocument()
    expect(screen.getByText('Settings')).toBeInTheDocument()
  })

  it('renders the main components', () => {
    renderApp()
    
    // Check that main components are rendered
    expect(screen.getByTestId('books-landing-page')).toBeInTheDocument()
    expect(screen.getByTestId('pwa-badge')).toBeInTheDocument()
  })

  it('renders the floating action button', () => {
    renderApp()
    
    // Check for FAB (add book button)
    const fab = screen.getByLabelText('add book')
    expect(fab).toBeInTheDocument()
  })

  it('has the correct page structure', () => {
    renderApp()
    
    // Verify basic page structure exists
    const appContainer = screen.getByText('Flute - Your Reading Companion').closest('[class*="MuiBox"]')
    expect(appContainer).toBeInTheDocument()
  })
})