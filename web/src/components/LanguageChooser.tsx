import { useState, useEffect } from 'react'
import {
  IconButton,
  Menu,
  MenuItem,
  Typography,
  ListItemIcon,
  ListItemText,
  Divider,
  CircularProgress,
  Alert,
} from '@mui/material'
import {
  Language as LanguageIcon,
  Add as AddIcon,
} from '@mui/icons-material'
import { useAtom } from 'jotai'
import { selectedLanguageAtom } from '../store/atoms'
import { api } from '../api'
import { LanguageSummary } from '../api/types'

const LanguageChooser = () => {
  const [selectedLanguage, setSelectedLanguage] = useAtom(selectedLanguageAtom)
  const [anchorEl, setAnchorEl] = useState<null | HTMLElement>(null)
  const [languages, setLanguages] = useState<LanguageSummary[]>([])
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState<string | null>(null)
  const [imageErrors, setImageErrors] = useState<Set<string>>(new Set())

  const open = Boolean(anchorEl)

  const handleImageError = (filepath: string) => {
    setImageErrors(prev => new Set(prev).add(filepath))
  }

  // Load languages on mount only
  useEffect(() => {
    // Skip if already loaded
    if (languages.length > 0) return

    let isCancelled = false

    const fetchLanguages = async () => {
      if (isCancelled) return

      setLoading(true)
      setError(null)
      try {
        const response = await api.languages.getSummaries({ with_books: true })

        if (isCancelled) return

        setLanguages(response.languages)

        // Auto-select first language if none selected
        if (!selectedLanguage && response.languages.length > 0) {
          setSelectedLanguage(response.languages[0])
        }
      } catch (err) {
        if (isCancelled) return

        setError('Failed to load languages')
        console.error('Error loading languages:', err)
      } finally {
        if (!isCancelled) {
          setLoading(false)
        }
      }
    }

    fetchLanguages()

    return () => {
      isCancelled = true
    }
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, []) // Only run on mount

  const handleClick = (event: React.MouseEvent<HTMLElement>) => {
    setAnchorEl(event.currentTarget)
  }

  const handleClose = () => {
    setAnchorEl(null)
  }

  const handleLanguageSelect = (language: LanguageSummary) => {
    setSelectedLanguage(language)
    handleClose()
  }

  const handleAddLanguage = () => {
    // TODO: Implement add language functionality
    console.log('Add new language clicked')
    handleClose()
  }

  const renderLanguageDisplay = (language: LanguageSummary) => {
    if (language.flag_image_filepath && !imageErrors.has(language.flag_image_filepath)) {
      return (
        <img
          src={language.flag_image_filepath}
          alt={`${language.name} flag`}
          style={{
            width: 24,
            height: 16,
            objectFit: 'cover',
            borderRadius: 2,
          }}
          onError={() => handleImageError(language.flag_image_filepath!)}
        />
      )
    }
    return (
      <Typography variant="body2" color="inherit">
        {language.name}
      </Typography>
    )
  }

  if (error) {
    return (
      <Alert severity="error" sx={{ minWidth: 200 }}>
        {error}
      </Alert>
    )
  }

  return (
    <>
      <IconButton
        onClick={handleClick}
        size="small"
        sx={{ ml: 1 }}
        aria-controls={open ? 'language-menu' : undefined}
        aria-haspopup="true"
        aria-expanded={open ? 'true' : undefined}
        disabled={loading}
      >
        {loading ? (
          <CircularProgress size={24} color="inherit" />
        ) : selectedLanguage ? (
          renderLanguageDisplay(selectedLanguage)
        ) : (
          <LanguageIcon />
        )}
      </IconButton>

      <Menu
        id="language-menu"
        anchorEl={anchorEl}
        open={open}
        onClose={handleClose}
        MenuListProps={{
          'aria-labelledby': 'language-button',
        }}
        transformOrigin={{ horizontal: 'right', vertical: 'top' }}
        anchorOrigin={{ horizontal: 'right', vertical: 'bottom' }}
      >
        {languages.map((language) => (
          <MenuItem
            key={language.id}
            onClick={() => handleLanguageSelect(language)}
            selected={selectedLanguage?.id === language.id}
          >
            <ListItemIcon sx={{ minWidth: 40 }}>
              {language.flag_image_filepath && !imageErrors.has(language.flag_image_filepath) ? (
                <img
                  src={language.flag_image_filepath}
                  alt={`${language.name} flag`}
                  style={{
                    width: 24,
                    height: 16,
                    objectFit: 'cover',
                    borderRadius: 2,
                  }}
                  onError={() => handleImageError(language.flag_image_filepath!)}
                />
              ) : (
                <LanguageIcon />
              )}
            </ListItemIcon>
            <ListItemText primary={language.name} />
          </MenuItem>
        ))}

        {languages.length > 0 && (
          <Divider />
        )}

        <MenuItem onClick={handleAddLanguage}>
          <ListItemIcon>
            <AddIcon />
          </ListItemIcon>
          <ListItemText primary="Add new language" />
        </MenuItem>
      </Menu>
    </>
  )
}

export default LanguageChooser