"""Tests for database models."""
from __future__ import annotations

from typing import TYPE_CHECKING

import pytest
import sqlalchemy as sa
from sqlalchemy.exc import IntegrityError

from src.models import db
from src.models.books import Book, Chapter

if TYPE_CHECKING:
    from flask import Flask

class TestBookModel:
    """Test cases for Book model."""

    def test_create_book(self, app: Flask):
        """Test creating a book instance."""
        book = Book(
            title="Test Book",
            source="Test Source"
        )
        db.session.add(book)
        db.session.commit()

        assert book.id is not None
        assert book.title == "Test Book"
        assert book.source == "Test Source"
        assert book.is_archived is False
        assert book.cover_art_filepath is None
        assert book.last_visited_chapter is None
        assert book.last_visited_word_index is None

    def test_book_chapter_relationship(self, app: Flask):
        """Test book-chapter relationship."""
        book = Book(title="Test Book")
        chapter1 = Chapter(
            book=book,
            chapter_number=1,
            content="Chapter 1 content",
            word_count=3,
        )
        chapter2 = Chapter(
            book=book,
            chapter_number=2,
            content="Chapter 2 content",
            word_count=3,
        )
        db.session.add_all([book, chapter1, chapter2])
        db.session.commit()

        # Test relationship
        assert book.chapters.count() == 2
        assert chapter1 in book.chapters.all()
        assert chapter2 in book.chapters.all()

    def test_book_cascade_delete(self, app: Flask):
        """Test that deleting a book cascades to chapters."""
        # Given a book with a chapter
        book = Book(title="Test Book")
        chapter = Chapter(
            book=book,
            chapter_number=1,
            content="Test content",
            word_count=3,
        )
        db.session.add_all([book, chapter])
        db.session.commit()

        # When deleting the book
        db.session.delete(book)
        db.session.commit()

        # Then chapter should be deleted as well
        chapters = list(db.session.execute(sa.select(Chapter)).all())
        assert not chapters


class TestChapterModel:
    """Test cases for Chapter model."""

    def test_create_chapter(self, app: Flask):
        """Test creating a chapter instance."""
        book = Book(title="Test Book")
        chapter = Chapter(
            book=book,
            chapter_number=1,
            content="This is chapter content with multiple words",
            word_count=3,
        )
        db.session.add_all([book, chapter])
        db.session.commit()

        assert chapter.id is not None
        assert chapter.book_id == book.id
        assert chapter.chapter_number == 1
        assert chapter.content == "This is chapter content with multiple words"
        assert chapter.word_count == 3

    def test_unique_constraint(self, app: Flask):
        """Test book_id + chapter_number uniqueness"""
        # Given a book with a chapter number 1
        book = Book(title="Test Book")
        chapter1 = Chapter(
            book=book,
            chapter_number=1,
            content="First chapter",
            word_count=3,
        )
        db.session.add_all([book, chapter1])
        db.session.commit()

        # When trying to add another chapter with the same chapter_number
        chapter2 = Chapter(
            book=book,
            chapter_number=1,
            content="Duplicate chapter",
            word_count=3,
        )
        db.session.add(chapter2)

        # Then it should raise an IntegrityError
        with pytest.raises(IntegrityError):
            db.session.commit()
