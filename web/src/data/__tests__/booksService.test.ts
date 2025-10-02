import { describe, it, expect } from 'vitest'
import { transformBookSummary } from '../booksService'
import type { BookSummary } from '../../api/types'

describe('transformBookSummary', () => {
  it('should transform a complete BookSummary with all fields populated', () => {
    const summary: BookSummary = {
      book_id: 123,
      title: 'Test Book',
      cover_art_filepath: 'covers/test.jpg',
      total_terms: 1000,
      known_terms: 600,
      learning_terms: 200,
      unknown_terms: 200,
      last_visited_chapter: 5,
      last_visited_word_index: 150,
      last_read: '2025-09-15T10:30:00Z',
    }

    const result = transformBookSummary(summary)

    expect(result).toEqual({
      id: '123',
      title: 'Test Book',
      coverArt: '/api/images/covers/test.jpg',
      wordCount: 1000,
      unknownWords: 200,
      learningWords: 200,
      knownWords: 600,
      lastReadDate: '2025-09-15T10:30:00Z',
      readProgressRatio: 0.6,
      lastReadChapter: 5,
    })
  })

  it('should handle null last_read with empty string', () => {
    const summary: BookSummary = {
      book_id: 456,
      title: 'Never Read Book',
      cover_art_filepath: 'covers/test.jpg',
      total_terms: 500,
      known_terms: 0,
      learning_terms: 0,
      unknown_terms: 500,
      last_visited_chapter: null,
      last_visited_word_index: null,
      last_read: null,
    }

    const result = transformBookSummary(summary)

    expect(result.lastReadDate).toBe('')
  })

  it('should handle null last_visited_chapter with undefined', () => {
    const summary: BookSummary = {
      book_id: 789,
      title: 'Another Book',
      cover_art_filepath: 'covers/test.jpg',
      total_terms: 300,
      known_terms: 100,
      learning_terms: 50,
      unknown_terms: 150,
      last_visited_chapter: null,
      last_visited_word_index: null,
      last_read: '2025-09-20T14:00:00Z',
    }

    const result = transformBookSummary(summary)

    expect(result.lastReadChapter).toBeUndefined()
  })

  it('should use placeholder cover art when cover_art_filepath is null', () => {
    const summary: BookSummary = {
      book_id: 999,
      title: 'No Cover Book',
      cover_art_filepath: null,
      total_terms: 200,
      known_terms: 50,
      learning_terms: 25,
      unknown_terms: 125,
      last_visited_chapter: 3,
      last_visited_word_index: 100,
      last_read: '2025-09-25T09:15:00Z',
    }

    const result = transformBookSummary(summary)

    expect(result.coverArt).toBe('https://picsum.photos/300/400?random=999')
  })

  it('should calculate readProgressRatio correctly', () => {
    const summary: BookSummary = {
      book_id: 111,
      title: 'Progress Book',
      cover_art_filepath: 'covers/test.jpg',
      total_terms: 1000,
      known_terms: 750,
      learning_terms: 150,
      unknown_terms: 100,
      last_visited_chapter: 8,
      last_visited_word_index: 500,
      last_read: '2025-09-30T16:45:00Z',
    }

    const result = transformBookSummary(summary)

    expect(result.readProgressRatio).toBe(0.75)
  })

  it('should handle zero total_terms gracefully', () => {
    const summary: BookSummary = {
      book_id: 222,
      title: 'Empty Book',
      cover_art_filepath: 'covers/test.jpg',
      total_terms: 0,
      known_terms: 0,
      learning_terms: 0,
      unknown_terms: 0,
      last_visited_chapter: null,
      last_visited_word_index: null,
      last_read: null,
    }

    const result = transformBookSummary(summary)

    expect(result.readProgressRatio).toBe(0)
  })

  it('should convert book_id to string', () => {
    const summary: BookSummary = {
      book_id: 12345,
      title: 'ID Test Book',
      cover_art_filepath: 'covers/test.jpg',
      total_terms: 100,
      known_terms: 50,
      learning_terms: 25,
      unknown_terms: 25,
      last_visited_chapter: 1,
      last_visited_word_index: 10,
      last_read: '2025-10-01T08:00:00Z',
    }

    const result = transformBookSummary(summary)

    expect(result.id).toBe('12345')
    expect(typeof result.id).toBe('string')
  })
})
