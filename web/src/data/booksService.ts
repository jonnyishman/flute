import { api } from '../api'
import type { BookSummary } from '../api/types'
import { SortOption, SortOrder } from '../api/types'
import type { Book, BooksPaginationResponse } from '../types/book'
import type { SortOptions } from '../types/sorting'

// Default language ID - in a real app this would come from user settings
const DEFAULT_LANGUAGE_ID = 1

/**
 * Maps backend BookSummary to frontend Book format
 */
function transformBookSummary(summary: BookSummary): Book {
  return {
    id: summary.book_id.toString(),
    title: summary.title,
    coverArt: summary.cover_art_filepath || `https://picsum.photos/300/400?random=${summary.book_id}`,
    wordCount: summary.total_terms,
    unknownWords: summary.unknown_terms,
    learningWords: summary.learning_terms,
    knownWords: summary.known_terms,
    // Mock data for fields not available from backend
    // In a real implementation, these would come from additional API calls
    lastReadDate: new Date().toISOString(),
    readProgressRatio: summary.total_terms > 0 ? summary.known_terms / summary.total_terms : 0,
    totalChapters: 20, // Default placeholder
    lastReadChapter: 1,
  }
}

/**
 * Maps frontend sort options to backend sort parameters
 */
function mapSortOptions(sortOptions: SortOptions): { sortOption: SortOption | null; sortOrder: SortOrder } {
  let backendSortOption: SortOption | null = null

  switch (sortOptions.field) {
    case 'alphabetical':
      backendSortOption = SortOption.TITLE
      break
    case 'lastRead':
      backendSortOption = SortOption.LAST_READ
      break
    case 'learningWords':
      backendSortOption = SortOption.LEARNING_TERMS
      break
    case 'unknownWords':
      backendSortOption = SortOption.UNKNOWN_TERMS
      break
    default:
      backendSortOption = null
  }

  const backendSortOrder = sortOptions.order === 'asc' ? SortOrder.ASC : SortOrder.DESC

  return { sortOption: backendSortOption, sortOrder: backendSortOrder }
}

/**
 * Fetches books from the backend API with pagination and sorting
 */
export async function fetchBooks(
  page: number = 1,
  pageSize: number = 12,
  sortOptions?: SortOptions,
  languageId: number = DEFAULT_LANGUAGE_ID
): Promise<BooksPaginationResponse> {
  const { sortOption, sortOrder } = sortOptions ? mapSortOptions(sortOptions) : { sortOption: null, sortOrder: SortOrder.ASC }

  const response = await api.books.getSummaries({
    language_id: languageId,
    sort_option: sortOption,
    sort_order: sortOrder,
    page,
    per_page: pageSize,
  })

  const transformedBooks = response.summaries.map(transformBookSummary)

  // Backend doesn't provide hasMore or totalCount - these should be calculated by caller
  // using the separate book count endpoint
  const hasNextPage = response.summaries.length === pageSize

  return {
    books: transformedBooks,
    nextPage: hasNextPage ? page + 1 : null,
  }
}