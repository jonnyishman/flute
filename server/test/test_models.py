"""Tests for database models."""

import pytest
from sqlalchemy.exc import IntegrityError

from src.models.book import Book, Chapter


class TestBookModel:
    """Test cases for Book model."""

    def test_create_book(self, app):
        """Test creating a book instance."""
        with app.app_context():
            book = Book(
                title="Test Book",
                source="Test Source"
            )
            book.save()

            assert book.id is not None
            assert book.title == "Test Book"
            assert book.source == "Test Source"
            assert book.is_archived is False
            assert book.cover_art_filepath is None
            assert book.last_visited_chapter is None
            assert book.last_visited_word_index is None

    def test_book_repr(self, app):
        """Test book string representation."""
        with app.app_context():
            book = Book(title="Test Book")
            book.save()

            assert str(book) == "<Book Test Book>"

    def test_book_chapter_relationship(self, app):
        """Test book-chapter relationship."""
        with app.app_context():
            book = Book(title="Test Book")
            book.save()

            chapter1 = Chapter(
                book_id=book.id,
                chapter_number=1,
                content="Chapter 1 content"
            )
            chapter1.save()

            chapter2 = Chapter(
                book_id=book.id,
                chapter_number=2,
                content="Chapter 2 content"
            )
            chapter2.save()

            # Test relationship
            assert book.chapters.count() == 2
            assert chapter1 in book.chapters.all()
            assert chapter2 in book.chapters.all()

    def test_chapter_count_property(self, app):
        """Test chapter_count property."""
        with app.app_context():
            book = Book(title="Test Book")
            book.save()

            # Initially no chapters
            assert book.chapter_count == 0

            # Add chapters
            Chapter(book_id=book.id, chapter_number=1, content="Content 1").save()
            Chapter(book_id=book.id, chapter_number=2, content="Content 2").save()

            assert book.chapter_count == 2

    def test_book_cascade_delete(self, app):
        """Test that deleting a book cascades to chapters."""
        with app.app_context():
            book = Book(title="Test Book")
            book.save()

            chapter = Chapter(
                book_id=book.id,
                chapter_number=1,
                content="Test content"
            )
            chapter.save()

            chapter_id = chapter.id

            # Delete the book
            book.delete()

            # Chapter should be deleted as well
            deleted_chapter = Chapter.query.get(chapter_id)
            assert deleted_chapter is None

    def test_book_to_dict(self, app):
        """Test converting book to dictionary."""
        with app.app_context():
            book = Book(
                title="Test Book",
                source="Test Source",
                cover_art_filepath="/path/to/cover.jpg",
                is_archived=True,
                last_visited_chapter=5,
                last_visited_word_index=100
            )
            book.save()

            book_dict = book.to_dict()
            assert book_dict["title"] == "Test Book"
            assert book_dict["source"] == "Test Source"
            assert book_dict["cover_art_filepath"] == "/path/to/cover.jpg"
            assert book_dict["is_archived"] is True
            assert book_dict["last_visited_chapter"] == 5
            assert book_dict["last_visited_word_index"] == 100
            assert "id" in book_dict
            assert "created_at" in book_dict
            assert "updated_at" in book_dict


class TestChapterModel:
    """Test cases for Chapter model."""

    def test_create_chapter(self, app):
        """Test creating a chapter instance."""
        with app.app_context():
            book = Book(title="Test Book")
            book.save()

            chapter = Chapter(
                book_id=book.id,
                chapter_number=1,
                content="This is chapter content with multiple words"
            )
            chapter.save()

            assert chapter.id is not None
            assert chapter.book_id == book.id
            assert chapter.chapter_number == 1
            assert chapter.content == "This is chapter content with multiple words"
            assert chapter.word_count == 0  # Default value

    def test_chapter_repr(self, app):
        """Test chapter string representation."""
        with app.app_context():
            book = Book(title="Test Book")
            book.save()

            chapter = Chapter(
                book_id=book.id,
                chapter_number=1,
                content="Test content"
            )
            chapter.save()

            assert str(chapter) == f"<Chapter 1 of Book {book.id}>"

    def test_chapter_title_property(self, app):
        """Test chapter title property."""
        with app.app_context():
            book = Book(title="Test Book")
            book.save()

            chapter = Chapter(
                book_id=book.id,
                chapter_number=5,
                content="Test content"
            )
            chapter.save()

            assert chapter.title == "Chapter 5"

    def test_unique_constraint(self, app):
        """Test book_id + chapter_number uniqueness."""
        with app.app_context():
            book = Book(title="Test Book")
            book.save()

            # Create first chapter
            chapter1 = Chapter(
                book_id=book.id,
                chapter_number=1,
                content="First chapter"
            )
            chapter1.save()

            # Try to create another chapter with same book_id and chapter_number
            chapter2 = Chapter(
                book_id=book.id,
                chapter_number=1,
                content="Duplicate chapter"
            )

            with pytest.raises(IntegrityError):
                chapter2.save()

    def test_chapter_book_relationship(self, app):
        """Test chapter-book relationship."""
        with app.app_context():
            book = Book(title="Test Book")
            book.save()

            chapter = Chapter(
                book_id=book.id,
                chapter_number=1,
                content="Test content"
            )
            chapter.save()

            # Test reverse relationship
            assert chapter.book == book
            assert chapter.book.title == "Test Book"

    def test_chapter_word_count_default(self, app):
        """Test that word_count has proper default value."""
        with app.app_context():
            book = Book(title="Test Book")
            book.save()

            # Create chapter without specifying word_count
            chapter = Chapter(
                book_id=book.id,
                chapter_number=1,
                content="Test content"
            )
            chapter.save()

            assert chapter.word_count == 0

            # Create chapter with explicit word_count
            chapter2 = Chapter(
                book_id=book.id,
                chapter_number=2,
                content="Test content",
                word_count=50
            )
            chapter2.save()

            assert chapter2.word_count == 50

    def test_chapter_to_dict(self, app):
        """Test converting chapter to dictionary."""
        with app.app_context():
            book = Book(title="Test Book")
            book.save()

            chapter = Chapter(
                book_id=book.id,
                chapter_number=1,
                content="Test content",
                word_count=25
            )
            chapter.save()

            chapter_dict = chapter.to_dict()
            assert chapter_dict["book_id"] == book.id
            assert chapter_dict["chapter_number"] == 1
            assert chapter_dict["content"] == "Test content"
            assert chapter_dict["word_count"] == 25
            assert "id" in chapter_dict
            assert "created_at" in chapter_dict
            assert "updated_at" in chapter_dict
