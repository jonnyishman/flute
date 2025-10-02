import { render, screen, fireEvent } from '@testing-library/react'
import { describe, it, expect, vi } from 'vitest'
import { ThemeProvider } from '@mui/material/styles'
import theme from '../theme'
import BookTile from './BookTile'
import { Book } from '../types/book'

const mockBook: Book = {
  id: '1',
  title: 'Test Book',
  coverArt: 'https://example.com/cover.jpg',
  readProgressRatio: 0.5,
  wordCount: 50000,
  knownWords: 25000,
  learningWords: 15000,
  unknownWords: 10000,
  lastReadDate: '2023-12-01T00:00:00Z',
}

const renderBookTile = (props = {}) => {
  const defaultProps = {
    book: mockBook,
    ...props
  }
  
  return render(
    <ThemeProvider theme={theme}>
      <BookTile {...defaultProps} />
    </ThemeProvider>
  )
}

describe('BookTile Options Menu', () => {
  it('renders BookTile without options menu initially', () => {
    renderBookTile()
    
    expect(screen.getByText('Test Book')).toBeInTheDocument()
    expect(screen.getByLabelText('book options')).toBeInTheDocument()
    expect(screen.queryByText('Edit')).not.toBeInTheDocument()
    expect(screen.queryByText('Archive')).not.toBeInTheDocument()
    expect(screen.queryByText('Delete')).not.toBeInTheDocument()
  })

  it('opens options menu when menu button is clicked', () => {
    renderBookTile()
    
    const menuButton = screen.getByLabelText('book options')
    fireEvent.click(menuButton)
    
    expect(screen.getByText('Edit')).toBeInTheDocument()
    expect(screen.getByText('Archive')).toBeInTheDocument()
    expect(screen.getByText('Delete')).toBeInTheDocument()
  })

  it('does not trigger card onClick when menu button is clicked', () => {
    const onClickMock = vi.fn()
    renderBookTile({ onClick: onClickMock })
    
    const menuButton = screen.getByLabelText('book options')
    fireEvent.click(menuButton)
    
    expect(onClickMock).not.toHaveBeenCalled()
  })
})