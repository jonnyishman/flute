import { useState, useEffect } from 'react'
import {
  Dialog,
  DialogTitle,
  DialogContent,
  DialogActions,
  Button,
  Typography,
  Box,
  Slider,
  Divider,
} from '@mui/material'
import { ReaderSettings } from '../types/reader'
import { useDebounce } from '../hooks/useDebounce'
import { SETTINGS_PREVIEW_DEBOUNCE, MIN_FONT_SIZE, MAX_FONT_SIZE, MIN_LINE_SPACING, MAX_LINE_SPACING } from '../constants/reader'

interface ReaderSettingsModalProps {
  open: boolean
  onClose: () => void
  settings: ReaderSettings
  onSettingsChange: (settings: ReaderSettings) => void
}

const ReaderSettingsModal = ({ open, onClose, settings, onSettingsChange }: ReaderSettingsModalProps) => {
  const [tempSettings, setTempSettings] = useState<ReaderSettings>(settings)
  
  // Debounce the preview settings to prevent excessive re-renders
  const debouncedPreviewSettings = useDebounce(tempSettings, SETTINGS_PREVIEW_DEBOUNCE)

  useEffect(() => {
    setTempSettings(settings)
  }, [settings])

  const handleSave = () => {
    onSettingsChange(tempSettings)
    onClose()
  }

  const handleCancel = () => {
    setTempSettings(settings)
    onClose()
  }

  const handleFontSizeChange = (_: Event, newValue: number | number[]) => {
    setTempSettings({
      ...tempSettings,
      fontSize: newValue as number
    })
  }

  const handleLineSpacingChange = (_: Event, newValue: number | number[]) => {
    setTempSettings({
      ...tempSettings,
      lineSpacing: newValue as number
    })
  }

  return (
    <Dialog open={open} onClose={handleCancel} maxWidth="sm" fullWidth>
      <DialogTitle>
        Reading Settings
      </DialogTitle>
      
      <DialogContent>
        <Box sx={{ py: 2 }}>
          {/* Font Size */}
          <Typography gutterBottom variant="subtitle1" fontWeight="medium">
            Font Size
          </Typography>
          <Typography variant="body2" color="text.secondary" gutterBottom>
            Adjust the text size for comfortable reading
          </Typography>
          <Box sx={{ px: 2, mb: 3 }}>
            <Slider
              value={tempSettings.fontSize}
              onChange={handleFontSizeChange}
              min={MIN_FONT_SIZE}
              max={MAX_FONT_SIZE}
              step={1}
              marks={[
                { value: MIN_FONT_SIZE, label: `${MIN_FONT_SIZE}px` },
                { value: 16, label: '16px' },
                { value: 20, label: '20px' },
                { value: MAX_FONT_SIZE, label: `${MAX_FONT_SIZE}px` },
              ]}
              valueLabelDisplay="auto"
              valueLabelFormat={(value) => `${value}px`}
            />
          </Box>

          <Divider sx={{ my: 3 }} />

          {/* Line Spacing */}
          <Typography gutterBottom variant="subtitle1" fontWeight="medium">
            Line Spacing
          </Typography>
          <Typography variant="body2" color="text.secondary" gutterBottom>
            Adjust the space between lines of text
          </Typography>
          <Box sx={{ px: 2 }}>
            <Slider
              value={tempSettings.lineSpacing}
              onChange={handleLineSpacingChange}
              min={MIN_LINE_SPACING}
              max={MAX_LINE_SPACING}
              step={0.1}
              marks={[
                { value: MIN_LINE_SPACING, label: 'Tight' },
                { value: 1.5, label: 'Normal' },
                { value: 2.0, label: 'Loose' },
                { value: MAX_LINE_SPACING, label: 'Extra' },
              ]}
              valueLabelDisplay="auto"
              valueLabelFormat={(value) => `${value}x`}
            />
          </Box>

          {/* Preview */}
          <Box sx={{ mt: 4, p: 2, border: 1, borderColor: 'divider', borderRadius: 1 }}>
            <Typography variant="caption" color="text.secondary" gutterBottom>
              Preview
            </Typography>
            <Typography 
              sx={{ 
                fontSize: `${debouncedPreviewSettings.fontSize}px`,
                lineHeight: debouncedPreviewSettings.lineSpacing,
                mt: 1
              }}
            >
              This is how your text will appear with the current settings. You can adjust the font size and line spacing to make reading more comfortable for your eyes.
            </Typography>
          </Box>
        </Box>
      </DialogContent>

      <DialogActions>
        <Button onClick={handleCancel} color="inherit">
          Cancel
        </Button>
        <Button onClick={handleSave} variant="contained">
          Save Settings
        </Button>
      </DialogActions>
    </Dialog>
  )
}

export default ReaderSettingsModal