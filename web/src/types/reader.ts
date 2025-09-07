// Chapter-based structure
export interface Chapter {
  id: number
  chapter_number: number
  title?: string
  content: string
  word_count: number
}

export interface Book {
  id: number
  title: string
  author: string
  description?: string
  cover_image_url?: string
  total_chapters: number
  created_at: string
  chapters?: Chapter[]
}

export interface ReaderSettings {
  fontSize: number // in px, default 16
  lineSpacing: number // multiplier, default 1.5
}

export interface ReadingProgress {
  bookId: string
  currentChapter: number
  totalChapters: number
  scrollPosition: number // For desktop vertical scrolling
  lastReadDate: string
}

// Legacy interfaces for backward compatibility during transition
export interface BookPage {
  pageNumber: number
  content: string
  wordCount: number
}