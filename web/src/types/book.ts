export interface Book {
  id: string
  title: string
  coverArt: string
  wordCount: number
  unknownWords: number
  learningWords: number
  knownWords: number
  lastReadDate: string | null
  readProgressRatio: number // 0-1, representing percentage read
  lastReadChapter?: number
}

export interface BooksPaginationResponse {
  books: Book[]
  nextPage: number | null
}