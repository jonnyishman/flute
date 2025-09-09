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
  totalChapters: number
  lastReadChapter?: number
}

export interface BooksPaginationResponse {
  books: Book[]
  hasMore: boolean
  nextPage: number | null
  totalCount: number
}