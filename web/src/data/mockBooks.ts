import { Book } from '../types/book'
import { SortOptions } from '../types/sorting'

// Generate dummy book data
const generateDummyBooks = (startId: number, count: number): Book[] => {
  const bookTitles = [
    "The Great Gatsby", "To Kill a Mockingbird", "1984", "Pride and Prejudice",
    "The Catcher in the Rye", "Lord of the Flies", "The Hobbit", "Fahrenheit 451",
    "Jane Eyre", "Wuthering Heights", "The Lord of the Rings", "Animal Farm",
    "Brave New World", "The Picture of Dorian Gray", "Dracula", "Frankenstein",
    "The Adventures of Huckleberry Finn", "The Odyssey", "Romeo and Juliet",
    "Hamlet", "Macbeth", "A Tale of Two Cities", "Great Expectations",
    "Oliver Twist", "David Copperfield", "The Sun Also Rises", "For Whom the Bell Tolls",
    "The Old Man and the Sea", "On the Road", "Of Mice and Men", "The Grapes of Wrath",
    "East of Eden", "Slaughterhouse-Five", "Cat's Cradle", "The Handmaid's Tale",
    "Margaret Atwood", "Beloved", "The Color Purple", "Their Eyes Were Watching God",
    "Invisible Man", "The Sound and the Fury", "As I Lay Dying", "Light in August",
    "Go Set a Watchman", "The Kite Runner", "A Thousand Splendid Suns", "Life of Pi",
    "The Curious Incident", "Never Let Me Go", "Atonement", "The Book Thief"
  ]

  return Array.from({ length: count }, (_, i) => {
    const id = startId + i
    const totalWords = Math.floor(Math.random() * 150000) + 50000 // 50k-200k words
    const readProgress = Math.random()
    const wordsRead = Math.floor(totalWords * readProgress)
    const unknownWords = Math.floor(Math.random() * 5000)
    const learningWords = Math.floor(Math.random() * 3000)
    const knownWords = Math.max(0, wordsRead - unknownWords - learningWords)
    
    const lastReadChapter = Math.floor(readProgress * 20) + 1 // Assume up to 20 chapters for lastReadChapter calculation

    return {
      id: `book-${id}`,
      title: bookTitles[i % bookTitles.length],
      coverArt: `https://picsum.photos/300/400?random=${id}`,
      wordCount: totalWords,
      unknownWords,
      learningWords,
      knownWords,
      lastReadDate: new Date(Date.now() - Math.floor(Math.random() * 30 * 24 * 60 * 60 * 1000)).toISOString(), // Random date within last 30 days
      readProgressRatio: readProgress,
      lastReadChapter,
    }
  })
}

// Helper function to sort books based on sort options
const sortBooks = (books: Book[], sortOptions: SortOptions): Book[] => {
  return [...books].sort((a, b) => {
    let comparison = 0
    
    switch (sortOptions.field) {
      case 'lastRead':
        const dateA = a.lastReadDate ? new Date(a.lastReadDate).getTime() : 0
        const dateB = b.lastReadDate ? new Date(b.lastReadDate).getTime() : 0
        comparison = dateA - dateB
        break
      case 'alphabetical':
        comparison = a.title.localeCompare(b.title)
        break
      case 'unknownWords':
        comparison = a.unknownWords - b.unknownWords
        break
      case 'learningWords':
        comparison = a.learningWords - b.learningWords
        break
      default:
        comparison = 0
    }
    
    return sortOptions.order === 'asc' ? comparison : -comparison
  })
}

// Mock API function to simulate paginated book fetching
export const fetchBooks = async (
  page: number = 1, 
  pageSize: number = 12,
  sortOptions?: SortOptions
): Promise<{ books: Book[], hasMore: boolean, nextPage: number | null, totalCount: number }> => {
  // Simulate API delay
  await new Promise(resolve => setTimeout(resolve, 500))
  
  const totalBooks = 150 // Total number of books in our mock database
  
  // Generate all books for sorting (in real implementation, this would be handled by the backend)
  const allBooks = generateDummyBooks(0, totalBooks)
  
  // Sort books if sort options provided
  const sortedBooks = sortOptions ? sortBooks(allBooks, sortOptions) : allBooks
  
  // Apply pagination to sorted books
  const startIndex = (page - 1) * pageSize
  const paginatedBooks = sortedBooks.slice(startIndex, startIndex + pageSize)
  const hasMore = startIndex + pageSize < totalBooks
  
  return {
    books: paginatedBooks,
    hasMore,
    nextPage: hasMore ? page + 1 : null,
    totalCount: totalBooks,
  }
}