export interface Book {
  id: string
  title: string
  coverArt: string
  wordCount: number
  unknownWords: number
  learningWords: number
  knownWords: number
  lastReadDate: string
  readProgressRatio: number // 0-1, representing percentage read
  lastReadChapter?: number
  totalChapters?: number // Optional - only available when viewing individual book
}

export interface BooksPaginationResponse {
  books: Book[]
  nextPage: number | null
}