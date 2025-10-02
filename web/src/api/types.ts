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

// Chapter types
export interface ChapterResponse {
  id: number
  chapter_number: number
  content: string
  word_count: number
}

export interface TermHighlight {
  term_id: number
  display: string
  start_pos: number
  end_pos: number
  status: LearningStatus
  learning_stage: number | null
}

export interface ChapterWithHighlightsResponse {
  chapter: ChapterResponse
  term_highlights: TermHighlight[]
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

// Language types
export interface LanguageSummary {
  id: number
  name: string
  flag_image_filepath: string | null
}

export interface LanguageDetail {
  id: number
  name: string
  flag_image_filepath: string | null
  character_substitutions: string
  regexp_split_sentences: string
  exceptions_split_sentences: string
  word_characters: string
  right_to_left: boolean
  show_romanization: boolean
  parser_type: string
}

export interface LanguageCreate {
  name: string
  flag_image_filepath?: string | null
  character_substitutions?: string
  regexp_split_sentences?: string
  exceptions_split_sentences?: string
  word_characters?: string
  right_to_left?: boolean
  show_romanization?: boolean
  parser_type?: string
}

export interface LanguageUpdate {
  name?: string
  flag_image_filepath?: string | null
  character_substitutions?: string
  regexp_split_sentences?: string
  exceptions_split_sentences?: string
  word_characters?: string
  right_to_left?: boolean
  show_romanization?: boolean
  parser_type?: string
}

export interface LanguageCreateResponse {
  language_id: number
}

export interface LanguageSummariesRequest {
  with_books?: boolean
}

export interface LanguageSummariesResponse {
  languages: LanguageSummary[]
}

// Error types
export interface ApiError {
  error: string
  msg: string
}