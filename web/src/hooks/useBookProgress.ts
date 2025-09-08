import { useAtom, useAtomValue, useSetAtom } from 'jotai'
import { 
  bookProgressAtom, 
  updateBookProgressAtom, 
  readingSessionAtom,
  startReadingSessionAtom,
  endReadingSessionAtom,
  BookProgress
} from '../store/atoms'

export const useBookProgress = () => {
  const [bookProgress] = useAtom(bookProgressAtom)
  const updateProgress = useSetAtom(updateBookProgressAtom)
  const readingSession = useAtomValue(readingSessionAtom)
  const startSession = useSetAtom(startReadingSessionAtom)
  const endSession = useSetAtom(endReadingSessionAtom)
  
  const getBookProgress = (bookId: string): BookProgress | null => {
    return bookProgress[bookId] || null
  }
  
  const updateBookProgress = (bookId: string, chapter: number, progressRatio?: number) => {
    updateProgress({ bookId, chapter, progressRatio })
  }
  
  const startReadingSession = (bookId: string, chapter: number) => {
    startSession({ bookId, chapter })
  }
  
  const endReadingSession = () => {
    endSession()
  }
  
  const isCurrentlyReading = (bookId: string): boolean => {
    return readingSession.currentBookId === bookId
  }
  
  return {
    bookProgress,
    getBookProgress,
    updateBookProgress,
    startReadingSession,
    endReadingSession,
    isCurrentlyReading,
    currentSession: readingSession,
  }
}

export default useBookProgress