"""BDD-style tests for books API endpoints."""

import json

import pytest

from src.models.book import Book, Chapter


class TestGetBooks:
    """Test cases for GET /api/books endpoint."""
    
    def test_get_books_empty_database(self, client):
        """Test getting books from empty database returns empty list."""
        # Given: An empty database
        
        # When: I request the books endpoint
        response = client.get("/api/books")
        
        # Then: I get a successful response with empty results
        assert response.status_code == 200
        data = json.loads(response.data)
        assert data["books"] == []
        assert data["total"] == 0
        assert data["page"] == 1
        assert data["per_page"] == 10
        assert data["total_pages"] == 0
    
    def test_get_books_with_data(self, client, app):
        """Test getting books returns correct book summaries."""
        # Given: A database with sample books and chapters
        with app.app_context():
            book1 = Book(
                title="The Great Gatsby",
                cover_art_filepath="/covers/gatsby.jpg",
                source="Project Gutenberg",
                last_visited_chapter=3,
                last_visited_word_index=150
            )
            book2 = Book(
                title="1984",
                cover_art_filepath=None,
                source=None,
                last_visited_chapter=1,
                last_visited_word_index=50
            )
            book1.save()
            book2.save()
            
            # Add chapters with word counts
            Chapter(book_id=book1.id, chapter_number=1, word_count=1000, content="Chapter 1 content").save()
            Chapter(book_id=book1.id, chapter_number=2, word_count=1200, content="Chapter 2 content").save()
            Chapter(book_id=book1.id, chapter_number=3, word_count=800, content="Chapter 3 content").save()
            
            Chapter(book_id=book2.id, chapter_number=1, word_count=2000, content="Chapter 1 content").save()
        
        # When: I request the books endpoint
        response = client.get("/api/books")
        
        # Then: I get the correct book summaries
        assert response.status_code == 200
        data = json.loads(response.data)
        assert len(data["books"]) == 2
        assert data["total"] == 2
        assert data["total_pages"] == 1
        
        # Check first book details
        book1_data = next(b for b in data["books"] if b["title"] == "The Great Gatsby")
        assert book1_data["cover_art_filepath"] == "/covers/gatsby.jpg"
        assert book1_data["source"] == "Project Gutenberg"
        assert book1_data["last_visited_chapter"] == 3
        assert book1_data["last_visited_word_index"] == 150
        assert book1_data["word_count"] == 3000  # Sum of chapter word counts
        
        # Check second book details
        book2_data = next(b for b in data["books"] if b["title"] == "1984")
        assert book2_data["cover_art_filepath"] is None
        assert book2_data["source"] is None
        assert book2_data["last_visited_chapter"] == 1
        assert book2_data["last_visited_word_index"] == 50
        assert book2_data["word_count"] == 2000
    
    def test_get_books_excludes_archived_books(self, client, app):
        """Test that archived books are excluded from results."""
        # Given: A database with both active and archived books
        with app.app_context():
            active_book = Book(title="Active Book")
            archived_book = Book(title="Archived Book", is_archived=True)
            active_book.save()
            archived_book.save()
        
        # When: I request the books endpoint
        response = client.get("/api/books")
        
        # Then: Only active books are returned
        assert response.status_code == 200
        data = json.loads(response.data)
        assert len(data["books"]) == 1
        assert data["books"][0]["title"] == "Active Book"
    
    def test_get_books_with_no_chapters(self, client, app):
        """Test books with no chapters have word count of 0."""
        # Given: A book with no chapters
        with app.app_context():
            book = Book(title="Empty Book")
            book.save()
        
        # When: I request the books endpoint
        response = client.get("/api/books")
        
        # Then: The book has word count of 0
        assert response.status_code == 200
        data = json.loads(response.data)
        assert len(data["books"]) == 1
        assert data["books"][0]["word_count"] == 0
    
    def test_pagination_first_page(self, client, app):
        """Test pagination returns correct first page."""
        # Given: A database with multiple books
        with app.app_context():
            for i in range(15):
                Book(title=f"Book {i+1}").save()
        
        # When: I request the first page with per_page=5
        response = client.get("/api/books?page=1&per_page=5")
        
        # Then: I get the first 5 books
        assert response.status_code == 200
        data = json.loads(response.data)
        assert len(data["books"]) == 5
        assert data["page"] == 1
        assert data["per_page"] == 5
        assert data["total"] == 15
        assert data["total_pages"] == 3
        
        # Books should be returned in order
        expected_titles = ["Book 1", "Book 2", "Book 3", "Book 4", "Book 5"]
        actual_titles = [book["title"] for book in data["books"]]
        assert actual_titles == expected_titles
    
    def test_pagination_middle_page(self, client, app):
        """Test pagination returns correct middle page."""
        # Given: A database with multiple books
        with app.app_context():
            for i in range(15):
                Book(title=f"Book {i+1}").save()
        
        # When: I request the second page with per_page=5
        response = client.get("/api/books?page=2&per_page=5")
        
        # Then: I get books 6-10
        assert response.status_code == 200
        data = json.loads(response.data)
        assert len(data["books"]) == 5
        assert data["page"] == 2
        
        expected_titles = ["Book 6", "Book 7", "Book 8", "Book 9", "Book 10"]
        actual_titles = [book["title"] for book in data["books"]]
        assert actual_titles == expected_titles
    
    def test_pagination_last_page_partial(self, client, app):
        """Test pagination handles partial last page correctly."""
        # Given: A database with books that don't fill the last page exactly
        with app.app_context():
            for i in range(12):
                Book(title=f"Book {i+1}").save()
        
        # When: I request the third page with per_page=5
        response = client.get("/api/books?page=3&per_page=5")
        
        # Then: I get the remaining 2 books
        assert response.status_code == 200
        data = json.loads(response.data)
        assert len(data["books"]) == 2
        assert data["page"] == 3
        assert data["total_pages"] == 3
        
        expected_titles = ["Book 11", "Book 12"]
        actual_titles = [book["title"] for book in data["books"]]
        assert actual_titles == expected_titles
    
    def test_sort_alphabetical_ascending(self, client, app):
        """Test sorting books alphabetically in ascending order."""
        # Given: Books with titles that need alphabetical sorting
        with app.app_context():
            Book(title="Zebra").save()
            Book(title="Apple").save()
            Book(title="Banana").save()
        
        # When: I request books sorted alphabetically ascending
        response = client.get("/api/books?sort_field=alphabetical&sort_order=asc")
        
        # Then: Books are returned in alphabetical order
        assert response.status_code == 200
        data = json.loads(response.data)
        titles = [book["title"] for book in data["books"]]
        assert titles == ["Apple", "Banana", "Zebra"]
    
    def test_sort_alphabetical_descending(self, client, app):
        """Test sorting books alphabetically in descending order."""
        # Given: Books with titles that need alphabetical sorting
        with app.app_context():
            Book(title="Zebra").save()
            Book(title="Apple").save()
            Book(title="Banana").save()
        
        # When: I request books sorted alphabetically descending
        response = client.get("/api/books?sort_field=alphabetical&sort_order=desc")
        
        # Then: Books are returned in reverse alphabetical order
        assert response.status_code == 200
        data = json.loads(response.data)
        titles = [book["title"] for book in data["books"]]
        assert titles == ["Zebra", "Banana", "Apple"]
    
    def test_sort_word_count_ascending(self, client, app):
        """Test sorting books by word count in ascending order."""
        # Given: Books with different word counts
        with app.app_context():
            book1 = Book(title="Short Book")
            book2 = Book(title="Long Book")
            book3 = Book(title="Medium Book")
            book1.save()
            book2.save()
            book3.save()
            
            Chapter(book_id=book1.id, chapter_number=1, word_count=100, content="Short").save()
            Chapter(book_id=book2.id, chapter_number=1, word_count=1000, content="Long").save()
            Chapter(book_id=book3.id, chapter_number=1, word_count=500, content="Medium").save()
        
        # When: I request books sorted by word count ascending
        response = client.get("/api/books?sort_field=word_count&sort_order=asc")
        
        # Then: Books are returned in word count order
        assert response.status_code == 200
        data = json.loads(response.data)
        titles = [book["title"] for book in data["books"]]
        word_counts = [book["word_count"] for book in data["books"]]
        assert titles == ["Short Book", "Medium Book", "Long Book"]
        assert word_counts == [100, 500, 1000]
    
    def test_sort_word_count_descending(self, client, app):
        """Test sorting books by word count in descending order."""
        # Given: Books with different word counts
        with app.app_context():
            book1 = Book(title="Short Book")
            book2 = Book(title="Long Book")
            book3 = Book(title="Medium Book")
            book1.save()
            book2.save()
            book3.save()
            
            Chapter(book_id=book1.id, chapter_number=1, word_count=100, content="Short").save()
            Chapter(book_id=book2.id, chapter_number=1, word_count=1000, content="Long").save()
            Chapter(book_id=book3.id, chapter_number=1, word_count=500, content="Medium").save()
        
        # When: I request books sorted by word count descending
        response = client.get("/api/books?sort_field=word_count&sort_order=desc")
        
        # Then: Books are returned in reverse word count order
        assert response.status_code == 200
        data = json.loads(response.data)
        titles = [book["title"] for book in data["books"]]
        word_counts = [book["word_count"] for book in data["books"]]
        assert titles == ["Long Book", "Medium Book", "Short Book"]
        assert word_counts == [1000, 500, 100]
    
    def test_combined_pagination_and_sorting(self, client, app):
        """Test that pagination and sorting work together correctly."""
        # Given: Multiple books with different word counts
        with app.app_context():
            for i in range(5):
                book = Book(title=f"Book {i+1}")
                book.save()
                # Create chapters with word counts: 500, 400, 300, 200, 100
                Chapter(
                    book_id=book.id,
                    chapter_number=1,
                    word_count=500 - (i * 100),
                    content=f"Content {i+1}"
                ).save()
        
        # When: I request the first page sorted by word count descending
        response = client.get("/api/books?page=1&per_page=2&sort_field=word_count&sort_order=desc")
        
        # Then: I get the top 2 books by word count
        assert response.status_code == 200
        data = json.loads(response.data)
        assert len(data["books"]) == 2
        assert data["total"] == 5
        assert data["total_pages"] == 3
        
        titles = [book["title"] for book in data["books"]]
        word_counts = [book["word_count"] for book in data["books"]]
        assert titles == ["Book 1", "Book 2"]
        assert word_counts == [500, 400]
    
    def test_invalid_page_parameter(self, client):
        """Test that invalid page parameter returns 400."""
        # Given: A request with invalid page parameter
        
        # When: I request with page=0
        response = client.get("/api/books?page=0")
        
        # Then: I get a validation error
        assert response.status_code == 400
    
    def test_invalid_per_page_parameter(self, client):
        """Test that invalid per_page parameter returns 400."""
        # Given: A request with invalid per_page parameter
        
        # When: I request with per_page=0
        response = client.get("/api/books?per_page=0")
        
        # Then: I get a validation error
        assert response.status_code == 400
    
    def test_per_page_too_large(self, client):
        """Test that per_page over limit returns 400."""
        # Given: A request with per_page over the limit
        
        # When: I request with per_page=200 (over limit of 100)
        response = client.get("/api/books?per_page=200")
        
        # Then: I get a validation error
        assert response.status_code == 400
    
    def test_invalid_sort_field(self, client):
        """Test that invalid sort_field returns 400."""
        # Given: A request with invalid sort_field
        
        # When: I request with an invalid sort field
        response = client.get("/api/books?sort_field=invalid")
        
        # Then: I get a validation error
        assert response.status_code == 400
    
    def test_invalid_sort_order(self, client):
        """Test that invalid sort_order returns 400."""
        # Given: A request with invalid sort_order
        
        # When: I request with an invalid sort order
        response = client.get("/api/books?sort_order=invalid")
        
        # Then: I get a validation error
        assert response.status_code == 400
    
    def test_default_parameters(self, client, app):
        """Test that default parameters are applied correctly."""
        # Given: A database with books
        with app.app_context():
            for i in range(3):
                Book(title=f"Book {i+1}").save()
        
        # When: I request without any parameters
        response = client.get("/api/books")
        
        # Then: Default values are used
        assert response.status_code == 200
        data = json.loads(response.data)
        assert data["page"] == 1
        assert data["per_page"] == 10
        # Default sort should be by ID (insertion order)
        titles = [book["title"] for book in data["books"]]
        assert titles == ["Book 1", "Book 2", "Book 3"]
    
    def test_complex_word_count_aggregation(self, client, app):
        """Test word count aggregation with multiple chapters per book."""
        # Given: Books with multiple chapters having different word counts
        with app.app_context():
            book = Book(title="Multi-Chapter Book")
            book.save()
            
            # Add chapters with various word counts
            Chapter(book_id=book.id, chapter_number=1, word_count=1000, content="Ch1").save()
            Chapter(book_id=book.id, chapter_number=2, word_count=1500, content="Ch2").save()
            Chapter(book_id=book.id, chapter_number=3, word_count=800, content="Ch3").save()
            Chapter(book_id=book.id, chapter_number=4, word_count=1200, content="Ch4").save()
        
        # When: I request the books
        response = client.get("/api/books")
        
        # Then: The word count is correctly aggregated
        assert response.status_code == 200
        data = json.loads(response.data)
        assert len(data["books"]) == 1
        assert data["books"][0]["word_count"] == 4500  # 1000+1500+800+1200