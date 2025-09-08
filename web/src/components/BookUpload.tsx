import React, { useState, useRef, useCallback } from 'react'
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
  Dialog,
  DialogTitle,
  DialogContent,
  DialogActions,
  Card,
  CardContent,
  ButtonGroup,
  CircularProgress,
  Alert,
} from '@mui/material'
import {
  ArrowBack,
  CloudUpload,
  ContentPaste,
} from '@mui/icons-material'
import { useNavigate } from 'react-router-dom'

// Constants
const RENDER_OPTIONS = ['Standard', 'Markdown', 'HTML'] as const
const MAX_FILE_SIZE = 5 * 1024 * 1024 // 5MB
const ACCEPTED_IMAGE_TYPES = ['image/jpeg', 'image/png', 'image/gif', 'image/webp'] as const
const MAX_IMAGE_DIMENSION = 1200 // pixels

// Types
interface BookFormData {
  title: string
  source: string
  contents: string
  renderOption: typeof RENDER_OPTIONS[number]
}

type LoadingState = {
  fileUpload: boolean
  clipboardPaste: boolean
  imageProcessing: boolean
}

type ErrorState = {
  fileUpload: string | null
  clipboardPaste: string | null
  general: string | null
}

export default function BookUpload() {
  const navigate = useNavigate()
  const fileInputRef = useRef<HTMLInputElement>(null)
  const [formData, setFormData] = useState<BookFormData>({
    title: '',
    source: '',
    contents: '',
    renderOption: 'Standard',
  })
  const [coverArt, setCoverArt] = useState<string>('')
  const [showSuccess, setShowSuccess] = useState(false)
  const [loading, setLoading] = useState<LoadingState>({
    fileUpload: false,
    clipboardPaste: false,
    imageProcessing: false,
  })
  const [errors, setErrors] = useState<ErrorState>({
    fileUpload: null,
    clipboardPaste: null,
    general: null,
  })

  const handleInputChange = useCallback((field: keyof BookFormData, value: string) => {
    setFormData(prev => ({ ...prev, [field]: value }))
    // Clear general errors when user makes changes
    if (errors.general) {
      setErrors(prev => ({ ...prev, general: null }))
    }
  }, [errors.general])

  const processImageFile = useCallback(async (file: File): Promise<string> => {
    return new Promise((resolve, reject) => {
      // Validate file type
      if (!ACCEPTED_IMAGE_TYPES.some(type => file.type === `image/${type.split('/')[1]}`)) {
        reject(new Error(`Unsupported file type. Accepted types: ${ACCEPTED_IMAGE_TYPES.join(', ')}`)) 
        return
      }

      // Validate file size
      if (file.size > MAX_FILE_SIZE) {
        reject(new Error(`File too large. Maximum size: ${Math.round(MAX_FILE_SIZE / (1024 * 1024))}MB`))
        return
      }

      const reader = new FileReader()
      reader.onload = (e) => {
        const result = e.target?.result as string
        if (result) {
          // Create an image element to get dimensions and potentially resize
          const img = new Image()
          img.onload = () => {
            // Check if we need to resize
            if (img.width > MAX_IMAGE_DIMENSION || img.height > MAX_IMAGE_DIMENSION) {
              const canvas = document.createElement('canvas')
              const ctx = canvas.getContext('2d')
              if (!ctx) {
                reject(new Error('Cannot process image'))
                return
              }

              // Calculate new dimensions maintaining aspect ratio
              const ratio = Math.min(MAX_IMAGE_DIMENSION / img.width, MAX_IMAGE_DIMENSION / img.height)
              canvas.width = img.width * ratio
              canvas.height = img.height * ratio

              // Draw resized image
              ctx.drawImage(img, 0, 0, canvas.width, canvas.height)
              const resizedDataUrl = canvas.toDataURL(file.type, 0.8)
              resolve(resizedDataUrl)
            } else {
              resolve(result)
            }
          }
          img.onerror = () => reject(new Error('Invalid image file'))
          img.src = result
        } else {
          reject(new Error('Failed to read file'))
        }
      }
      reader.onerror = () => reject(new Error('Failed to read file'))
      reader.readAsDataURL(file)
    })
  }, [])

  const handleFileUpload = useCallback(async (event: React.ChangeEvent<HTMLInputElement>) => {
    const file = event.target.files?.[0]
    if (!file) return

    setLoading(prev => ({ ...prev, fileUpload: true, imageProcessing: true }))
    setErrors(prev => ({ ...prev, fileUpload: null }))

    try {
      const processedImage = await processImageFile(file)
      setCoverArt(processedImage)
    } catch (error) {
      const errorMessage = error instanceof Error ? error.message : 'Failed to process image'
      setErrors(prev => ({ ...prev, fileUpload: errorMessage }))
    } finally {
      setLoading(prev => ({ ...prev, fileUpload: false, imageProcessing: false }))
      // Clear the input so the same file can be selected again
      if (fileInputRef.current) {
        fileInputRef.current.value = ''
      }
    }
  }, [processImageFile])

  const isClipboardAPISupported = useCallback(() => {
    return (
      typeof navigator !== 'undefined' &&
      'clipboard' in navigator &&
      'read' in navigator.clipboard &&
      window.isSecureContext
    )
  }, [])

  const handlePasteImage = useCallback(async () => {
    if (!isClipboardAPISupported()) {
      setErrors(prev => ({
        ...prev,
        clipboardPaste: 'Clipboard API not supported in this browser or context'
      }))
      return
    }

    setLoading(prev => ({ ...prev, clipboardPaste: true, imageProcessing: true }))
    setErrors(prev => ({ ...prev, clipboardPaste: null }))

    try {
      const clipboardItems = await navigator.clipboard.read()
      let imageFound = false

      for (const clipboardItem of clipboardItems) {
        for (const type of clipboardItem.types) {
          if (type.startsWith('image/')) {
            imageFound = true
            const blob = await clipboardItem.getType(type)
            const file = new File([blob], `pasted-image.${type.split('/')[1]}`, { type })
            
            const processedImage = await processImageFile(file)
            setCoverArt(processedImage)
            return
          }
        }
      }

      if (!imageFound) {
        setErrors(prev => ({ ...prev, clipboardPaste: 'No image found in clipboard' }))
      }
    } catch (error) {
      let errorMessage = 'Failed to paste image from clipboard'
      
      if (error instanceof Error) {
        if (error.name === 'NotAllowedError') {
          errorMessage = 'Clipboard access denied. Please grant permission.'
        } else if (error.name === 'NotFoundError') {
          errorMessage = 'No image found in clipboard'
        } else {
          errorMessage = error.message
        }
      }
      
      setErrors(prev => ({ ...prev, clipboardPaste: errorMessage }))
    } finally {
      setLoading(prev => ({ ...prev, clipboardPaste: false, imageProcessing: false }))
    }
  }, [isClipboardAPISupported, processImageFile])

  const handleImport = useCallback(() => {
    // Basic validation
    if (!formData.title.trim()) {
      setErrors(prev => ({ ...prev, general: 'Title is required' }))
      return
    }
    if (!formData.contents.trim()) {
      setErrors(prev => ({ ...prev, general: 'Contents are required' }))
      return
    }

    // Since this is a prototype, just show success message
    setShowSuccess(true)
  }, [formData.title, formData.contents])

  const handleSuccessClose = useCallback(() => {
    setShowSuccess(false)
    navigate('/')
  }, [navigate])

  const clearError = useCallback((errorType: keyof ErrorState) => {
    setErrors(prev => ({ ...prev, [errorType]: null }))
  }, [])

  const isFormValid = formData.title.trim() && formData.contents.trim()

  return (
    <Box sx={{ flexGrow: 1, minHeight: '100vh', bgcolor: 'background.default' }}>
      <AppBar position="static">
        <Toolbar>
          <IconButton
            edge="start"
            color="inherit"
            onClick={() => navigate('/')}
            sx={{ mr: 2 }}
            aria-label="Go back to home"
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
              inputProps={{
                'aria-describedby': 'title-helper-text',
              }}
              helperText="Enter the title of the book"
              id="title-helper-text"
            />

            {/* Source/Author Field */}
            <TextField
              fullWidth
              label="Source/Author (Optional)"
              value={formData.source}
              onChange={(e) => handleInputChange('source', e.target.value)}
              sx={{ mb: 3 }}
              inputProps={{
                'aria-describedby': 'source-helper-text',
              }}
              helperText="Enter the author or source of the book"
              id="source-helper-text"
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
              inputProps={{
                'aria-describedby': 'contents-helper-text',
              }}
              helperText="Enter the full text content of the book"
              id="contents-helper-text"
            />

            {/* Cover Art Section */}
            <Box sx={{ mb: 3 }}>
              <Typography variant="h6" gutterBottom>
                Cover Art (Optional)
              </Typography>
              
              <ButtonGroup variant="outlined" sx={{ mb: 2 }}>
                <Button
                  startIcon={loading.fileUpload ? <CircularProgress size={16} /> : <CloudUpload />}
                  onClick={() => fileInputRef.current?.click()}
                  disabled={loading.fileUpload || loading.imageProcessing}
                  aria-label="Upload image file from computer"
                >
                  {loading.fileUpload ? 'Uploading...' : 'Upload Image'}
                </Button>
                <Button
                  startIcon={loading.clipboardPaste ? <CircularProgress size={16} /> : <ContentPaste />}
                  onClick={handlePasteImage}
                  disabled={loading.clipboardPaste || loading.imageProcessing || !isClipboardAPISupported()}
                  aria-label="Paste image from clipboard"
                  title={!isClipboardAPISupported() ? 'Clipboard API not supported in this browser' : ''}
                >
                  {loading.clipboardPaste ? 'Pasting...' : 'Paste Image'}
                </Button>
              </ButtonGroup>

              {/* Error Messages */}
              {errors.fileUpload && (
                <Alert 
                  severity="error" 
                  sx={{ mb: 2 }} 
                  onClose={() => clearError('fileUpload')}
                >
                  {errors.fileUpload}
                </Alert>
              )}
              {errors.clipboardPaste && (
                <Alert 
                  severity="error" 
                  sx={{ mb: 2 }}
                  onClose={() => clearError('clipboardPaste')}
                >
                  {errors.clipboardPaste}
                </Alert>
              )}

              <input
                type="file"
                accept={ACCEPTED_IMAGE_TYPES.map(type => `image/${type.split('/')[1]}`).join(',')}
                ref={fileInputRef}
                onChange={handleFileUpload}
                style={{ display: 'none' }}
                aria-label="File input for cover art"
              />

              {loading.imageProcessing && (
                <Box sx={{ display: 'flex', alignItems: 'center', mt: 2, mb: 2 }}>
                  <CircularProgress size={24} sx={{ mr: 2 }} />
                  <Typography variant="body2" color="text.secondary">
                    Processing image...
                  </Typography>
                </Box>
              )}

              {coverArt && !loading.imageProcessing && (
                <Card sx={{ maxWidth: 200, mt: 2 }}>
                  <CardContent>
                    <img
                      src={coverArt}
                      alt="Cover art preview - will be used as book cover"
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
                      aria-label="Remove cover art image"
                    >
                      Remove
                    </Button>
                  </CardContent>
                </Card>
              )}
            </Box>

            {/* Render Option */}
            <FormControl fullWidth sx={{ mb: 4 }}>
              <InputLabel id="render-option-label">Render Option</InputLabel>
              <Select
                value={formData.renderOption}
                label="Render Option"
                onChange={(e) => handleInputChange('renderOption', e.target.value as typeof RENDER_OPTIONS[number])}
                labelId="render-option-label"
                aria-describedby="render-option-helper-text"
              >
                {RENDER_OPTIONS.map((option) => (
                  <MenuItem key={option} value={option}>
                    {option}
                  </MenuItem>
                ))}
              </Select>
              <Typography variant="caption" color="text.secondary" id="render-option-helper-text">
                Choose how the book content should be rendered
              </Typography>
            </FormControl>

            {/* General Error */}
            {errors.general && (
              <Alert 
                severity="error" 
                sx={{ mb: 3 }}
                onClose={() => clearError('general')}
              >
                {errors.general}
              </Alert>
            )}

            {/* Import Button */}
            <Box sx={{ display: 'flex', justifyContent: 'center' }}>
              <Button
                variant="contained"
                size="large"
                onClick={handleImport}
                disabled={!isFormValid}
                sx={{ px: 4 }}
                aria-label="Import the book with entered details"
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