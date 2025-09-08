import { atom } from 'jotai'
import { atomWithStorage } from 'jotai/utils'

// Types for our persistent data
export interface ReaderSettings {
  readonly fontSize: number
  readonly lineSpacing: number
}

export interface BookProgress {
  readonly bookId: string
  readonly lastChapter: number
  readonly lastReadDate: string
  readonly readProgressRatio: number
}

export interface UserPreferences {
  readonly theme: 'light' | 'dark' | 'auto'
  readonly preferredPageSize: number
  readonly enableHapticFeedback: boolean
}

export interface ReadingSession {
  readonly currentBookId: string | null
  readonly currentChapter: number | null
  readonly startTime: string | null
}

// Default values
const defaultReaderSettings: ReaderSettings = {
  fontSize: 16,
  lineSpacing: 1.6,
}

const defaultUserPreferences: UserPreferences = {
  theme: 'auto',
  preferredPageSize: 12,
  enableHapticFeedback: true,
}

const defaultReadingSession: ReadingSession = {
  currentBookId: null,
  currentChapter: null,
  startTime: null,
}

// Persistent storage atoms using atomWithStorage for localStorage integration
export const readerSettingsAtom = atomWithStorage<ReaderSettings>(
  'flute-reader-settings',
  defaultReaderSettings,
  undefined,
  {
    getOnInit: true,
  }
)

export const userPreferencesAtom = atomWithStorage<UserPreferences>(
  'flute-user-preferences',
  defaultUserPreferences,
  undefined,
  {
    getOnInit: true,
  }
)

// Book progress stored as a map of bookId -> BookProgress
export const bookProgressAtom = atomWithStorage<Record<string, BookProgress>>(
  'flute-book-progress',
  {},
  undefined,
  {
    getOnInit: true,
  }
)

// Current reading session (not persisted, only in memory during session)
export const readingSessionAtom = atom<ReadingSession>(defaultReadingSession)

// Derived atoms for easier access
export const currentBookProgressAtom = atom(
  (get) => {
    const session = get(readingSessionAtom)
    const allProgress = get(bookProgressAtom)
    return session.currentBookId ? allProgress[session.currentBookId] : null
  }
)

// Helper atoms for updating book progress
export const updateBookProgressAtom = atom(
  null,
  (get, set, update: { bookId: string; chapter?: number; progressRatio?: number }) => {
    const currentProgress = get(bookProgressAtom)
    const existing = currentProgress[update.bookId] || {
      bookId: update.bookId,
      lastChapter: 1,
      lastReadDate: new Date().toISOString(),
      readProgressRatio: 0,
    }
    
    const updated: BookProgress = {
      ...existing,
      ...(update.chapter !== undefined && { lastChapter: update.chapter }),
      ...(update.progressRatio !== undefined && { readProgressRatio: update.progressRatio }),
      lastReadDate: new Date().toISOString(),
    }
    
    set(bookProgressAtom, {
      ...currentProgress,
      [update.bookId]: updated,
    })
  }
)

// Helper atom for starting a reading session
export const startReadingSessionAtom = atom(
  null,
  (get, set, { bookId, chapter }: { bookId: string; chapter: number }) => {
    set(readingSessionAtom, {
      currentBookId: bookId,
      currentChapter: chapter,
      startTime: new Date().toISOString(),
    })
  }
)

// Helper atom for ending a reading session
export const endReadingSessionAtom = atom(
  null,
  (get, set) => {
    const session = get(readingSessionAtom)
    if (session.currentBookId && session.currentChapter) {
      // Update book progress when ending session
      set(updateBookProgressAtom, {
        bookId: session.currentBookId,
        chapter: session.currentChapter,
      })
    }
    
    set(readingSessionAtom, defaultReadingSession)
  }
)