export enum LearningStatus {
  KNOWN = 'known',
  LEARNING = 'learning',
  IGNORE = 'ignore',
}

export enum SortOption {
  TITLE = 'title',
  LAST_READ = 'last_read',
  LEARNING_TERMS = 'learning_terms',
  UNKNOWN_TERMS = 'unknown_terms',
}

export enum SortOrder {
  ASC = 'asc',
  DESC = 'desc',
}

// Health check types
export interface HealthCheckResponse {
  status: string
  message: string
}

// Book types
export interface CreateBookRequest {
  title: string
  language_id: number
  chapters: string[]
  source?: string | null
  cover_art_filepath?: string | null
}

export interface CreateBookResponse {
  book_id: number
}

export interface BookSummariesRequest {
  language_id: number
  sort_option?: SortOption | null
  sort_order?: SortOrder
  page?: number
  per_page?: number
}

export interface BookSummary {
  book_id: number
  title: string
  cover_art_filepath: string | null
  total_terms: number
  known_terms: number
  learning_terms: number
  unknown_terms: number
  last_visited_chapter: number | null
  last_visited_word_index: number | null
  last_read: string | null
}

export interface BookSummariesResponse {
  summaries: BookSummary[]
}

export interface BookCountRequest {
  language_id: number
}

export interface BookCountResponse {
  count: number
}

export interface ChapterCountResponse {
  count: number
}

// Term types
export interface UpdateTermRequest {
  status: LearningStatus
  learning_stage?: number
  display?: string | null
  translation?: string | null
}

export interface CreateTermRequest extends UpdateTermRequest {
  term: string
  language_id: number
}

export interface TermIdResponse {
  term_id: number
}

// Error types
export interface ApiError {
  error: string
  msg: string
}