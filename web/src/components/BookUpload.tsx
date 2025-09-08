import React, { useState, useRef } from 'react'
import {
  Box,
  Paper,
  Typography,
  TextField,
  Button,
  Select,
  MenuItem,
  FormControl,
  InputLabel,
  AppBar,
  Toolbar,
  IconButton,
  Fab,
  Dialog,
  DialogTitle,
  DialogContent,
  DialogActions,
  Card,
  CardContent,
  ButtonGroup,
} from '@mui/material'
import {
  ArrowBack,
  CloudUpload,
  ContentPaste,
  Image as ImageIcon,
} from '@mui/icons-material'
import { useNavigate } from 'react-router-dom'

export default function BookUpload() {
  const navigate = useNavigate()
  const fileInputRef = useRef<HTMLInputElement>(null)
  const [formData, setFormData] = useState({
    title: '',
    source: '',
    contents: '',
    renderOption: 'Standard',
  })
  const [coverArt, setCoverArt] = useState<string>('')
  const [showSuccess, setShowSuccess] = useState(false)

  const handleInputChange = (field: string, value: string) => {
    setFormData(prev => ({ ...prev, [field]: value }))
  }

  const handleFileUpload = (event: React.ChangeEvent<HTMLInputElement>) => {
    const file = event.target.files?.[0]
    if (file && file.type.startsWith('image/')) {
      const reader = new FileReader()
      reader.onload = (e) => {
        setCoverArt(e.target?.result as string)
      }
      reader.readAsDataURL(file)
    }
  }

  const handlePasteImage = async () => {
    try {
      const clipboardItems = await navigator.clipboard.read()
      for (const clipboardItem of clipboardItems) {
        for (const type of clipboardItem.types) {
          if (type.startsWith('image/')) {
            const blob = await clipboardItem.getType(type)
            const reader = new FileReader()
            reader.onload = (e) => {
              setCoverArt(e.target?.result as string)
            }
            reader.readAsDataURL(blob)
            return
          }
        }
      }
    } catch (err) {
      // Clipboard API might not be available or permission denied
      console.log('Unable to access clipboard:', err)
    }
  }

  const handleImport = () => {
    // Since this is a prototype, just show success message
    setShowSuccess(true)
  }

  const handleSuccessClose = () => {
    setShowSuccess(false)
    navigate('/')
  }

  return (
    <Box sx={{ flexGrow: 1, minHeight: '100vh', bgcolor: 'background.default' }}>
      <AppBar position="static">
        <Toolbar>
          <IconButton
            edge="start"
            color="inherit"
            onClick={() => navigate('/')}
            sx={{ mr: 2 }}
          >
            <ArrowBack />
          </IconButton>
          <Typography variant="h6" component="div" sx={{ flexGrow: 1 }}>
            Import New Book
          </Typography>
        </Toolbar>
      </AppBar>

      <Box sx={{ p: 3, maxWidth: 800, mx: 'auto' }}>
        <Paper elevation={3} sx={{ p: 4 }}>
          <Typography variant="h4" gutterBottom>
            Add New Book
          </Typography>

          <Box component="form" sx={{ mt: 3 }}>
            {/* Title Field */}
            <TextField
              fullWidth
              label="Book Title"
              value={formData.title}
              onChange={(e) => handleInputChange('title', e.target.value)}
              sx={{ mb: 3 }}
              required
            />

            {/* Source/Author Field */}
            <TextField
              fullWidth
              label="Source/Author (Optional)"
              value={formData.source}
              onChange={(e) => handleInputChange('source', e.target.value)}
              sx={{ mb: 3 }}
            />

            {/* Contents Field */}
            <TextField
              fullWidth
              label="Book Contents"
              multiline
              rows={8}
              value={formData.contents}
              onChange={(e) => handleInputChange('contents', e.target.value)}
              sx={{ mb: 3 }}
              required
            />

            {/* Cover Art Section */}
            <Box sx={{ mb: 3 }}>
              <Typography variant="h6" gutterBottom>
                Cover Art (Optional)
              </Typography>
              
              <ButtonGroup variant="outlined" sx={{ mb: 2 }}>
                <Button
                  startIcon={<CloudUpload />}
                  onClick={() => fileInputRef.current?.click()}
                >
                  Upload Image
                </Button>
                <Button
                  startIcon={<ContentPaste />}
                  onClick={handlePasteImage}
                >
                  Paste Image
                </Button>
              </ButtonGroup>

              <input
                type="file"
                accept="image/*"
                ref={fileInputRef}
                onChange={handleFileUpload}
                style={{ display: 'none' }}
              />

              {coverArt && (
                <Card sx={{ maxWidth: 200, mt: 2 }}>
                  <CardContent>
                    <img
                      src={coverArt}
                      alt="Cover preview"
                      style={{
                        width: '100%',
                        height: 'auto',
                        maxHeight: 250,
                        objectFit: 'contain',
                      }}
                    />
                    <Button
                      size="small"
                      onClick={() => setCoverArt('')}
                      sx={{ mt: 1 }}
                    >
                      Remove
                    </Button>
                  </CardContent>
                </Card>
              )}
            </Box>

            {/* Render Option */}
            <FormControl fullWidth sx={{ mb: 4 }}>
              <InputLabel>Render Option</InputLabel>
              <Select
                value={formData.renderOption}
                label="Render Option"
                onChange={(e) => handleInputChange('renderOption', e.target.value)}
              >
                <MenuItem value="Standard">Standard</MenuItem>
                <MenuItem value="Markdown">Markdown</MenuItem>
                <MenuItem value="HTML">HTML</MenuItem>
              </Select>
            </FormControl>

            {/* Import Button */}
            <Box sx={{ display: 'flex', justifyContent: 'center' }}>
              <Button
                variant="contained"
                size="large"
                onClick={handleImport}
                disabled={!formData.title || !formData.contents}
                sx={{ px: 4 }}
              >
                Import Book
              </Button>
            </Box>
          </Box>
        </Paper>
      </Box>

      {/* Success Dialog */}
      <Dialog open={showSuccess} onClose={handleSuccessClose}>
        <DialogTitle>Success!</DialogTitle>
        <DialogContent>
          <Typography>
            Your book "{formData.title}" has been imported successfully!
          </Typography>
        </DialogContent>
        <DialogActions>
          <Button onClick={handleSuccessClose} variant="contained">
            Continue
          </Button>
        </DialogActions>
      </Dialog>
    </Box>
  )
}