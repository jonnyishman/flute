import { renderHook, act } from '@testing-library/react'
import { usePersistedState, useReaderSettings, useReadingProgress } from '../../hooks/usePersistedState'

// Mock localStorage
const localStorageMock = (() => {
  let store: Record<string, string> = {}

  return {
    getItem: (key: string) => store[key] || null,
    setItem: (key: string, value: string) => {
      store[key] = value
    },
    removeItem: (key: string) => {
      delete store[key]
    },
    clear: () => {
      store = {}
    },
  }
})()

Object.defineProperty(window, 'localStorage', {
  value: localStorageMock,
})

describe('usePersistedState', () => {
  beforeEach(() => {
    localStorageMock.clear()
  })

  it('should initialize with default value when localStorage is empty', () => {
    const { result } = renderHook(() => usePersistedState('test-key', 'default'))
    
    expect(result.current[0]).toBe('default')
  })

  it('should initialize with stored value when localStorage has data', () => {
    localStorageMock.setItem('test-key', JSON.stringify('stored-value'))
    
    const { result } = renderHook(() => usePersistedState('test-key', 'default'))
    
    expect(result.current[0]).toBe('stored-value')
  })

  it('should update localStorage when state changes', () => {
    const { result } = renderHook(() => usePersistedState('test-key', 'default'))
    
    act(() => {
      result.current[1]('new-value')
    })
    
    expect(result.current[0]).toBe('new-value')
    expect(JSON.parse(localStorageMock.getItem('test-key')!)).toBe('new-value')
  })

  it('should handle function updates', () => {
    const { result } = renderHook(() => usePersistedState('test-key', 10))
    
    act(() => {
      result.current[1](prev => prev + 5)
    })
    
    expect(result.current[0]).toBe(15)
  })

  it('should use default value when stored value is invalid JSON', () => {
    localStorageMock.setItem('test-key', 'invalid-json')
    
    const { result } = renderHook(() => usePersistedState('test-key', 'default'))
    
    expect(result.current[0]).toBe('default')
  })

  it('should validate stored value when validator is provided', () => {
    const validator = (value: any): value is string => typeof value === 'string'
    localStorageMock.setItem('test-key', JSON.stringify(123)) // Invalid type
    
    const { result } = renderHook(() => 
      usePersistedState('test-key', 'default', validator)
    )
    
    expect(result.current[0]).toBe('default')
  })
})

describe('useReaderSettings', () => {
  beforeEach(() => {
    localStorageMock.clear()
  })

  it('should initialize with default settings', () => {
    const { result } = renderHook(() => useReaderSettings())
    
    expect(result.current[0]).toEqual({
      fontSize: 16,
      lineSpacing: 1.5
    })
  })

  it('should reject invalid font size', () => {
    localStorageMock.setItem('flute-reader-settings', JSON.stringify({
      fontSize: 100, // Invalid
      lineSpacing: 1.5
    }))
    
    const { result } = renderHook(() => useReaderSettings())
    
    expect(result.current[0]).toEqual({
      fontSize: 16,
      lineSpacing: 1.5
    })
  })

  it('should accept valid settings', () => {
    const validSettings = { fontSize: 20, lineSpacing: 2.0 }
    localStorageMock.setItem('flute-reader-settings', JSON.stringify(validSettings))
    
    const { result } = renderHook(() => useReaderSettings())
    
    expect(result.current[0]).toEqual(validSettings)
  })
})

describe('useReadingProgress', () => {
  beforeEach(() => {
    localStorageMock.clear()
  })

  it('should initialize with default progress', () => {
    const { result } = renderHook(() => useReadingProgress('book-1'))
    
    expect(result.current[0]).toMatchObject({
      currentChapter: 1,
      scrollPosition: 0
    })
    expect(result.current[0].lastReadDate).toBeTruthy()
  })

  it('should load stored progress', () => {
    const progress = {
      currentChapter: 3,
      scrollPosition: 500,
      lastReadDate: '2023-01-01T00:00:00.000Z'
    }
    localStorageMock.setItem('flute-progress-book-1', JSON.stringify(progress))
    
    const { result } = renderHook(() => useReadingProgress('book-1'))
    
    expect(result.current[0]).toEqual(progress)
  })

  it('should reject invalid progress data', () => {
    localStorageMock.setItem('flute-progress-book-1', JSON.stringify({
      currentChapter: -1, // Invalid
      scrollPosition: 100,
      lastReadDate: '2023-01-01T00:00:00.000Z'
    }))
    
    const { result } = renderHook(() => useReadingProgress('book-1'))
    
    expect(result.current[0].currentChapter).toBe(1)
  })
})