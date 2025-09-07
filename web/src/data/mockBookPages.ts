// This file is deprecated - use bookApi.ts instead
// Kept for backward compatibility

import { BookPage } from '../types/reader'

console.warn('mockBookPages.ts is deprecated. Please use bookApi.ts instead.')

// Sample book content for different pages
const sampleTexts = [
  "In the beginning, there was darkness. Not the kind of darkness that comes with night, but a profound absence of light that seemed to stretch beyond the boundaries of perception. Maria stood at the edge of the cliff, her eyes searching the vast expanse of the ocean below. The waves crashed against the rocks with a rhythmic persistence that had become the soundtrack to her solitude.\n\nShe had come here every day for the past month, always at the same time, always carrying the same leather-bound journal that her grandmother had given her years ago. The journal contained stories, memories, and dreams that seemed more real than the world around her. Today, however, felt different. There was something in the air, a change that she couldn't quite define but could feel in the depths of her soul.\n\nThe wind picked up, carrying with it the scent of salt and something else - something that reminded her of childhood summers and forgotten laughter. She opened the journal to a blank page and began to write, her pen moving across the paper with a fluidity that surprised her. The words came naturally, as if they had been waiting inside her all along, patient and ready to emerge into the light of day.",
  
  "Chapter Two opened with a scene that would haunt readers for generations. The old lighthouse keeper, Thomas, had been alone on the island for fifteen years. His only companions were the seabirds that nested in the rocky crevices and the occasional ship that passed by on clear nights. He had grown accustomed to the isolation, finding solace in the predictable rhythm of his duties.\n\nEach evening, as the sun began its descent toward the horizon, Thomas would climb the spiral staircase to the top of the lighthouse. The stairs creaked under his weight, a familiar symphony that marked the transition from day to night. At the top, he would light the great beacon, its powerful beam sweeping across the dark waters like a guardian angel watching over lost souls.\n\nBut tonight was different. As Thomas reached for the switch that would illuminate the beacon, he noticed something moving in the water below. It wasn't a ship or a whale or any of the usual inhabitants of these waters. It was something else entirely, something that made his heart race and his hands tremble as he pressed his face against the cold glass of the lighthouse window.",

  "The discovery changed everything. What Maria had found in her grandmother's journal wasn't just family history - it was a map, a guide to understanding the strange occurrences that had been happening in the small coastal town for decades. The disappearances, the unexplained lights, the stories that the older residents whispered about but never fully explained.\n\nShe traced the faded ink with her finger, following the careful annotations her grandmother had made in the margins. Each note was dated, some going back fifty years or more. They told a story of vigilance, of watching and waiting, of a responsibility passed down through generations of women in her family.\n\n'The keeper of memories,' one note read, 'must never let the truth fade into legend.' Maria understood now why her grandmother had always seemed so serious, so watchful. She had been guarding something precious and dangerous, something that required constant attention and care. Now that responsibility had passed to Maria, and she wasn't sure she was ready for what it might demand of her.\n\nThe lighthouse beam swept across her window, and for a moment, she could swear she saw a figure standing at the top of the tower, waving in her direction. But when she looked again, there was nothing there but the endless rotation of light against the darkness.",

  "Days turned into weeks as Maria delved deeper into the mystery. She discovered that the lighthouse keeper, Thomas, had been writing his own journal, documenting strange phenomena that occurred on and around the island. Ship logs from the past century mentioned unexplained magnetic disturbances in the area, compasses spinning wildly, and electronic equipment failing without cause.\n\nThe town's library held newspaper clippings dating back to the 1800s, all reporting similar incidents. People would see lights beneath the water, hear music carried on the wind when there were no musicians for miles, and occasionally, someone would simply vanish without a trace, leaving behind only their belongings and a lingering scent of sea salt and jasmine.\n\nMaria realized that her grandmother hadn't just been documenting these events - she had been trying to understand them, to find a pattern or purpose behind the supernatural occurrences. The journal contained sketches of symbols found carved into rocks along the shoreline, translations of ancient texts, and correspondence with scholars from universities around the world.\n\nIt was becoming clear that this small coastal town was situated at the intersection of something much larger and more mysterious than anyone had imagined. The lighthouse wasn't just guiding ships to safety - it was serving as a beacon for something else entirely, something that existed in the spaces between the known and the unknown."
]

// Generate pages for a specific book
export const generateBookPages = (bookId: string, totalPages: number = 4): BookPage[] => {
  return Array.from({ length: totalPages }, (_, index) => ({
    pageNumber: index + 1,
    content: sampleTexts[index % sampleTexts.length],
    wordCount: sampleTexts[index % sampleTexts.length].split(' ').length
  }))
}

// Mock API function to fetch a specific page
export const fetchBookPage = async (bookId: string, pageNumber: number): Promise<BookPage> => {
  // Simulate API delay
  await new Promise(resolve => setTimeout(resolve, 300))
  
  const pages = generateBookPages(bookId)
  const page = pages.find(p => p.pageNumber === pageNumber)
  
  if (!page) {
    throw new Error(`Page ${pageNumber} not found for book ${bookId}`)
  }
  
  return page
}

// Get total pages for a book
export const getBookTotalPages = (bookId: string): number => {
  return 4 // For now, all books have 4 pages
}