import React from 'react'
import {
  Card,
  CardContent,
  CardMedia,
  Typography,
  Box,
  LinearProgress,
  Chip,
  Avatar,
  Stack,
  IconButton,
  Menu,
  MenuItem,
  ListItemIcon,
  ListItemText,
} from '@mui/material'
import {
  Schedule,
  Book as BookIcon,
  MoreVert,
  Edit,
  Archive,
  Delete,
} from '@mui/icons-material'
import { Book } from '../types/book'

interface BookTileProps {
  book: Book
  onClick?: (book: Book) => void
}

const BookTile = ({ book, onClick }: BookTileProps) => {
  const [anchorEl, setAnchorEl] = React.useState<null | HTMLElement>(null)
  const menuOpen = Boolean(anchorEl)

  const handleMenuOpen = (event: React.MouseEvent<HTMLButtonElement>) => {
    event.stopPropagation()
    setAnchorEl(event.currentTarget)
  }

  const handleMenuClose = () => {
    setAnchorEl(null)
  }

  const handleMenuItemClick = (_action: string) => {
    handleMenuClose()
  }
  const formatNumber = (num: number): string => {
    if (num >= 1000) {
      return `${(num / 1000).toFixed(1)}k`
    }
    return num.toString()
  }

  const formatDate = (dateString: string): string => {
    const date = new Date(dateString)
    const now = new Date()
    const diffTime = Math.abs(now.getTime() - date.getTime())
    const diffDays = Math.floor(diffTime / (1000 * 60 * 60 * 24))
    
    if (diffDays === 0) {
      return 'Today'
    } else if (diffDays === 1) {
      return 'Yesterday'
    } else if (diffDays < 7) {
      return `${diffDays} days ago`
    } else if (diffDays < 30) {
      const weeks = Math.floor(diffDays / 7)
      return `${weeks} week${weeks > 1 ? 's' : ''} ago`
    } else {
      return date.toLocaleDateString()
    }
  }

  const progressPercentage = Math.round(book.readProgressRatio * 100)

  return (
    <Card
      sx={{
        height: '100%',
        display: 'flex',
        flexDirection: 'column',
        transition: 'transform 0.2s, box-shadow 0.2s',
        cursor: onClick ? 'pointer' : 'default',
        position: 'relative',
        '&:hover': {
          transform: 'translateY(-4px)',
          boxShadow: 4,
        },
      }}
      onClick={() => onClick?.(book)}
    >
      <CardMedia
        component="img"
        height="200"
        image={book.coverArt}
        alt={book.title}
        sx={{
          objectFit: 'cover',
        }}
      />
      
      <CardContent sx={{ flexGrow: 1, pb: 2 }}>
        <Typography
          variant="h6"
          component="h2"
          gutterBottom
          sx={{
            fontWeight: 'bold',
            overflow: 'hidden',
            textOverflow: 'ellipsis',
            display: '-webkit-box',
            WebkitLineClamp: 2,
            WebkitBoxOrient: 'vertical',
            minHeight: '3em',
          }}
        >
          {book.title}
        </Typography>

        {/* Progress Section */}
        <Box sx={{ mb: 2 }}>
          <Box display="flex" justifyContent="space-between" alignItems="center" mb={1}>
            <Typography variant="body2" color="text.secondary">
              Progress
            </Typography>
            <Typography variant="body2" fontWeight="medium">
              {progressPercentage}%
            </Typography>
          </Box>
          <LinearProgress
            variant="determinate"
            value={progressPercentage}
            sx={{
              height: 6,
              borderRadius: 3,
              '& .MuiLinearProgress-bar': {
                borderRadius: 3,
              },
            }}
          />
        </Box>

        {/* Word Count */}
        <Box display="flex" alignItems="center" gap={1} mb={2}>
          <Avatar sx={{ width: 24, height: 24, bgcolor: 'primary.main' }}>
            <BookIcon sx={{ fontSize: 14 }} />
          </Avatar>
          <Typography variant="body2" color="text.secondary">
            {formatNumber(book.wordCount)} words
          </Typography>
        </Box>

        {/* Learning Stats */}
        <Stack direction="row" spacing={1} mb={2} flexWrap="wrap" gap={0.5}>
          <Chip
            label={`${formatNumber(book.knownWords)} known`}
            size="small"
            color="success"
            variant="outlined"
          />
          <Chip
            label={`${formatNumber(book.learningWords)} learning`}
            size="small"
            color="warning"
            variant="outlined"
          />
          <Chip
            label={`${formatNumber(book.unknownWords)} unknown`}
            size="small"
            color="error"
            variant="outlined"
          />
        </Stack>

        {/* Last Read */}
        <Box display="flex" alignItems="center" gap={1}>
          <Schedule sx={{ fontSize: 16, color: 'text.secondary' }} />
          <Typography variant="body2" color="text.secondary">
            Last read: {formatDate(book.lastReadDate)}
          </Typography>
        </Box>
      </CardContent>
      
      {/* Options Menu Button */}
      <IconButton
        aria-label="book options"
        onClick={handleMenuOpen}
        sx={{
          position: 'absolute',
          bottom: 8,
          right: 8,
          backgroundColor: 'rgba(255, 255, 255, 0.9)',
          backdropFilter: 'blur(4px)',
          '&:hover': {
            backgroundColor: 'rgba(255, 255, 255, 1)',
          },
          minWidth: 44,
          minHeight: 44,
        }}
      >
        <MoreVert />
      </IconButton>

      {/* Options Menu */}
      <Menu
        anchorEl={anchorEl}
        open={menuOpen}
        onClose={handleMenuClose}
        anchorOrigin={{
          vertical: 'top',
          horizontal: 'left',
        }}
        transformOrigin={{
          vertical: 'bottom',
          horizontal: 'left',
        }}
      >
        <MenuItem onClick={() => handleMenuItemClick('edit')}>
          <ListItemIcon>
            <Edit fontSize="small" />
          </ListItemIcon>
          <ListItemText>Edit</ListItemText>
        </MenuItem>
        <MenuItem onClick={() => handleMenuItemClick('archive')}>
          <ListItemIcon>
            <Archive fontSize="small" />
          </ListItemIcon>
          <ListItemText>Archive</ListItemText>
        </MenuItem>
        <MenuItem onClick={() => handleMenuItemClick('delete')}>
          <ListItemIcon>
            <Delete fontSize="small" />
          </ListItemIcon>
          <ListItemText>Delete</ListItemText>
        </MenuItem>
      </Menu>
    </Card>
  )
}

export default BookTile