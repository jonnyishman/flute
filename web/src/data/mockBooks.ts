import { Book } from '../types/book';

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
  ];

  const authors = [
    "F. Scott Fitzgerald", "Harper Lee", "George Orwell", "Jane Austen",
    "J.D. Salinger", "William Golding", "J.R.R. Tolkien", "Ray Bradbury",
    "Charlotte Brontë", "Emily Brontë", "Aldous Huxley", "Oscar Wilde",
    "Bram Stoker", "Mary Shelley", "Mark Twain", "Homer", "William Shakespeare",
    "Charles Dickens", "Ernest Hemingway", "Jack Kerouac", "John Steinbeck",
    "Kurt Vonnegut", "Margaret Atwood", "Toni Morrison", "Alice Walker",
    "Zora Neale Hurston", "Ralph Ellison", "William Faulkner", "Khaled Hosseini",
    "Yann Martel", "Mark Haddon", "Kazuo Ishiguro", "Ian McEwan", "Markus Zusak"
  ];

  return Array.from({ length: count }, (_, i) => {
    const id = startId + i;
    const totalWords = Math.floor(Math.random() * 150000) + 50000; // 50k-200k words
    const readProgress = Math.random();
    const wordsRead = Math.floor(totalWords * readProgress);
    const unknownWords = Math.floor(Math.random() * 5000);
    const learningWords = Math.floor(Math.random() * 3000);
    const knownWords = Math.max(0, wordsRead - unknownWords - learningWords);
    
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
    };
  });
};

// Mock API function to simulate paginated book fetching
export const fetchBooks = async (page: number = 1, pageSize: number = 12): Promise<{ books: Book[], hasMore: boolean, nextPage: number | null, totalCount: number }> => {
  // Simulate API delay
  await new Promise(resolve => setTimeout(resolve, 500));
  
  const totalBooks = 150; // Total number of books in our mock database
  const startIndex = (page - 1) * pageSize;
  const books = generateDummyBooks(startIndex, Math.min(pageSize, totalBooks - startIndex));
  const hasMore = startIndex + pageSize < totalBooks;
  
  return {
    books,
    hasMore,
    nextPage: hasMore ? page + 1 : null,
    totalCount: totalBooks,
  };
};