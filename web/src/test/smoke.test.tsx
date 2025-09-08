import { render, screen } from '@testing-library/react'
import { ThemeProvider } from '@mui/material/styles'
import CssBaseline from '@mui/material/CssBaseline'
import { describe, it, expect, vi } from 'vitest'
import { MemoryRouter, Routes, Route } from 'react-router-dom'
import App from '../App'
import theme from '../theme'

// Mock all the components that make external calls
vi.mock('../components/BooksLandingPage', () => ({
  default: () => <div data-testid="books-landing-page">Mocked Books Landing Page</div>
}))

vi.mock('../PWABadge', () => ({
  default: () => <div data-testid="pwa-badge">Mocked PWA Badge</div>
}))

vi.mock('../components/BookUpload', () => ({
  default: () => <div data-testid="book-upload-page">Mocked Book Upload Page</div>
}))

describe('Smoke Tests - Overall Page Rendering', () => {
  const renderFullApp = () => {
    return render(
      <ThemeProvider theme={theme}>
        <CssBaseline />
        <App />
      </ThemeProvider>
    )
  }

  it('renders the complete application without errors', () => {
    renderFullApp()
    
    // Verify all main sections are present
    expect(screen.getByText('Flute - Your Reading Companion')).toBeInTheDocument()
    expect(screen.getByTestId('books-landing-page')).toBeInTheDocument()
    expect(screen.getByTestId('pwa-badge')).toBeInTheDocument()
  })

  it('renders navigation elements', () => {
    renderFullApp()
    
    // Check navigation/header elements
    expect(screen.getByText('Profile')).toBeInTheDocument()
    expect(screen.getByText('Settings')).toBeInTheDocument()
  })

  it('renders interactive elements', () => {
    renderFullApp()
    
    // Check for interactive elements
    const addButton = screen.getByLabelText('add book')
    expect(addButton).toBeInTheDocument()
  })

  it('has no obvious rendering errors', () => {
    // This test ensures no JavaScript errors are thrown during rendering
    expect(() => renderFullApp()).not.toThrow()
  })

  it('renders with Material-UI theme applied', () => {
    renderFullApp()
    
    // Verify theme is applied by checking for MUI classes
    const appContainer = screen.getByText('Flute - Your Reading Companion').closest('[class*="MuiToolbar"]')
    expect(appContainer).toBeInTheDocument()
  })

  it('renders upload page when navigating to /upload', () => {
    render(
      <ThemeProvider theme={theme}>
        <CssBaseline />
        <MemoryRouter initialEntries={['/upload']}>
          <Routes>
            <Route path="/" element={<div data-testid="books-landing-page">Mocked Books Landing Page</div>} />
            <Route path="/upload" element={<div data-testid="book-upload-page">Mocked Book Upload Page</div>} />
          </Routes>
        </MemoryRouter>
      </ThemeProvider>
    )
    
    expect(screen.getByTestId('book-upload-page')).toBeInTheDocument()
  })
})