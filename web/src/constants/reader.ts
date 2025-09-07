// Reader configuration constants

// Touch gesture thresholds
export const SWIPE_THRESHOLD = 50 // pixels
export const SWIPE_MIN_VELOCITY = 0.3 // pixels per ms

// API configuration
export const API_DELAY = 300 // milliseconds

// Font size limits
export const MIN_FONT_SIZE = 12 // pixels
export const MAX_FONT_SIZE = 24 // pixels
export const DEFAULT_FONT_SIZE = 16 // pixels

// Line spacing limits
export const MIN_LINE_SPACING = 1.0
export const MAX_LINE_SPACING = 2.5
export const DEFAULT_LINE_SPACING = 1.5

// Debounce delays
export const SETTINGS_PREVIEW_DEBOUNCE = 200 // milliseconds
export const SCROLL_POSITION_SAVE_DEBOUNCE = 500 // milliseconds

// Keyboard shortcuts
export const KEYBOARD_SHORTCUTS = {
  NEXT_CHAPTER: ['ArrowRight', 'ArrowDown', 'PageDown', 'n'],
  PREVIOUS_CHAPTER: ['ArrowLeft', 'ArrowUp', 'PageUp', 'p'],
  TOGGLE_SETTINGS: ['s', 'S'],
  GO_BACK: ['Escape', 'b', 'B']
} as const

// Breakpoints (should match MUI theme breakpoints)
export const MOBILE_BREAKPOINT = 'md' // Below this is considered mobile

// Storage keys
export const STORAGE_KEYS = {
  READER_SETTINGS: 'flute-reader-settings',
  READING_PROGRESS: (bookId: string) => `flute-progress-${bookId}`
} as const

// Animation durations
export const ANIMATION_DURATION = {
  CHAPTER_TRANSITION: 300, // milliseconds
  SETTINGS_FADE: 200, // milliseconds
  BUTTON_HOVER: 150 // milliseconds
} as const

// Reader layout constants
export const READER_LAYOUT = {
  MAX_CONTENT_WIDTH: 800, // pixels
  CONTENT_PADDING: 24, // pixels
  CONTROL_PANEL_HEIGHT: 64, // pixels
  MOBILE_BUTTON_SIZE: 48, // pixels
  DESKTOP_BUTTON_SIZE: 40 // pixels
} as const