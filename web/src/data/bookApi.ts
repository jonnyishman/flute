import { Book, Chapter } from '../types/reader'

// API configuration
const API_BASE_URL = process.env.REACT_APP_API_URL || 'http://localhost:5000/api'

// API delay simulation for development
const API_DELAY = 300

// Helper function to simulate API delay
const delay = (ms: number) => new Promise(resolve => setTimeout(resolve, ms))

// Fetch all books
export const fetchBooks = async (): Promise<Book[]> => {
  await delay(API_DELAY)
  
  try {
    const response = await fetch(`${API_BASE_URL}/books`)
    if (!response.ok) {
      throw new Error(`HTTP error! status: ${response.status}`)
    }
    return await response.json()
  } catch (error) {
    console.error('Error fetching books:', error)
    // Return mock data for development
    return getMockBooks()
  }
}

// Fetch a specific book with all chapters
export const fetchBookWithChapters = async (bookId: string): Promise<Book> => {
  await delay(API_DELAY)
  
  try {
    const response = await fetch(`${API_BASE_URL}/books/${bookId}`)
    if (!response.ok) {
      throw new Error(`HTTP error! status: ${response.status}`)
    }
    return await response.json()
  } catch (error) {
    console.error('Error fetching book:', error)
    // Return mock data for development
    return getMockBook(bookId)
  }
}

// Fetch a specific chapter
export const fetchChapter = async (bookId: string, chapterNumber: number): Promise<Chapter> => {
  await delay(API_DELAY)
  
  try {
    const response = await fetch(`${API_BASE_URL}/books/${bookId}/chapters/${chapterNumber}`)
    if (!response.ok) {
      throw new Error(`HTTP error! status: ${response.status}`)
    }
    return await response.json()
  } catch (error) {
    console.error('Error fetching chapter:', error)
    // Return mock data for development
    return getMockChapter(bookId, chapterNumber)
  }
}

// Mock data for development and fallback
const mockChapterContents = [
  `# Chapter 1: The Beginning

In the beginning, there was darkness. Not the kind of darkness that comes with night, but a profound absence of light that seemed to stretch beyond the boundaries of perception. Maria stood at the edge of the cliff, her eyes searching the vast expanse of the ocean below.

The waves crashed against the rocks with a rhythmic persistence that had become the soundtrack to her solitude. She had come here every day for the past month, always at the same time, always carrying the same leather-bound journal that her grandmother had given her years ago.

The journal contained stories, memories, and dreams that seemed more real than the world around her. Today, however, felt different. There was something in the air, a change that she couldn't quite define but could feel in the depths of her soul.

The wind picked up, carrying with it the scent of salt and something else - something that reminded her of childhood summers and forgotten laughter. She opened the journal to a blank page and began to write, her pen moving across the paper with a fluidity that surprised her.

The words came naturally, as if they had been waiting inside her all along, patient and ready to emerge into the light of day. As she wrote, the darkness around her seemed to recede slightly, as though the very act of creation was bringing light back into the world.

She paused, looking up from the page to see the first faint glimmer of dawn on the horizon. The lighthouse in the distance began to fade as natural light took its place, but its presence remained a constant reminder of guidance through the darkness.`,

  `# Chapter 2: The Lighthouse Keeper

Chapter Two opened with a scene that would haunt readers for generations. The old lighthouse keeper, Thomas, had been alone on the island for fifteen years. His only companions were the seabirds that nested in the rocky crevices and the occasional ship that passed by on clear nights.

He had grown accustomed to the isolation, finding solace in the predictable rhythm of his duties. Each evening, as the sun began its descent toward the horizon, Thomas would climb the spiral staircase to the top of the lighthouse.

The stairs creaked under his weight, a familiar symphony that marked the transition from day to night. At the top, he would light the great beacon, its powerful beam sweeping across the dark waters like a guardian angel watching over lost souls.

But tonight was different. As Thomas reached for the switch that would illuminate the beacon, he noticed something moving in the water below. It wasn't a ship or a whale or any of the usual inhabitants of these waters.

It was something else entirely, something that made his heart race and his hands tremble as he pressed his face against the cold glass of the lighthouse window. The shape moved with purpose, circling the island in a pattern that seemed almost deliberate.

Thomas had seen many strange things during his years of solitude, but this was different. This felt like a message, a sign that his years of faithful service were about to be rewarded with something extraordinary.

He lit the beacon with trembling hands, watching as its light swept across the mysterious form in the water. Whatever it was, it seemed to respond to the light, moving closer to the shore with each pass of the beam.`,

  `# Chapter 3: The Discovery

The discovery changed everything. What Maria had found in her grandmother's journal wasn't just family history - it was a map, a guide to understanding the strange occurrences that had been happening in the small coastal town for decades.

The disappearances, the unexplained lights, the stories that the older residents whispered about but never fully explained. She traced the faded ink with her finger, following the careful annotations her grandmother had made in the margins.

Each note was dated, some going back fifty years or more. They told a story of vigilance, of watching and waiting, of a responsibility passed down through generations of women in her family.

'The keeper of memories,' one note read, 'must never let the truth fade into legend.' Maria understood now why her grandmother had always seemed so serious, so watchful. She had been guarding something precious and dangerous, something that required constant attention and care.

Now that responsibility had passed to Maria, and she wasn't sure she was ready for what it might demand of her. The lighthouse beam swept across her window, and for a moment, she could swear she saw a figure standing at the top of the tower, waving in her direction.

But when she looked again, there was nothing there but the endless rotation of light against the darkness. The journal in her hands seemed to grow heavier with each page she turned, as though the weight of generations of secrets was settling on her shoulders.

She closed the book and walked to her window, looking out at the lighthouse. Thomas was up there, she knew, keeping his lonely vigil. Did he know about the journal? Did he understand his role in the greater mystery that surrounded their small town?

These questions would have to wait for daylight. Tonight, she would read every word her grandmother had written, preparing herself for the responsibilities that awaited her.`,

  `# Chapter 4: The Pattern Emerges

Days turned into weeks as Maria delved deeper into the mystery. She discovered that the lighthouse keeper, Thomas, had been writing his own journal, documenting strange phenomena that occurred on and around the island.

Ship logs from the past century mentioned unexplained magnetic disturbances in the area, compasses spinning wildly, and electronic equipment failing without cause. The town's library held newspaper clippings dating back to the 1800s, all reporting similar incidents.

People would see lights beneath the water, hear music carried on the wind when there were no musicians for miles, and occasionally, someone would simply vanish without a trace, leaving behind only their belongings and a lingering scent of sea salt and jasmine.

Maria realized that her grandmother hadn't just been documenting these events - she had been trying to understand them, to find a pattern or purpose behind the supernatural occurrences. The journal contained sketches of symbols found carved into rocks along the shoreline, translations of ancient texts, and correspondence with scholars from universities around the world.

It was becoming clear that this small coastal town was situated at the intersection of something much larger and more mysterious than anyone had imagined. The lighthouse wasn't just guiding ships to safety - it was serving as a beacon for something else entirely.

Something that existed in the spaces between the known and the unknown, between the world of the living and realms that defied explanation. The pattern was emerging, and Maria was beginning to understand her grandmother's warnings about the weight of knowledge.

Some truths, once discovered, could never be forgotten. Some responsibilities, once accepted, could never be abandoned. The lighthouse beam continued its eternal sweep across the waters, and Maria knew that her life would never be the same again.

As she prepared to meet with Thomas and share what she had learned, she wondered if he was ready for the truth that had been hiding in plain sight for so many years.`
]

const getMockBooks = (): Book[] => [
  {
    id: 1,
    title: "The Lighthouse Mystery",
    author: "Anonymous",
    description: "A haunting tale of secrets, solitude, and supernatural occurrences in a small coastal town.",
    total_chapters: 4,
    created_at: new Date().toISOString(),
    chapters: []
  }
]

const getMockBook = (bookId: string): Book => {
  const chapters: Chapter[] = mockChapterContents.map((content, index) => ({
    id: index + 1,
    chapter_number: index + 1,
    title: `Chapter ${index + 1}`,
    content,
    word_count: content.split(' ').length
  }))

  return {
    id: parseInt(bookId),
    title: "The Lighthouse Mystery",
    author: "Anonymous",
    description: "A haunting tale of secrets, solitude, and supernatural occurrences in a small coastal town.",
    total_chapters: 4,
    created_at: new Date().toISOString(),
    chapters
  }
}

const getMockChapter = (bookId: string, chapterNumber: number): Chapter => {
  const content = mockChapterContents[chapterNumber - 1] || mockChapterContents[0]
  return {
    id: chapterNumber,
    chapter_number: chapterNumber,
    title: `Chapter ${chapterNumber}`,
    content,
    word_count: content.split(' ').length
  }
}