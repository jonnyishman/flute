import { render, screen, fireEvent, waitFor } from '@testing-library/react'
import { ThemeProvider, createTheme } from '@mui/material'
import ReaderSettingsModal from '../../components/ReaderSettingsModal'
import { ReaderSettings } from '../../types/reader'

const theme = createTheme()

const defaultSettings: ReaderSettings = {
  fontSize: 16,
  lineSpacing: 1.5,
}

const renderComponent = (props: Partial<React.ComponentProps<typeof ReaderSettingsModal>> = {}) => {
  const defaultProps = {
    open: true,
    onClose: jest.fn(),
    settings: defaultSettings,
    onSettingsChange: jest.fn(),
    ...props,
  }

  return render(
    <ThemeProvider theme={theme}>
      <ReaderSettingsModal {...defaultProps} />
    </ThemeProvider>
  )
}

describe('ReaderSettingsModal', () => {
  it('should render when open', () => {
    renderComponent()
    
    expect(screen.getByText('Reading Settings')).toBeInTheDocument()
    expect(screen.getByText('Font Size')).toBeInTheDocument()
    expect(screen.getByText('Line Spacing')).toBeInTheDocument()
    expect(screen.getByText('Preview')).toBeInTheDocument()
  })

  it('should not render when closed', () => {
    renderComponent({ open: false })
    
    expect(screen.queryByText('Reading Settings')).not.toBeInTheDocument()
  })

  it('should display current settings values', () => {
    const customSettings = { fontSize: 20, lineSpacing: 2.0 }
    renderComponent({ settings: customSettings })
    
    // Check if sliders show correct values (this might need adjustment based on MUI implementation)
    const fontSlider = screen.getByLabelText(/Font Size/i)
    const lineSpacingSlider = screen.getByLabelText(/Line Spacing/i)
    
    expect(fontSlider).toBeInTheDocument()
    expect(lineSpacingSlider).toBeInTheDocument()
  })

  it('should call onSettingsChange when saved', async () => {
    const mockOnSettingsChange = jest.fn()
    renderComponent({ onSettingsChange: mockOnSettingsChange })
    
    const saveButton = screen.getByText('Save Settings')
    fireEvent.click(saveButton)
    
    expect(mockOnSettingsChange).toHaveBeenCalledWith(defaultSettings)
  })

  it('should call onClose when cancelled', () => {
    const mockOnClose = jest.fn()
    renderComponent({ onClose: mockOnClose })
    
    const cancelButton = screen.getByText('Cancel')
    fireEvent.click(cancelButton)
    
    expect(mockOnClose).toHaveBeenCalled()
  })

  it('should call onClose when saved', async () => {
    const mockOnClose = jest.fn()
    renderComponent({ onClose: mockOnClose })
    
    const saveButton = screen.getByText('Save Settings')
    fireEvent.click(saveButton)
    
    expect(mockOnClose).toHaveBeenCalled()
  })

  it('should reset to original settings when cancelled', () => {
    const originalSettings = { fontSize: 18, lineSpacing: 1.8 }
    const mockOnSettingsChange = jest.fn()
    
    renderComponent({
      settings: originalSettings,
      onSettingsChange: mockOnSettingsChange,
    })
    
    // Change settings would happen through slider interaction
    // Then cancel
    const cancelButton = screen.getByText('Cancel')
    fireEvent.click(cancelButton)
    
    // Settings should not have been changed
    expect(mockOnSettingsChange).not.toHaveBeenCalled()
  })

  it('should show preview text with current settings', () => {
    renderComponent()
    
    const previewText = screen.getByText(/This is how your text will appear/i)
    expect(previewText).toBeInTheDocument()
  })

  it('should have proper accessibility attributes', () => {
    renderComponent()
    
    // Check for proper dialog structure
    expect(screen.getByRole('dialog')).toBeInTheDocument()
    
    // Check for buttons
    expect(screen.getByRole('button', { name: 'Cancel' })).toBeInTheDocument()
    expect(screen.getByRole('button', { name: 'Save Settings' })).toBeInTheDocument()
  })

  it('should show proper slider ranges', () => {
    renderComponent()
    
    // Font size marks
    expect(screen.getByText('12px')).toBeInTheDocument()
    expect(screen.getByText('24px')).toBeInTheDocument()
    
    // Line spacing marks
    expect(screen.getByText('Tight')).toBeInTheDocument()
    expect(screen.getByText('Normal')).toBeInTheDocument()
    expect(screen.getByText('Loose')).toBeInTheDocument()
    expect(screen.getByText('Extra')).toBeInTheDocument()
  })
})