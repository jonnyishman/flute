"""Tests for database models."""
from __future__ import annotations

from typing import TYPE_CHECKING

import pytest
import sqlalchemy as sa
from sqlalchemy.exc import IntegrityError

from src.models import db
from src.models.books import (
    Book,
    BookTotals,
    BookVocab,
    Chapter,
    LearningStatus,
    Term,
    TermProgress,
)
from src.models.language import Language

if TYPE_CHECKING:
    from flask import Flask

class TestBookModel:
    """Test cases for Book model."""

    def test_create_book(self, app: Flask):
        """Test creating a book instance."""
        # Given
        language = Language(name="English")
        book = Book(
            language=language,
            title="Test Book",
            source="Test Source"
        )

        # When
        db.session.add_all([language, book])
        db.session.commit()

        # Then
        assert book.id is not None
        assert book.language_id == language.id
        assert book.title == "Test Book"
        assert book.source == "Test Source"
        assert book.is_archived is False
        assert book.cover_art_filepath is None
        assert book.last_visited_chapter is None
        assert book.last_visited_word_index is None

    def test_book_chapter_relationship(self, app: Flask):
        """Test book-chapter relationship."""
        # Given
        language = Language(name="Spanish")
        book = Book(language=language, title="Test Book")
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

        # When
        db.session.add_all([language, book, chapter1, chapter2])
        db.session.commit()

        # Then
        assert book.chapters.count() == 2
        assert chapter1 in book.chapters.all()
        assert chapter2 in book.chapters.all()

    def test_book_cascade_delete(self, app: Flask):
        """Test that deleting a book cascades to chapters."""
        # Given a book with a chapter
        language = Language(name="French")
        book = Book(language=language, title="Test Book")
        chapter = Chapter(
            book=book,
            chapter_number=1,
            content="Test content",
            word_count=2,
        )
        db.session.add_all([language, book, chapter])
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
        # Given
        language = Language(name="German")
        book = Book(language=language, title="Test Book")
        chapter = Chapter(
            book=book,
            chapter_number=1,
            content="This is chapter content with multiple words",
            word_count=7,
        )

        # When
        db.session.add_all([language, book, chapter])
        db.session.commit()

        # Then
        assert chapter.id is not None
        assert chapter.book_id == book.id
        assert chapter.chapter_number == 1
        assert chapter.content == "This is chapter content with multiple words"

    def test_unique_constraint(self, app: Flask):
        """Test book_id + chapter_number uniqueness"""
        # Given a book with a chapter number 1
        language = Language(name="Italian")
        book = Book(language=language, title="Test Book")
        chapter1 = Chapter(
            book=book,
            chapter_number=1,
            content="First chapter",
            word_count=2,
        )
        db.session.add_all([language, book, chapter1])
        db.session.commit()

        # When trying to add another chapter with the same chapter_number
        chapter2 = Chapter(
            book=book,
            chapter_number=1,
            content="Duplicate chapter",
            word_count=2,
        )
        db.session.add(chapter2)

        # Then it should raise an IntegrityError
        with pytest.raises(IntegrityError):
            db.session.commit()


class TestTermModel:
    """Test cases for Term model."""

    def test_create_Term_word(self, english: Language):
        """Test creating a word Term."""
        # Given
        term = Term(language=english, norm="hello", display="Hello", token_count=1)

        # When
        db.session.add_all([english, term])
        db.session.commit()

        # Then
        assert term.id is not None
        assert term.language_id == english.id
        assert term.norm == "hello"
        assert term.display == "Hello"
        assert term.token_count == 1

    def test_create_token_phrase(self, spanish: Language):
        """Test creating a phrase token."""
        # Given
        term = Term(language_id=spanish.id, norm="hello world", display="Hello World", token_count=2)

        # When
        db.session.add(term)
        db.session.commit()

        # Then
        assert term.id is not None
        assert term.language_id == spanish.id
        assert term.norm == "hello world"
        assert term.display == "Hello World"
        assert term.token_count == 2

    def test_term_unique_constraint(self, turkish: Language):
        """Test term norm must be unique per language."""
        # Given
        term1 = Term(language=turkish, norm="unique", display="Unique", token_count=1)
        term2 = Term(language=turkish, norm="unique", display="Unique2", token_count=1)

        # When
        db.session.add_all([term1, term2])

        # Then
        with pytest.raises(IntegrityError):
            db.session.commit()




class TestBookVocabModel:
    """Test cases for BookVocab model."""

    def test_create_book_vocab(self, japanese: Language):
        """Test creating a book vocab entry."""
        # Given
        book = Book(language_id=japanese.id, title="Test Book")
        term = Term(language_id=japanese.id, norm="word", display="word", token_count=1)
        db.session.add_all([book, term])
        db.session.commit()

        vocab = BookVocab(book_id=book.id, term_id=term.id, term_count=5)

        # When
        db.session.add(vocab)
        db.session.commit()

        # Then
        assert vocab.book_id == book.id
        assert vocab.term_id == term.id
        assert vocab.term_count == 5

    def test_book_vocab_composite_key(self, classical_chinese):
        """Test book vocab composite primary key constraint."""
        # Given
        book = Book(language=classical_chinese, title="Test Book")
        term = Term(language=classical_chinese, norm="word", display="word", token_count=1)
        db.session.add_all([book, term])
        db.session.commit()

        vocab1 = BookVocab(book_id=book.id, term_id=term.id, term_count=3)
        vocab2 = BookVocab(book_id=book.id, term_id=term.id, term_count=5)

        # When
        db.session.add_all([vocab1, vocab2])

        # Then
        with pytest.raises(IntegrityError):
            db.session.commit()

    def test_book_vocab_foreign_keys(self, hindi: Language):
        """Test book vocab requires valid book and token."""
        # Given
        book = Book(language_id=hindi.id, title="Test Book")
        term = Term(language_id=hindi.id, norm="word", display="word", token_count=1)
        db.session.add_all([book, term])
        db.session.commit()

        # When - Valid vocab entry should work
        vocab = BookVocab(book_id=book.id, term_id=term.id, term_count=1)
        db.session.add(vocab)
        db.session.commit()

        # Then
        assert vocab.book_id == book.id
        assert vocab.term_id == term.id


class TestTermProgressModel:
    """Test cases for TermProgress model."""

    def test_create_term_progress_learning(self, spanish: Language):
        """Test creating term progress in learning state."""
        # Given
        term = Term(language=spanish, norm="learning", display="learning", token_count=1)
        db.session.add(term)
        db.session.commit()

        progress = TermProgress(
            term_id=term.id,
            status=LearningStatus.LEARNING,
            learning_stage=3,
            translation="aprendiendo"
        )

        # When
        db.session.add(progress)
        db.session.commit()

        # Then
        assert progress.term_id == term.id
        assert progress.status == LearningStatus.LEARNING
        assert progress.learning_stage == 3
        assert progress.translation == "aprendiendo"

    def test_create_term_progress_known(self, spanish: Language):
        """Test creating term progress in known state."""
        # Given
        term = Term(language_id=spanish.id, norm="known", display="known", token_count=1)
        db.session.add(term)
        db.session.commit()

        progress = TermProgress(
            term_id=term.id,
            status=LearningStatus.KNOWN,
            translation="conocido"
        )

        # When
        db.session.add(progress)
        db.session.commit()

        # Then
        assert progress.term_id == term.id
        assert progress.status == LearningStatus.KNOWN
        assert progress.learning_stage is None

    def test_create_term_progress_ignore(self, japanese: Language):
        """Test creating term progress in ignore state."""
        # Given
        term = Term(language=japanese, norm="ignore", display="ignore", token_count=1)
        db.session.add(term)
        db.session.commit()

        progress = TermProgress(
            term_id=term.id,
            status=LearningStatus.IGNORE
        )

        # When
        db.session.add(progress)
        db.session.commit()

        # Then
        assert progress.term_id == term.id
        assert progress.status == LearningStatus.IGNORE
        assert progress.learning_stage is None

    def test_term_progress_status_constraint(self, hindi: Language):
        """Test term progress status must be valid."""
        # Given
        term = Term(language=hindi, norm="test", display="test", token_count=1)
        db.session.add(term)
        db.session.commit()

        progress = TermProgress(term_id=term.id, status=99)

        # When
        db.session.add(progress)

        # Then
        with pytest.raises(IntegrityError):
            db.session.commit()

    def test_term_progress_learning_stage_constraint(self, hindi: Language):
        """Test learning stage constraint for learning status."""
        # Given
        term = Term(language_id=hindi.id, norm="test", display="test", token_count=1)
        db.session.add(term)
        db.session.commit()

        # When - Learning status with invalid stage
        progress = TermProgress(
            term_id=term.id,
            status=LearningStatus.LEARNING,
            learning_stage=10  # Invalid stage
        )
        db.session.add(progress)

        # Then
        with pytest.raises(IntegrityError):
            db.session.commit()

    def test_term_progress_foreign_key(self, spanish: Language):
        """Test term progress requires valid term."""
        # Given
        term = Term(language_id=spanish.id, norm="valid", display="valid", token_count=1)
        db.session.add(term)
        db.session.commit()

        # When - Valid progress entry should work
        progress = TermProgress(term_id=term.id, status=LearningStatus.KNOWN)
        db.session.add(progress)
        db.session.commit()

        # Then
        assert progress.term_id == term.id
        assert progress.status == LearningStatus.KNOWN


class TestBookTotalsModel:
    """Test cases for BookTotals model."""

    def test_create_book_totals(self, english: Language):
        """Test creating book totals."""
        # Given
        book = Book(language=english, title="Test Book")
        db.session.add(book)
        db.session.commit()

        totals = BookTotals(
            book_id=book.id,
            total_terms=1000,
            total_types=500
        )

        # When
        db.session.add(totals)
        db.session.commit()

        # Then
        assert totals.book_id == book.id
        assert totals.total_terms == 1000
        assert totals.total_types == 500

    def test_book_totals_relationship(self, spanish: Language):
        """Test book totals relationship with book."""
        # Given
        book = Book(language=spanish, title="Test Book")
        db.session.add(book)
        db.session.commit()

        totals = BookTotals(
            book_id=book.id,
            total_terms=1000,
            total_types=500
        )

        # When
        db.session.add(totals)
        db.session.commit()

        # Then - Verify the relationship
        assert totals.book_id == book.id

        # Test querying
        found_totals = db.session.execute(
            sa.select(BookTotals).where(BookTotals.book_id == book.id)
        ).scalar_one()
        assert found_totals.total_terms == 1000
        assert found_totals.total_types == 500
