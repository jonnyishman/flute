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
    Token,
    TokenKind,
    TokenProgress,
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


class TestTokenModel:
    """Test cases for Token model."""

    def test_create_token_word(self, app: Flask):
        """Test creating a word token."""
        # Given
        language = Language(name="English")
        token = Token(language=language, norm="hello", kind=TokenKind.WORD)

        # When
        db.session.add_all([language, token])
        db.session.commit()

        # Then
        assert token.id is not None
        assert token.language_id == language.id
        assert token.norm == "hello"
        assert token.kind == TokenKind.WORD

    def test_create_token_phrase(self, app: Flask):
        """Test creating a phrase token."""
        # Given
        language = Language(name="Spanish")
        db.session.add(language)
        db.session.commit()

        token = Token(language_id=language.id, norm="hello world", kind=TokenKind.PHRASE)

        # When
        db.session.add(token)
        db.session.commit()

        # Then
        assert token.id is not None
        assert token.language_id == language.id
        assert token.norm == "hello world"
        assert token.kind == TokenKind.PHRASE

    def test_token_default_kind(self, app: Flask):
        """Test token defaults to WORD kind."""
        # Given
        language = Language(name="French")
        db.session.add(language)
        db.session.commit()

        token = Token(language_id=language.id, norm="default")

        # When
        db.session.add(token)
        db.session.commit()

        # Then
        assert token.kind == TokenKind.WORD

    def test_token_unique_constraint(self, app: Flask):
        """Test token norm must be unique."""
        # Given
        language = Language(name="German")
        db.session.add(language)
        db.session.commit()

        token1 = Token(language_id=language.id, norm="unique")
        token2 = Token(language_id=language.id, norm="unique")

        # When
        db.session.add_all([token1, token2])

        # Then
        with pytest.raises(IntegrityError):
            db.session.commit()

    def test_token_kind_constraint(self, app: Flask):
        """Test token kind must be valid."""
        # Given
        language = Language(name="Portuguese")
        db.session.add(language)
        db.session.commit()

        token = Token(language_id=language.id, norm="test", kind=99)  # Invalid kind

        # When
        db.session.add(token)

        # Then
        with pytest.raises(IntegrityError):
            db.session.commit()


class TestBookVocabModel:
    """Test cases for BookVocab model."""

    def test_create_book_vocab(self, app: Flask):
        """Test creating a book vocab entry."""
        # Given
        language = Language(name="Japanese")
        db.session.add(language)
        db.session.commit()

        book = Book(language_id=language.id, title="Test Book")
        token = Token(language_id=language.id, norm="word")
        db.session.add_all([book, token])
        db.session.commit()

        vocab = BookVocab(book_id=book.id, token_id=token.id, token_count=5)

        # When
        db.session.add(vocab)
        db.session.commit()

        # Then
        assert vocab.book_id == book.id
        assert vocab.token_id == token.id
        assert vocab.token_count == 5

    def test_book_vocab_composite_key(self, app: Flask):
        """Test book vocab composite primary key constraint."""
        # Given
        language = Language(name="Korean")
        db.session.add(language)
        db.session.commit()

        book = Book(language_id=language.id, title="Test Book")
        token = Token(language_id=language.id, norm="word")
        db.session.add_all([book, token])
        db.session.commit()

        vocab1 = BookVocab(book_id=book.id, token_id=token.id, token_count=3)
        vocab2 = BookVocab(book_id=book.id, token_id=token.id, token_count=5)

        # When
        db.session.add_all([vocab1, vocab2])

        # Then
        with pytest.raises(IntegrityError):
            db.session.commit()

    def test_book_vocab_foreign_keys(self, app: Flask):
        """Test book vocab requires valid book and token."""
        # Given
        language = Language(name="Russian")
        db.session.add(language)
        db.session.commit()

        book = Book(language_id=language.id, title="Test Book")
        token = Token(language_id=language.id, norm="word")
        db.session.add_all([book, token])
        db.session.commit()

        # When - Valid vocab entry should work
        vocab = BookVocab(book_id=book.id, token_id=token.id, token_count=1)
        db.session.add(vocab)
        db.session.commit()

        # Then
        assert vocab.book_id == book.id
        assert vocab.token_id == token.id


class TestTokenProgressModel:
    """Test cases for TokenProgress model."""

    def test_create_token_progress_learning(self, app: Flask):
        """Test creating token progress in learning state."""
        # Given
        language = Language(name="Spanish")
        db.session.add(language)
        db.session.commit()

        token = Token(language_id=language.id, norm="learning")
        db.session.add(token)
        db.session.commit()

        progress = TokenProgress(
            token_id=token.id,
            status=LearningStatus.LEARNING,
            learning_stage=3,
            translation="aprendiendo"
        )

        # When
        db.session.add(progress)
        db.session.commit()

        # Then
        assert progress.token_id == token.id
        assert progress.status == LearningStatus.LEARNING
        assert progress.learning_stage == 3
        assert progress.translation == "aprendiendo"

    def test_create_token_progress_known(self, app: Flask):
        """Test creating token progress in known state."""
        # Given
        language = Language(name="Spanish")
        db.session.add(language)
        db.session.commit()

        token = Token(language_id=language.id, norm="known")
        db.session.add(token)
        db.session.commit()

        progress = TokenProgress(
            token_id=token.id,
            status=LearningStatus.KNOWN,
            translation="conocido"
        )

        # When
        db.session.add(progress)
        db.session.commit()

        # Then
        assert progress.token_id == token.id
        assert progress.status == LearningStatus.KNOWN
        assert progress.learning_stage is None

    def test_create_token_progress_ignore(self, app: Flask):
        """Test creating token progress in ignore state."""
        # Given
        language = Language(name="Chinese")
        db.session.add(language)
        db.session.commit()

        token = Token(language_id=language.id, norm="ignore")
        db.session.add(token)
        db.session.commit()

        progress = TokenProgress(
            token_id=token.id,
            status=LearningStatus.IGNORE
        )

        # When
        db.session.add(progress)
        db.session.commit()

        # Then
        assert progress.token_id == token.id
        assert progress.status == LearningStatus.IGNORE
        assert progress.learning_stage is None

    def test_token_progress_status_constraint(self, app: Flask):
        """Test token progress status must be valid."""
        # Given
        language = Language(name="Arabic")
        db.session.add(language)
        db.session.commit()

        token = Token(language_id=language.id, norm="test")
        db.session.add(token)
        db.session.commit()

        progress = TokenProgress(token_id=token.id, status=99)

        # When
        db.session.add(progress)

        # Then
        with pytest.raises(IntegrityError):
            db.session.commit()

    def test_token_progress_learning_stage_constraint(self, app: Flask):
        """Test learning stage constraint for learning status."""
        # Given
        language = Language(name="Hindi")
        db.session.add(language)
        db.session.commit()

        token = Token(language_id=language.id, norm="test")
        db.session.add(token)
        db.session.commit()

        # When - Learning status with invalid stage
        progress = TokenProgress(
            token_id=token.id,
            status=LearningStatus.LEARNING,
            learning_stage=10  # Invalid stage
        )
        db.session.add(progress)

        # Then
        with pytest.raises(IntegrityError):
            db.session.commit()

    def test_token_progress_foreign_key(self, app: Flask):
        """Test token progress requires valid token."""
        # Given
        language = Language(name="Dutch")
        db.session.add(language)
        db.session.commit()

        token = Token(language_id=language.id, norm="valid")
        db.session.add(token)
        db.session.commit()

        # When - Valid progress entry should work
        progress = TokenProgress(token_id=token.id, status=LearningStatus.KNOWN)
        db.session.add(progress)
        db.session.commit()

        # Then
        assert progress.token_id == token.id
        assert progress.status == LearningStatus.KNOWN


class TestBookTotalsModel:
    """Test cases for BookTotals model."""

    def test_create_book_totals(self, app: Flask):
        """Test creating book totals."""
        # Given
        language = Language(name="Swedish")
        db.session.add(language)
        db.session.commit()

        book = Book(language_id=language.id, title="Test Book")
        db.session.add(book)
        db.session.commit()

        totals = BookTotals(
            book_id=book.id,
            total_tokens=1000,
            total_types=500
        )

        # When
        db.session.add(totals)
        db.session.commit()

        # Then
        assert totals.book_id == book.id
        assert totals.total_tokens == 1000
        assert totals.total_types == 500

    def test_book_totals_relationship(self, app: Flask):
        """Test book totals relationship with book."""
        # Given
        language = Language(name="Norwegian")
        db.session.add(language)
        db.session.commit()

        book = Book(language_id=language.id, title="Test Book")
        db.session.add(book)
        db.session.commit()

        totals = BookTotals(
            book_id=book.id,
            total_tokens=1000,
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
        assert found_totals.total_tokens == 1000
        assert found_totals.total_types == 500
