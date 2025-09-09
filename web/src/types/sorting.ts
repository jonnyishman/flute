export type SortField = 'lastRead' | 'alphabetical' | 'wordCount' | 'unknownWords' | 'learningWords'
export type SortOrder = 'asc' | 'desc'

export interface SortOptions {
  field: SortField
  order: SortOrder
}

export const SORT_FIELD_LABELS: Record<SortField, string> = {
  lastRead: 'By last read',
  alphabetical: 'Alphabetically',
  wordCount: 'By word count',
  unknownWords: 'By unknown words',
  learningWords: 'By learning words',
}

export const DEFAULT_SORT_OPTIONS: SortOptions = {
  field: 'lastRead',
  order: 'desc',
}