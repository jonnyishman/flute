import { describe, it, expect, beforeEach } from 'vitest'
import { createStore } from 'jotai'
import { 
  readerSettingsAtom, 
  bookProgressAtom, 
  updateBookProgressAtom,
  userPreferencesAtom 
} from '../atoms'

describe('Jotai Atoms', () => {
  let store: ReturnType<typeof createStore>

  beforeEach(() => {
    store = createStore()
  })

  describe('readerSettingsAtom', () => {
    it('should have default values', () => {
      const settings = store.get(readerSettingsAtom)
      expect(settings.fontSize).toBe(16)
      expect(settings.lineSpacing).toBe(1.6)
    })

    it('should update settings', () => {
      const newSettings = { fontSize: 18, lineSpacing: 1.8 }
      store.set(readerSettingsAtom, newSettings)
      
      const settings = store.get(readerSettingsAtom)
      expect(settings.fontSize).toBe(18)
      expect(settings.lineSpacing).toBe(1.8)
    })
  })

  describe('bookProgressAtom', () => {
    it('should start with empty progress', () => {
      const progress = store.get(bookProgressAtom)
      expect(progress).toEqual({})
    })

    it('should update book progress', () => {
      const bookId = 'test-book-1'
      store.set(updateBookProgressAtom, { bookId, chapter: 5 })
      
      const progress = store.get(bookProgressAtom)
      expect(progress[bookId]).toBeDefined()
      expect(progress[bookId].lastChapter).toBe(5)
      expect(progress[bookId].bookId).toBe(bookId)
    })

    it('should update existing book progress', () => {
      const bookId = 'test-book-1'
      
      // First update
      store.set(updateBookProgressAtom, { bookId, chapter: 3 })
      
      // Second update
      store.set(updateBookProgressAtom, { bookId, chapter: 7, progressRatio: 0.35 })
      
      const progress = store.get(bookProgressAtom)
      expect(progress[bookId].lastChapter).toBe(7)
      expect(progress[bookId].readProgressRatio).toBe(0.35)
    })
  })

  describe('userPreferencesAtom', () => {
    it('should have default values', () => {
      const preferences = store.get(userPreferencesAtom)
      expect(preferences.theme).toBe('auto')
      expect(preferences.preferredPageSize).toBe(12)
      expect(preferences.enableHapticFeedback).toBe(true)
    })

    it('should update preferences', () => {
      const newPreferences = { 
        theme: 'dark' as const, 
        preferredPageSize: 24, 
        enableHapticFeedback: false 
      }
      store.set(userPreferencesAtom, newPreferences)
      
      const preferences = store.get(userPreferencesAtom)
      expect(preferences.theme).toBe('dark')
      expect(preferences.preferredPageSize).toBe(24)
      expect(preferences.enableHapticFeedback).toBe(false)
    })
  })
})