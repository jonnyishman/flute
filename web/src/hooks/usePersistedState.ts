import { useState, useEffect, useCallback } from 'react'

// Validation function type
type ValidationFn<T> = (value: any) => value is T

// Helper function to safely parse JSON with validation
const safeParseJson = <T>(
  value: string | null, 
  defaultValue: T, 
  validate?: ValidationFn<T>
): T => {
  if (!value) return defaultValue
  
  try {
    const parsed = JSON.parse(value)
    
    // If validation function provided, use it to check the parsed value
    if (validate && !validate(parsed)) {
      console.warn('Persisted state validation failed, using default value')
      return defaultValue
    }
    
    return parsed
  } catch (error) {
    console.error('Failed to parse persisted state:', error)
    return defaultValue
  }
}

// Custom hook for persisted state with localStorage
export const usePersistedState = <T>(
  key: string, 
  defaultValue: T, 
  validate?: ValidationFn<T>
): [T, (value: T | ((prev: T) => T)) => void] => {
  // Initialize state from localStorage or default value
  const [state, setState] = useState<T>(() => {
    const storedValue = localStorage.getItem(key)
    return safeParseJson(storedValue, defaultValue, validate)
  })

  // Update localStorage when state changes
  useEffect(() => {
    try {
      localStorage.setItem(key, JSON.stringify(state))
    } catch (error) {
      console.error('Failed to persist state to localStorage:', error)
    }
  }, [key, state])

  // Wrapper function to handle both direct values and updater functions
  const setPersistedState = useCallback((value: T | ((prev: T) => T)) => {
    setState(prevState => {
      const newValue = typeof value === 'function' 
        ? (value as (prev: T) => T)(prevState)
        : value
      
      // Validate the new value if validator is provided
      if (validate && !validate(newValue)) {
        console.warn('New state value failed validation, keeping previous value')
        return prevState
      }
      
      return newValue
    })
  }, [validate])

  return [state, setPersistedState]
}

// Specialized hook for reader settings with validation
export const useReaderSettings = () => {
  const validateSettings = (value: any): value is { fontSize: number; lineSpacing: number } => {
    return (
      typeof value === 'object' &&
      value !== null &&
      typeof value.fontSize === 'number' &&
      typeof value.lineSpacing === 'number' &&
      value.fontSize >= 12 &&
      value.fontSize <= 24 &&
      value.lineSpacing >= 1.0 &&
      value.lineSpacing <= 2.5
    )
  }

  return usePersistedState(
    'flute-reader-settings',
    { fontSize: 16, lineSpacing: 1.5 },
    validateSettings
  )
}

// Specialized hook for reading progress with validation
export const useReadingProgress = (bookId: string) => {
  const validateProgress = (value: any): value is { 
    currentChapter: number; 
    scrollPosition: number; 
    lastReadDate: string 
  } => {
    return (
      typeof value === 'object' &&
      value !== null &&
      typeof value.currentChapter === 'number' &&
      typeof value.scrollPosition === 'number' &&
      typeof value.lastReadDate === 'string' &&
      value.currentChapter >= 1 &&
      value.scrollPosition >= 0
    )
  }

  return usePersistedState(
    `flute-progress-${bookId}`,
    { currentChapter: 1, scrollPosition: 0, lastReadDate: new Date().toISOString() },
    validateProgress
  )
}