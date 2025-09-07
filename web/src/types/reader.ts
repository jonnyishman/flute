export interface BookPage {
  pageNumber: number
  content: string
  wordCount: number
}

export interface ReaderSettings {
  fontSize: number // in px, default 16
  lineSpacing: number // multiplier, default 1.5
}

export interface ReadingProgress {
  bookId: string
  currentPage: number
  totalPages: number
  lastReadDate: string
}