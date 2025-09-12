"""Tests for book API endpoints."""
from __future__ import annotations

from typing import TYPE_CHECKING
from unittest.mock import patch

import pytest
import sqlalchemy as sa

from src.models import Book, BookTotals, BookVocab, Chapter, Token, db
from src.models.language import Language

if TYPE_CHECKING:
    from unittest.mock import Mock

    from flask import Flask
    from flask.testing import FlaskClient


@pytest.fixture
def language(app: Flask) -> Language:
    """Create a test language."""
    language = Language(name="English")
    db.session.add(language)
    db.session.commit()
    return language


class TestCreateBookEndpoint:
    """Test cases for POST /api/books endpoint."""

    def test_create_book_success_single_chapter(self, client: FlaskClient, language: Language) -> None:
        """Test successful book creation with a single chapter."""
        # Given
        request_data = {
            "title": "Test Book",
            "language_id": language.id,
            "chapters": ["Hello world! This is a test chapter."],
            "source": "Test Source",
            "cover_art_filepath": "/path/to/cover.jpg"
        }

        # When
        response = client.post("/api/books", json=request_data)

        # Then
        assert response.status_code == 201
        data = response.get_json()
        assert "book_id" in data
        book_id = data["book_id"]

        # Verify book was created
        book = db.session.execute(
            sa.select(Book).where(Book.id == book_id)
        ).scalar_one()
        assert book.title == "Test Book"
        assert book.language_id == language.id
        assert book.source == "Test Source"
        assert book.cover_art_filepath == "/path/to/cover.jpg"
        assert book.is_archived is False

        # Verify chapter was created
        chapters = list(db.session.execute(
            sa.select(Chapter).where(Chapter.book_id == book_id)
        ).scalars())
        assert len(chapters) == 1
        assert chapters[0].chapter_number == 1
        assert chapters[0].content == "Hello world! This is a test chapter."
        assert chapters[0].word_count == 7  # "hello world this is a test chapter"

        # Verify tokens were created
        tokens = list(db.session.execute(
            sa.select(Token).where(Token.language_id == language.id)
        ).scalars())
        token_norms = {token.norm for token in tokens}
        expected_tokens = {"hello", "world", "this", "is", "a", "test", "chapter"}
        assert token_norms == expected_tokens

        # Verify book vocab was created
        vocab_entries = list(db.session.execute(
            sa.select(BookVocab).where(BookVocab.book_id == book_id)
        ).scalars())
        assert len(vocab_entries) == 7

        # Verify each token appears once
        for entry in vocab_entries:
            assert entry.token_count == 1

        # Verify book totals were created
        totals = db.session.execute(
            sa.select(BookTotals).where(BookTotals.book_id == book_id)
        ).scalar_one()
        assert totals.total_tokens == 7
        assert totals.total_types == 7

    def test_create_book_success_multiple_chapters(self, client: FlaskClient, language: Language) -> None:
        """Test successful book creation with multiple chapters."""
        # Given
        request_data = {
            "title": "Multi Chapter Book",
            "language_id": language.id,
            "chapters": [
                "First chapter with some words.",
                "Second chapter with more words and some repeated words."
            ]
        }

        # When
        response = client.post("/api/books", json=request_data)

        # Then
        assert response.status_code == 201
        data = response.get_json()
        book_id = data["book_id"]

        # Verify chapters were created
        chapters = list(db.session.execute(
            sa.select(Chapter)
            .where(Chapter.book_id == book_id)
            .order_by(Chapter.chapter_number)
        ).scalars())
        assert len(chapters) == 2
        assert chapters[0].chapter_number == 1
        assert chapters[0].content == "First chapter with some words."
        assert chapters[0].word_count == 5
        assert chapters[1].chapter_number == 2
        assert chapters[1].content == "Second chapter with more words and some repeated words."
        assert chapters[1].word_count == 9

        # Verify book totals account for all tokens
        totals = db.session.execute(
            sa.select(BookTotals).where(BookTotals.book_id == book_id)
        ).scalar_one()
        assert totals.total_tokens == 14  # 5 + 9

        # Verify unique token count (some words are repeated across chapters)
        vocab_count = db.session.execute(
            sa.select(sa.func.count()).select_from(BookVocab).where(BookVocab.book_id == book_id)
        ).scalar()
        assert totals.total_types == vocab_count

    def test_create_book_token_counts(self, client: FlaskClient, language: Language) -> None:
        """Test that token counts are calculated correctly for repeated words."""
        # Given
        request_data = {
            "title": "Repeated Words Book",
            "language_id": language.id,
            "chapters": ["the cat sat on the mat the cat was happy"]
        }

        # When
        response = client.post("/api/books", json=request_data)

        # Then
        assert response.status_code == 201
        data = response.get_json()
        book_id = data["book_id"]

        # Verify token counts
        vocab_entries = db.session.execute(
            sa.select(BookVocab, Token)
            .join(Token, BookVocab.token_id == Token.id)
            .where(BookVocab.book_id == book_id)
        ).all()

        token_counts = {token.norm: vocab.token_count for vocab, token in vocab_entries}
        assert token_counts["the"] == 3
        assert token_counts["cat"] == 2
        assert token_counts["sat"] == 1
        assert token_counts["on"] == 1
        assert token_counts["mat"] == 1
        assert token_counts["was"] == 1
        assert token_counts["happy"] == 1

        # Verify totals
        totals = db.session.execute(
            sa.select(BookTotals).where(BookTotals.book_id == book_id)
        ).scalar_one()
        assert totals.total_tokens == 10  # Total word count
        assert totals.total_types == 7   # Unique words

    def test_create_book_minimal_data(self, client: FlaskClient, language: Language) -> None:
        """Test book creation with minimal required data."""
        # Given
        request_data = {
            "title": "Minimal Book",
            "language_id": language.id,
            "chapters": ["Simple content."]
        }

        # When
        response = client.post("/api/books", json=request_data)

        # Then
        assert response.status_code == 201
        data = response.get_json()
        book_id = data["book_id"]

        book = db.session.execute(
            sa.select(Book).where(Book.id == book_id)
        ).scalar_one()
        assert book.title == "Minimal Book"
        assert book.source is None
        assert book.cover_art_filepath is None

    def test_create_book_empty_chapters(self, client: FlaskClient, language: Language) -> None:
        """Test book creation handles empty chapters correctly."""
        # Given
        request_data = {
            "title": "Empty Chapters Book",
            "language_id": language.id,
            "chapters": ["", "   ", "actual content here"]
        }

        # When
        response = client.post("/api/books", json=request_data)

        # Then
        assert response.status_code == 201
        data = response.get_json()
        book_id = data["book_id"]

        chapters = list(db.session.execute(
            sa.select(Chapter)
            .where(Chapter.book_id == book_id)
            .order_by(Chapter.chapter_number)
        ).scalars())
        assert len(chapters) == 3
        assert chapters[0].word_count == 0  # Empty content
        assert chapters[1].word_count == 0  # Whitespace only
        assert chapters[2].word_count == 3  # "actual content here"

    def test_create_book_punctuation_handling(self, client: FlaskClient, language: Language) -> None:
        """Test that punctuation is properly stripped from tokens."""
        # Given
        request_data = {
            "title": "Punctuation Book",
            "language_id": language.id,
            "chapters": ["Hello, world! How are you? I'm fine."]
        }

        # When
        response = client.post("/api/books", json=request_data)

        # Then
        assert response.status_code == 201

        tokens = list(db.session.execute(
            sa.select(Token).where(Token.language_id == language.id)
        ).scalars())
        token_norms = {token.norm for token in tokens}

        # Verify punctuation was stripped
        expected_tokens = {"hello", "world", "how", "are", "you", "i'm", "fine"}
        assert token_norms == expected_tokens

    def test_create_book_case_normalization(self, client: FlaskClient, language: Language) -> None:
        """Test that tokens are normalized to lowercase."""
        # Given
        request_data = {
            "title": "Case Test Book",
            "language_id": language.id,
            "chapters": ["Hello WORLD This Is Mixed CaSe"]
        }

        # When
        response = client.post("/api/books", json=request_data)

        # Then
        assert response.status_code == 201

        tokens = list(db.session.execute(
            sa.select(Token).where(Token.language_id == language.id)
        ).scalars())
        token_norms = {token.norm for token in tokens}

        # All should be lowercase
        expected_tokens = {"hello", "world", "this", "is", "mixed", "case"}
        assert token_norms == expected_tokens

        # Verify no uppercase tokens exist
        for token in tokens:
            assert token.norm.islower()

    def test_create_book_missing_title(self, client: FlaskClient, language: Language) -> None:
        """Test validation error for missing title."""
        # Given
        request_data = {
            "language_id": language.id,
            "chapters": ["Some content"]
        }

        # When
        response = client.post("/api/books", json=request_data)

        # Then
        assert response.status_code == 422  # Validation error

    def test_create_book_missing_language_id(self, client: FlaskClient) -> None:
        """Test validation error for missing language_id."""
        # Given
        request_data = {
            "title": "Test Book",
            "chapters": ["Some content"]
        }

        # When
        response = client.post("/api/books", json=request_data)

        # Then
        assert response.status_code == 422  # Validation error

    def test_create_book_missing_chapters(self, client: FlaskClient, language: Language) -> None:
        """Test validation error for missing chapters."""
        # Given
        request_data = {
            "title": "Test Book",
            "language_id": language.id
        }

        # When
        response = client.post("/api/books", json=request_data)

        # Then
        assert response.status_code == 422  # Validation error

    def test_create_book_empty_chapters_list(self, client: FlaskClient, language: Language) -> None:
        """Test validation error for empty chapters list."""
        # Given
        request_data = {
            "title": "Test Book",
            "language_id": language.id,
            "chapters": []
        }

        # When
        response = client.post("/api/books", json=request_data)

        # Then
        assert response.status_code == 201  # Should still succeed
        data = response.get_json()
        book_id = data["book_id"]

        # Verify no chapters were created
        chapter_count = db.session.execute(
            sa.select(sa.func.count()).select_from(Chapter).where(Chapter.book_id == book_id)
        ).scalar()
        assert chapter_count == 0

    def test_create_book_invalid_language_id(self, client: FlaskClient) -> None:
        """Test error handling for non-existent language_id."""
        # Given
        request_data = {
            "title": "Test Book",
            "language_id": 99999,  # Non-existent language
            "chapters": ["Some content"]
        }

        # When
        response = client.post("/api/books", json=request_data)

        # Then
        assert response.status_code == 404
        assert response.json == {"error": "Not Found", "msg": "invalid language_id: '99999'"}

    def test_create_book_existing_tokens(self, client: FlaskClient, language: Language) -> None:
        """Test that existing tokens are reused correctly."""
        # Given - Create a book with some tokens first
        first_request = {
            "title": "First Book",
            "language_id": language.id,
            "chapters": ["hello world"]
        }
        client.post("/api/books", json=first_request)

        # Get initial token count
        initial_token_count = db.session.execute(
            sa.select(sa.func.count()).select_from(Token).where(Token.language_id == language.id)
        ).scalar()
        assert initial_token_count == 2

        second_request = {
            "title": "Second Book",
            "language_id": language.id,
            "chapters": ["hello universe world"]  # "hello" and "world" already exist
        }

        # When
        response = client.post("/api/books", json=second_request)

        # Then
        assert response.status_code == 201

        # Verify token count only increased by 1 (for "universe")
        final_token_count = db.session.execute(
            sa.select(sa.func.count()).select_from(Token).where(Token.language_id == language.id)
        ).scalar()
        assert final_token_count == initial_token_count + 1

    def test_create_book_large_batch_chunking(self, client: FlaskClient, language: Language) -> None:
        """Test that large token batches are properly chunked."""
        # Given - Create content with many unique tokens to test chunking
        # Generate 600+ unique words to exceed the 500 chunk size
        words = [f"word{i}" for i in range(650)]
        content = " ".join(words)

        request_data = {
            "title": "Large Batch Book",
            "language_id": language.id,
            "chapters": [content]
        }

        # When
        response = client.post("/api/books", json=request_data)

        # Then
        assert response.status_code == 201
        data = response.get_json()
        book_id = data["book_id"]

        # Verify all tokens were created
        token_count = db.session.execute(
            sa.select(sa.func.count()).select_from(Token).where(Token.language_id == language.id)
        ).scalar()
        assert token_count == 650

        # Verify book vocab entries were created
        vocab_count = db.session.execute(
            sa.select(sa.func.count()).select_from(BookVocab).where(BookVocab.book_id == book_id)
        ).scalar()
        assert vocab_count == 650

    @patch('src.api.books.tokenise_and_count')
    def test_create_book_tokenizer_called(self, mock_tokenize: Mock, client: FlaskClient, language: Language) -> None:
        """Test that the tokenizer function is called for each chapter."""
        # Given
        mock_tokenize.side_effect = [
            {"hello": 1, "world": 1},
            {"foo": 1, "bar": 1}
        ]

        request_data = {
            "title": "Tokenizer Test Book",
            "language_id": language.id,
            "chapters": ["hello world", "foo bar"]
        }

        # When
        response = client.post("/api/books", json=request_data)

        # Then
        assert response.status_code == 201
        assert mock_tokenize.call_count == 2
        mock_tokenize.assert_any_call("hello world")
        mock_tokenize.assert_any_call("foo bar")

    def test_create_book_rollback_on_error(self, client: FlaskClient, language: Language) -> None:
        """Test that database changes are rolled back on error."""
        # Given - Create initial state
        initial_book_count = db.session.execute(
            sa.select(sa.func.count()).select_from(Book)
        ).scalar()

        request_data = {
            "title": "Test Book",
            "language_id": 99999,  # Invalid language_id to trigger error
            "chapters": ["Some content"]
        }

        # When
        response = client.post("/api/books", json=request_data)

        # Then
        assert response.status_code == 404

        # Verify no book was created
        final_book_count = db.session.execute(
            sa.select(sa.func.count()).select_from(Book)
        ).scalar()
        assert final_book_count == initial_book_count

    def test_create_book_response_structure(self, client: FlaskClient, language: Language) -> None:
        """Test that response has correct structure."""
        # Given
        request_data = {
            "title": "Response Test Book",
            "language_id": language.id,
            "chapters": ["test content"]
        }

        # When
        response = client.post("/api/books", json=request_data)

        # Then
        assert response.status_code == 201
        assert response.content_type == "application/json"

        data = response.get_json()
        assert isinstance(data, dict)
        assert "book_id" in data
        assert isinstance(data["book_id"], int)
        assert data["book_id"] > 0

