/**
 * Chapter count caching utility for reading sessions
 * Caches chapter counts in session storage for the duration of a reading session
 */

const CACHE_PREFIX = 'chapter-count-'

export interface ChapterCountCache {
  count: number
  timestamp: number
}

/**
 * Get cached chapter count for a book
 */
export function getCachedChapterCount(bookId: string): number | null {
  try {
    const cached = sessionStorage.getItem(`${CACHE_PREFIX}${bookId}`)
    if (!cached) return null

    const data: ChapterCountCache = JSON.parse(cached)
    return data.count
  } catch {
    return null
  }
}

/**
 * Cache chapter count for a book
 */
export function setCachedChapterCount(bookId: string, count: number): void {
  try {
    const data: ChapterCountCache = {
      count,
      timestamp: Date.now()
    }
    sessionStorage.setItem(`${CACHE_PREFIX}${bookId}`, JSON.stringify(data))
  } catch {
    // Silently fail if session storage is not available
  }
}

/**
 * Clear cached chapter count for a book
 */
export function clearCachedChapterCount(bookId: string): void {
  try {
    sessionStorage.removeItem(`${CACHE_PREFIX}${bookId}`)
  } catch {
    // Silently fail if session storage is not available
  }
}

/**
 * Clear all cached chapter counts
 */
export function clearAllCachedChapterCounts(): void {
  try {
    const keys = Object.keys(sessionStorage).filter(key => key.startsWith(CACHE_PREFIX))
    keys.forEach(key => sessionStorage.removeItem(key))
  } catch {
    // Silently fail if session storage is not available
  }
}