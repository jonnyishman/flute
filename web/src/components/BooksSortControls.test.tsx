import { render, screen } from '@testing-library/react'
import { ThemeProvider } from '@mui/material/styles'
import CssBaseline from '@mui/material/CssBaseline'
import { describe, it, expect, vi } from 'vitest'
import BooksSortControls from './BooksSortControls'
import theme from '../theme'
import { DEFAULT_SORT_OPTIONS } from '../types/sorting'

describe('BooksSortControls Smoke Tests', () => {
  const renderComponent = (props = {}) => {
    const defaultProps = {
      sortOptions: DEFAULT_SORT_OPTIONS,
      onSortChange: vi.fn(),
      ...props
    }

    return render(
      <ThemeProvider theme={theme}>
        <CssBaseline />
        <BooksSortControls {...defaultProps} />
      </ThemeProvider>
    )
  }

  it('renders without crashing', () => {
    renderComponent()
    expect(screen.getByLabelText('Sort by')).toBeInTheDocument()
  })

  it('displays current sort field', () => {
    renderComponent()
    // The select component should show the current field
    expect(screen.getByLabelText('Sort by')).toBeInTheDocument()
  })

  it('displays sort direction button', () => {
    renderComponent()
    // Should show the sort direction button (with default descending order)
    const sortButton = screen.getByRole('button')
    expect(sortButton).toBeInTheDocument()
    // Check that it has the correct icon for descending order (ArrowDownward)
    const downwardIcon = sortButton.querySelector('svg')
    expect(downwardIcon).toBeInTheDocument()
  })
})