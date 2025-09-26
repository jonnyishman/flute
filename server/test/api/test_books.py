"""Tests for book API endpoints."""
from __future__ import annotations

from datetime import datetime
from typing import TYPE_CHECKING

import pytest
import sqlalchemy as sa

from src.models import (
    Book,
    BookTotals,
    BookVocab,
    Chapter,
    LearningStatus,
    Term,
    TermProgress,
    db,
)

if TYPE_CHECKING:
    from flask.testing import FlaskClient

    from src.models.language import Language


class TestCreateBookEndpoint:
    """Test cases for POST /api/books endpoint."""

    def test_create_book_success_single_chapter(self, client: FlaskClient, english: Language) -> None:
        """Test successful book creation with a single chapter."""
        # Given
        request_data = {
            "title": "Test Book",
            "language_id": english.id,
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
        assert book.language_id == english.id
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
            sa.select(Term).where(Term.language_id == english.id)
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
            assert entry.term_count == 1

        # Verify book totals were created
        totals = db.session.execute(
            sa.select(BookTotals).where(BookTotals.book_id == book_id)
        ).scalar_one()
        assert totals.total_terms == 7
        assert totals.total_types == 7

    def test_create_book_success_multiple_chapters(self, client: FlaskClient, spanish: Language) -> None:
        """Test successful book creation with multiple chapters."""
        # Given
        request_data = {
            "title": "Multi Chapter Book",
            "language_id": spanish.id,
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
        assert totals.total_terms == 14  # 5 + 9

        # Verify unique token count (some words are repeated across chapters)
        vocab_count = db.session.execute(
            sa.select(sa.func.count()).select_from(BookVocab).where(BookVocab.book_id == book_id)
        ).scalar()
        assert totals.total_types == vocab_count

    def test_create_book_token_counts(self, client: FlaskClient, english: Language) -> None:
        """Test that token counts are calculated correctly for repeated words."""
        # Given
        request_data = {
            "title": "Repeated Words Book",
            "language_id": english.id,
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
            sa.select(BookVocab, Term)
            .join(Term, BookVocab.term_id == Term.id)
            .where(BookVocab.book_id == book_id)
        ).all()

        token_counts = {term.norm: vocab.term_count for vocab, term in vocab_entries}
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
        assert totals.total_terms == 10  # Total word count
        assert totals.total_types == 7   # Unique words

    def test_create_book_minimal_data(self, client: FlaskClient, english: Language) -> None:
        """Test book creation with minimal required data."""
        # Given
        request_data = {
            "title": "Minimal Book",
            "language_id": english.id,
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

    def test_create_book_empty_chapters(self, client: FlaskClient, english: Language) -> None:
        """Test book creation handles empty chapters correctly."""
        # Given
        request_data = {
            "title": "Empty Chapters Book",
            "language_id": english.id,
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

    def test_create_book_punctuation_handling(self, client: FlaskClient, english: Language) -> None:
        """Test that punctuation is properly stripped from tokens."""
        # Given
        request_data = {
            "title": "Punctuation Book",
            "language_id": english.id,
            "chapters": ["Hello, world! How are you? I am fine."]
        }

        # When
        response = client.post("/api/books", json=request_data)

        # Then
        assert response.status_code == 201

        tokens = list(db.session.execute(
            sa.select(Term).where(Term.language_id == english.id)
        ).scalars())
        token_norms = {token.norm for token in tokens}

        # Verify punctuation was stripped
        expected_tokens = {"hello", "world", "how", "are", "you", "i", "am", "fine"}
        assert token_norms == expected_tokens

    def test_create_book_case_normalization(self, client: FlaskClient, english: Language) -> None:
        """Test that tokens are normalized to lowercase."""
        # Given
        request_data = {
            "title": "Case Test Book",
            "language_id": english.id,
            "chapters": ["Hello WORLD This Is Mixed CaSe"]
        }

        # When
        response = client.post("/api/books", json=request_data)

        # Then
        assert response.status_code == 201

        tokens = list(db.session.execute(
            sa.select(Term).where(Term.language_id == english.id)
        ).scalars())
        token_norms = {token.norm for token in tokens}

        # All should be lowercase
        expected_tokens = {"hello", "world", "this", "is", "mixed", "case"}
        assert token_norms == expected_tokens

        # Verify no uppercase tokens exist
        for token in tokens:
            assert token.norm.islower()

    def test_create_book_missing_title(self, client: FlaskClient, english: Language) -> None:
        """Test validation error for missing title."""
        # Given
        request_data = {
            "language_id": english.id,
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

    def test_create_book_missing_chapters(self, client: FlaskClient, english: Language) -> None:
        """Test validation error for missing chapters."""
        # Given
        request_data = {
            "title": "Test Book",
            "language_id": english.id
        }

        # When
        response = client.post("/api/books", json=request_data)

        # Then
        assert response.status_code == 422  # Validation error

    def test_create_book_empty_chapters_list(self, client: FlaskClient, english: Language) -> None:
        """Test validation error for empty chapters list."""
        # Given
        request_data = {
            "title": "Test Book",
            "language_id": english.id,
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

    def test_create_book_existing_tokens(self, client: FlaskClient, english: Language) -> None:
        """Test that existing tokens are reused correctly."""
        # Given - Create a book with some tokens first
        first_request = {
            "title": "First Book",
            "language_id": english.id,
            "chapters": ["hello world"]
        }
        client.post("/api/books", json=first_request)

        # Get initial token count
        initial_token_count = db.session.execute(
            sa.select(sa.func.count()).select_from(Term).where(Term.language_id == english.id)
        ).scalar()
        assert initial_token_count == 2

        second_request = {
            "title": "Second Book",
            "language_id": english.id,
            "chapters": ["hello universe world"]  # "hello" and "world" already exist
        }

        # When
        response = client.post("/api/books", json=second_request)

        # Then
        assert response.status_code == 201

        # Verify token count only increased by 1 (for "universe")
        final_token_count = db.session.execute(
            sa.select(sa.func.count()).select_from(Term).where(Term.language_id == english.id)
        ).scalar()
        assert final_token_count == initial_token_count + 1

    def test_create_book_rollback_on_error(self, client: FlaskClient, english: Language) -> None:
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

    def test_create_book_response_structure(self, client: FlaskClient, english: Language) -> None:
        """Test that response has correct structure."""
        # Given
        request_data = {
            "title": "Response Test Book",
            "language_id": english.id,
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


@pytest.fixture
def books_with_progress(english: Language, spanish: Language) -> dict[str, int]:
    """Create test books with terms and progress for summaries testing."""
    # Create terms for both languages
    english_terms = [
        Term(norm="hello", display="hello", language_id=english.id, token_count=1),
        Term(norm="world", display="world", language_id=english.id, token_count=1),
        Term(norm="test", display="test", language_id=english.id, token_count=1),
        Term(norm="book", display="book", language_id=english.id, token_count=1),
        Term(norm="reading", display="reading", language_id=english.id, token_count=1),
    ]

    spanish_terms = [
        Term(norm="hola", display="hola", language_id=spanish.id, token_count=1),
        Term(norm="mundo", display="mundo", language_id=spanish.id, token_count=1),
        Term(norm="libro", display="libro", language_id=spanish.id, token_count=1),
    ]

    for term in english_terms + spanish_terms:
        db.session.add(term)
    db.session.flush()

    # Create books for different scenarios
    books = [
        # English books
        Book(
            title="Alpha Book",
            language_id=english.id,
            is_archived=False,
            last_read=datetime(2024, 1, 15),
        ),
        Book(
            title="Beta Book",
            language_id=english.id,
            is_archived=False,
            last_read=datetime(2024, 2, 10),
        ),
        Book(
            title="Gamma Book",
            language_id=english.id,
            is_archived=False,
            last_read=datetime(2024, 1, 5),
        ),
        Book(
            title="Archived Book",
            language_id=english.id,
            is_archived=True,
            last_read=datetime(2024, 1, 1),
        ),
        # Spanish books
        Book(
            title="Libro Español",
            language_id=spanish.id,
            is_archived=False,
            last_read=datetime(2024, 1, 20),
        ),
    ]

    for book in books:
        db.session.add(book)
    db.session.flush()

    # Create vocabulary mappings and progress
    # Alpha Book - 3 terms: 2 known, 1 learning, 0 unknown
    alpha_vocab = [
        BookVocab(book_id=books[0].id, term_id=english_terms[0].id, term_count=2),  # hello (known)
        BookVocab(book_id=books[0].id, term_id=english_terms[1].id, term_count=1),  # world (known)
        BookVocab(book_id=books[0].id, term_id=english_terms[2].id, term_count=1),  # test (learning)
    ]

    # Beta Book - 4 terms: 1 known, 2 learning, 1 unknown
    beta_vocab = [
        BookVocab(book_id=books[1].id, term_id=english_terms[0].id, term_count=1),  # hello (known)
        BookVocab(book_id=books[1].id, term_id=english_terms[2].id, term_count=2),  # test (learning)
        BookVocab(book_id=books[1].id, term_id=english_terms[3].id, term_count=1),  # book (learning)
        BookVocab(book_id=books[1].id, term_id=english_terms[4].id, term_count=1),  # reading (unknown)
    ]

    # Gamma Book - 2 terms: 0 known, 0 learning, 2 unknown
    gamma_vocab = [
        BookVocab(book_id=books[2].id, term_id=english_terms[3].id, term_count=3),  # book (unknown)
        BookVocab(book_id=books[2].id, term_id=english_terms[4].id, term_count=2),  # reading (unknown)
    ]

    # Archived Book - should not appear in results
    archived_vocab = [
        BookVocab(book_id=books[3].id, term_id=english_terms[0].id, term_count=1),  # hello
    ]

    # Spanish Book - 2 terms: 1 known, 1 learning
    spanish_vocab = [
        BookVocab(book_id=books[4].id, term_id=spanish_terms[0].id, term_count=1),  # hola (known)
        BookVocab(book_id=books[4].id, term_id=spanish_terms[1].id, term_count=1),  # mundo (learning)
    ]

    all_vocab = alpha_vocab + beta_vocab + gamma_vocab + archived_vocab + spanish_vocab
    for vocab in all_vocab:
        db.session.add(vocab)
    db.session.flush()

    # Create book totals
    book_totals = [
        BookTotals(book_id=books[0].id, total_terms=4, total_types=3),
        BookTotals(book_id=books[1].id, total_terms=5, total_types=4),
        BookTotals(book_id=books[2].id, total_terms=5, total_types=2),
        BookTotals(book_id=books[3].id, total_terms=1, total_types=1),
        BookTotals(book_id=books[4].id, total_terms=2, total_types=2),
    ]

    for total in book_totals:
        db.session.add(total)
    db.session.flush()

    # Create term progress
    progress_entries = [
        # Known terms
        TermProgress(term_id=english_terms[0].id, status=LearningStatus.KNOWN, learning_stage=5),
        TermProgress(term_id=english_terms[1].id, status=LearningStatus.KNOWN, learning_stage=5),
        TermProgress(term_id=spanish_terms[0].id, status=LearningStatus.KNOWN, learning_stage=4),

        # Learning terms
        TermProgress(term_id=english_terms[2].id, status=LearningStatus.LEARNING, learning_stage=2),
        TermProgress(term_id=english_terms[3].id, status=LearningStatus.LEARNING, learning_stage=1),
        TermProgress(term_id=spanish_terms[1].id, status=LearningStatus.LEARNING, learning_stage=3),
    ]

    for progress in progress_entries:
        db.session.add(progress)

    db.session.commit()

    return {
        "alpha_book_id": books[0].id,
        "beta_book_id": books[1].id,
        "gamma_book_id": books[2].id,
        "archived_book_id": books[3].id,
        "spanish_book_id": books[4].id,
        "english_id": english.id,
        "spanish_id": spanish.id,
    }


@pytest.fixture
def books_with_ignored_terms(english: Language, spanish: Language) -> dict[str, int]:
    """Create test books specifically for testing ignored terms functionality."""
    # Create additional terms for ignored terms testing
    english_terms = [
        Term(norm="ignore", display="ignore", language_id=english.id, token_count=1),
        Term(norm="skip", display="skip", language_id=english.id, token_count=1),
        Term(norm="review", display="review", language_id=english.id, token_count=1),
        Term(norm="study", display="study", language_id=english.id, token_count=1),
        Term(norm="common", display="common", language_id=english.id, token_count=1),
        Term(norm="word", display="word", language_id=english.id, token_count=1),
    ]

    for term in english_terms:
        db.session.add(term)
    db.session.flush()

    # Create books with different ignored term scenarios
    books = [
        # Delta Book - mixed statuses including ignored
        Book(
            title="Delta Book",
            language_id=english.id,
            is_archived=False,
            last_read=datetime(2024, 3, 1),
        ),
        # Epsilon Book - all terms ignored
        Book(
            title="Epsilon Book",
            language_id=english.id,
            is_archived=False,
            last_read=datetime(2024, 3, 5),
        ),
        # Zeta Book - no ignored terms (for backward compatibility)
        Book(
            title="Zeta Book",
            language_id=english.id,
            is_archived=False,
            last_read=datetime(2024, 3, 10),
        ),
    ]

    for book in books:
        db.session.add(book)
    db.session.flush()

    # Create vocabulary mappings
    # Delta Book - 6 terms: 1 known, 2 learning, 2 ignored, 1 unknown
    delta_vocab = [
        BookVocab(book_id=books[0].id, term_id=english_terms[0].id, term_count=3),  # ignore (ignored)
        BookVocab(book_id=books[0].id, term_id=english_terms[1].id, term_count=1),  # skip (ignored)
        BookVocab(book_id=books[0].id, term_id=english_terms[2].id, term_count=2),  # review (learning)
        BookVocab(book_id=books[0].id, term_id=english_terms[3].id, term_count=1),  # study (learning)
        BookVocab(book_id=books[0].id, term_id=english_terms[4].id, term_count=2),  # common (known)
        BookVocab(book_id=books[0].id, term_id=english_terms[5].id, term_count=1),  # word (unknown)
    ]

    # Epsilon Book - 2 terms: all ignored
    epsilon_vocab = [
        BookVocab(book_id=books[1].id, term_id=english_terms[0].id, term_count=2),  # ignore (ignored)
        BookVocab(book_id=books[1].id, term_id=english_terms[1].id, term_count=3),  # skip (ignored)
    ]

    # Zeta Book - 4 terms: 2 known, 1 learning, 1 unknown, 0 ignored
    zeta_vocab = [
        BookVocab(book_id=books[2].id, term_id=english_terms[2].id, term_count=1),  # review (learning)
        BookVocab(book_id=books[2].id, term_id=english_terms[3].id, term_count=2),  # study (known)
        BookVocab(book_id=books[2].id, term_id=english_terms[4].id, term_count=1),  # common (known)
        BookVocab(book_id=books[2].id, term_id=english_terms[5].id, term_count=3),  # word (unknown)
    ]

    all_vocab = delta_vocab + epsilon_vocab + zeta_vocab
    for vocab in all_vocab:
        db.session.add(vocab)
    db.session.flush()

    # Create book totals
    book_totals = [
        BookTotals(book_id=books[0].id, total_terms=10, total_types=6),  # Delta: 3+1+2+1+2+1=10
        BookTotals(book_id=books[1].id, total_terms=5, total_types=2),   # Epsilon: 2+3=5
        BookTotals(book_id=books[2].id, total_terms=7, total_types=4),   # Zeta: 1+2+1+3=7
    ]

    for total in book_totals:
        db.session.add(total)
    db.session.flush()

    # Create term progress (including ignored terms)
    progress_entries = [
        # Known terms
        TermProgress(term_id=english_terms[4].id, status=LearningStatus.KNOWN, learning_stage=5),  # common
        TermProgress(term_id=english_terms[3].id, status=LearningStatus.KNOWN, learning_stage=4),  # study

        # Learning terms
        TermProgress(term_id=english_terms[2].id, status=LearningStatus.LEARNING, learning_stage=2),  # review

        # Ignored terms
        TermProgress(term_id=english_terms[0].id, status=LearningStatus.IGNORE, learning_stage=1),  # ignore
        TermProgress(term_id=english_terms[1].id, status=LearningStatus.IGNORE, learning_stage=1),  # skip
    ]

    for progress in progress_entries:
        db.session.add(progress)

    db.session.commit()

    return {
        "delta_book_id": books[0].id,
        "epsilon_book_id": books[1].id,
        "zeta_book_id": books[2].id,
        "english_id": english.id,
        "ignore_term_id": english_terms[0].id,
        "skip_term_id": english_terms[1].id,
        "review_term_id": english_terms[2].id,
        "study_term_id": english_terms[3].id,
        "common_term_id": english_terms[4].id,
        "word_term_id": english_terms[5].id,
    }


class TestGetBookSummariesEndpoint:
    """Test cases for GET /api/books endpoint (book summaries)."""

    def test_get_book_summaries_default_params(self, client: FlaskClient, books_with_progress: dict[str, int]) -> None:
        """Test basic book summaries retrieval with default parameters."""
        # Given
        english_id = books_with_progress["english_id"]

        # When
        response = client.get(f"/api/books?language_id={english_id}")

        # Then
        assert response.status_code == 200
        data = response.get_json()
        assert "summaries" in data
        summaries = data["summaries"]
        assert len(summaries) == 3  # Only non-archived English books

        # Verify books are sorted by title (default)
        titles = [s["title"] for s in summaries]
        assert titles == ["Alpha Book", "Beta Book", "Gamma Book"]

        # Verify term counts for Alpha Book (first in alphabetical order)
        alpha_summary = summaries[0]
        assert alpha_summary["book_id"] == books_with_progress["alpha_book_id"]
        assert alpha_summary["title"] == "Alpha Book"
        assert alpha_summary["total_terms"] == 4
        assert alpha_summary["known_terms"] == 3  # hello(2) + world(1) = 3 term occurrences
        assert alpha_summary["learning_terms"] == 1  # test(1) = 1 term occurrence
        assert alpha_summary["unknown_terms"] == 0  # total - known - learning = 4-3-1 = 0

    def test_get_book_summaries_sort_by_learning_terms_desc(self, client: FlaskClient, books_with_progress: dict[str, int]) -> None:
        """Test sorting by learning terms in descending order."""
        # Given
        english_id = books_with_progress["english_id"]

        # When
        response = client.get(f"/api/books?language_id={english_id}&sort_option=learning_terms&sort_order=desc")

        # Then
        assert response.status_code == 200
        data = response.get_json()
        summaries = data["summaries"]

        # Should be ordered by learning_terms DESC: Beta(3), Gamma(3), Alpha(1)
        # When learning terms are equal (Beta=Gamma=3), secondary sort by title (B before G)
        learning_counts = [s["learning_terms"] for s in summaries]
        assert learning_counts == [3, 3, 1]
        assert summaries[0]["title"] == "Beta Book"   # 3 learning terms
        assert summaries[1]["title"] == "Gamma Book"  # 3 learning terms, "Gamma" > "Beta" alphabetically
        assert summaries[2]["title"] == "Alpha Book"  # 1 learning term

    def test_get_book_summaries_sort_by_unknown_terms_asc(self, client: FlaskClient, books_with_progress: dict[str, int]) -> None:
        """Test sorting by unknown terms in ascending order."""
        # Given
        english_id = books_with_progress["english_id"]

        # When
        response = client.get(f"/api/books?language_id={english_id}&sort_option=unknown_terms&sort_order=asc")

        # Then
        assert response.status_code == 200
        data = response.get_json()
        summaries = data["summaries"]

        # Should be ordered by unknown_terms ASC: Alpha(0), Beta(1), Gamma(2)
        unknown_counts = [s["unknown_terms"] for s in summaries]
        assert unknown_counts == [0, 1, 2]
        assert summaries[0]["title"] == "Alpha Book"  # 0 unknown terms
        assert summaries[1]["title"] == "Beta Book"   # 1 unknown term
        assert summaries[2]["title"] == "Gamma Book"  # 2 unknown terms

    def test_get_book_summaries_sort_by_last_read_desc(self, client: FlaskClient, books_with_progress: dict[str, int]) -> None:
        """Test sorting by last read date in descending order."""
        # Given
        english_id = books_with_progress["english_id"]

        # When
        response = client.get(f"/api/books?language_id={english_id}&sort_option=last_read&sort_order=desc")

        # Then
        assert response.status_code == 200
        data = response.get_json()
        summaries = data["summaries"]

        # Should be ordered by last_read DESC: Beta(2024-02-10), Alpha(2024-01-15), Gamma(2024-01-05)
        titles = [s["title"] for s in summaries]
        assert titles == ["Beta Book", "Alpha Book", "Gamma Book"]

    def test_get_book_summaries_pagination(self, client: FlaskClient, books_with_progress: dict[str, int]) -> None:
        """Test pagination with different page sizes."""
        # Given
        english_id = books_with_progress["english_id"]

        # When - First page with page size 2
        response = client.get(f"/api/books?language_id={english_id}&page=1&per_page=2")

        # Then
        assert response.status_code == 200
        data = response.get_json()
        summaries = data["summaries"]
        assert len(summaries) == 2
        assert summaries[0]["title"] == "Alpha Book"
        assert summaries[1]["title"] == "Beta Book"

        # When - Second page with page size 2
        response = client.get(f"/api/books?language_id={english_id}&page=2&per_page=2")

        # Then
        assert response.status_code == 200
        data = response.get_json()
        summaries = data["summaries"]
        assert len(summaries) == 1
        assert summaries[0]["title"] == "Gamma Book"

    def test_get_book_summaries_language_filtering(self, client: FlaskClient, books_with_progress: dict[str, int]) -> None:
        """Test that books are correctly filtered by language."""
        # Given
        spanish_id = books_with_progress["spanish_id"]

        # When
        response = client.get(f"/api/books?language_id={spanish_id}")

        # Then
        assert response.status_code == 200
        data = response.get_json()
        summaries = data["summaries"]
        assert len(summaries) == 1
        assert summaries[0]["title"] == "Libro Español"
        assert summaries[0]["known_terms"] == 1
        assert summaries[0]["learning_terms"] == 1
        assert summaries[0]["unknown_terms"] == 0

    def test_get_book_summaries_archived_books_excluded(self, client: FlaskClient, books_with_progress: dict[str, int]) -> None:
        """Test that archived books are excluded from results."""
        # Given
        english_id = books_with_progress["english_id"]

        # When
        response = client.get(f"/api/books?language_id={english_id}")

        # Then
        assert response.status_code == 200
        data = response.get_json()
        summaries = data["summaries"]

        # Verify archived book is not included
        titles = [s["title"] for s in summaries]
        assert "Archived Book" not in titles
        assert len(summaries) == 3  # Only non-archived books

    def test_get_book_summaries_no_books_for_language(self, client: FlaskClient, german: Language) -> None:
        """Test response when no books exist for specified language."""
        # Given - German language with no books

        # When
        response = client.get(f"/api/books?language_id={german.id}")

        # Then
        assert response.status_code == 200
        data = response.get_json()
        assert "summaries" in data
        assert data["summaries"] == []

    def test_get_book_summaries_no_progress_data(self, client: FlaskClient, english: Language) -> None:
        """Test book summaries when books have no term progress."""
        # Given - Create a book with no progress data
        book = Book(
            title="No Progress Book",
            language_id=english.id,
            is_archived=False,
        )
        db.session.add(book)
        db.session.flush()

        term = Term(norm="word", display="word", language_id=english.id, token_count=1)
        db.session.add(term)
        db.session.flush()

        vocab = BookVocab(book_id=book.id, term_id=term.id, term_count=3)
        db.session.add(vocab)

        totals = BookTotals(book_id=book.id, total_terms=3, total_types=1)
        db.session.add(totals)
        db.session.commit()

        # When
        response = client.get(f"/api/books?language_id={english.id}")

        # Then
        assert response.status_code == 200
        data = response.get_json()
        summaries = data["summaries"]

        # Find the book with no progress
        no_progress_book = next(s for s in summaries if s["title"] == "No Progress Book")
        assert no_progress_book["total_terms"] == 3
        assert no_progress_book["known_terms"] == 0
        assert no_progress_book["learning_terms"] == 0
        assert no_progress_book["unknown_terms"] == 3

    def test_get_book_summaries_missing_language_id(self, client: FlaskClient) -> None:
        """Test validation error when language_id is missing."""
        # Given - No language_id parameter

        # When
        response = client.get("/api/books")

        # Then
        assert response.status_code == 422  # Validation error

    def test_get_book_summaries_invalid_language_id(self, client: FlaskClient) -> None:
        """Test error handling for non-existent language_id."""
        # Given
        invalid_language_id = 99999

        # When
        response = client.get(f"/api/books?language_id={invalid_language_id}")

        # Then
        assert response.status_code == 200  # Should return empty results, not error
        data = response.get_json()
        assert data["summaries"] == []

    @pytest.mark.parametrize("sort_option", ["title", "last_read", "learning_terms", "unknown_terms"])
    def test_get_book_summaries_all_sort_options(self, client: FlaskClient, books_with_progress: dict[str, int], sort_option: str) -> None:
        """Test all valid sort options work correctly."""
        # Given
        english_id = books_with_progress["english_id"]

        # When
        response = client.get(f"/api/books?language_id={english_id}&sort_option={sort_option}")

        # Then
        assert response.status_code == 200
        data = response.get_json()
        assert "summaries" in data
        assert len(data["summaries"]) == 3

    @pytest.mark.parametrize("sort_order", ["asc", "desc"])
    def test_get_book_summaries_both_sort_orders(self, client: FlaskClient, books_with_progress: dict[str, int], sort_order: str) -> None:
        """Test both ascending and descending sort orders."""
        # Given
        english_id = books_with_progress["english_id"]

        # When
        response = client.get(f"/api/books?language_id={english_id}&sort_order={sort_order}")

        # Then
        assert response.status_code == 200
        data = response.get_json()
        summaries = data["summaries"]
        assert len(summaries) == 3

        # Verify ordering (default sort is by title)
        titles = [s["title"] for s in summaries]
        if sort_order == "asc":
            assert titles == ["Alpha Book", "Beta Book", "Gamma Book"]
        else:
            assert titles == ["Gamma Book", "Beta Book", "Alpha Book"]

    def test_get_book_summaries_invalid_sort_option(self, client: FlaskClient, books_with_progress: dict[str, int]) -> None:
        """Test handling of invalid sort option."""
        # Given
        english_id = books_with_progress["english_id"]

        # When
        response = client.get(f"/api/books?language_id={english_id}&sort_option=invalid_option")

        # Then
        assert response.status_code == 422  # Validation error

    def test_get_book_summaries_invalid_sort_order(self, client: FlaskClient, books_with_progress: dict[str, int]) -> None:
        """Test handling of invalid sort order."""
        # Given
        english_id = books_with_progress["english_id"]

        # When
        response = client.get(f"/api/books?language_id={english_id}&sort_order=invalid_order")

        # Then
        assert response.status_code == 422  # Validation error

    def test_get_book_summaries_invalid_pagination_params(self, client: FlaskClient, books_with_progress: dict[str, int]) -> None:
        """Test handling of invalid pagination parameters."""
        # Given
        english_id = books_with_progress["english_id"]

        test_cases = [
            {"page": 0, "per_page": 10},  # Invalid page (must be >= 1)
            {"page": 1, "per_page": 0},   # Invalid per_page (must be >= 1)
            {"page": 1, "per_page": 101}, # Invalid per_page (max 100)
        ]

        for params in test_cases:
            # When
            response = client.get(f"/api/books?language_id={english_id}&page={params['page']}&per_page={params['per_page']}")

            # Then
            assert response.status_code == 422  # Validation error

    def test_get_book_summaries_edge_case_pagination(self, client: FlaskClient, books_with_progress: dict[str, int]) -> None:
        """Test pagination edge cases."""
        # Given
        english_id = books_with_progress["english_id"]

        # When - Request page beyond available data
        response = client.get(f"/api/books?language_id={english_id}&page=10&per_page=10")

        # Then
        assert response.status_code == 200
        data = response.get_json()
        assert data["summaries"] == []  # Should return empty list

    def test_get_book_summaries_response_structure(self, client: FlaskClient, books_with_progress: dict[str, int]) -> None:
        """Test the structure of the response data."""
        # Given
        english_id = books_with_progress["english_id"]

        # When
        response = client.get(f"/api/books?language_id={english_id}")

        # Then
        assert response.status_code == 200
        assert response.content_type == "application/json"

        data = response.get_json()
        assert isinstance(data, dict)
        assert "summaries" in data
        assert isinstance(data["summaries"], list)

        # Verify each summary has correct structure
        for summary in data["summaries"]:
            assert isinstance(summary, dict)
            required_fields = [
                "book_id", "title", "cover_art_filepath",
                "total_terms", "known_terms", "learning_terms", "unknown_terms"
            ]
            for field in required_fields:
                assert field in summary

            # Verify data types
            assert isinstance(summary["book_id"], int)
            assert isinstance(summary["title"], str)
            assert isinstance(summary["total_terms"], int)
            assert isinstance(summary["known_terms"], int)
            assert isinstance(summary["learning_terms"], int)
            assert isinstance(summary["unknown_terms"], int)

    def test_get_book_summaries_term_count_consistency(self, client: FlaskClient, books_with_progress: dict[str, int]) -> None:
        """Test that term counts are mathematically consistent."""
        # Given
        english_id = books_with_progress["english_id"]

        # When
        response = client.get(f"/api/books?language_id={english_id}")

        # Then
        assert response.status_code == 200
        data = response.get_json()

        for summary in data["summaries"]:
            # Verify that known + learning + unknown <= total
            # (Equality holds only when no ignored terms are present)
            calculated_total = summary["known_terms"] + summary["learning_terms"] + summary["unknown_terms"]
            assert calculated_total <= summary["total_terms"], (
                f"Visible term count exceeds total for book {summary['title']}: "
                f"known({summary['known_terms']}) + learning({summary['learning_terms']}) + "
                f"unknown({summary['unknown_terms']}) = {calculated_total}, "
                f"but total_terms = {summary['total_terms']}"
            )

            # For the original fixture books (no ignored terms), they should be equal
            if summary["title"] in ["Alpha Book", "Beta Book", "Gamma Book"]:
                assert calculated_total == summary["total_terms"], (
                    f"Term count mismatch for book without ignored terms {summary['title']}: "
                    f"known({summary['known_terms']}) + learning({summary['learning_terms']}) + "
                    f"unknown({summary['unknown_terms']}) = {calculated_total}, "
                    f"but total_terms = {summary['total_terms']}"
                )


class TestGetBookSummariesIgnoredTerms:
    """Test cases for book summaries endpoint with ignored terms functionality."""

    def test_book_summaries_with_ignored_terms_basic(self, client: FlaskClient, books_with_ignored_terms: dict[str, int]) -> None:
        """Test book summaries calculation when books have ignored terms."""
        # Given
        english_id = books_with_ignored_terms["english_id"]

        # When
        response = client.get(f"/api/books?language_id={english_id}")

        # Then
        assert response.status_code == 200
        data = response.get_json()
        summaries = data["summaries"]
        assert len(summaries) == 3  # Delta, Epsilon, Zeta

        # Find each book by title
        delta_book = next(s for s in summaries if s["title"] == "Delta Book")
        epsilon_book = next(s for s in summaries if s["title"] == "Epsilon Book")
        zeta_book = next(s for s in summaries if s["title"] == "Zeta Book")

        # Verify Delta Book (mixed statuses with ignored terms)
        assert delta_book["book_id"] == books_with_ignored_terms["delta_book_id"]
        assert delta_book["total_terms"] == 10
        assert delta_book["known_terms"] == 3   # study(1) + common(2)
        assert delta_book["learning_terms"] == 2  # review(2)
        assert delta_book["unknown_terms"] == 1   # word(1) - ignored terms are subtracted

        # Verify Epsilon Book (all terms ignored)
        assert epsilon_book["book_id"] == books_with_ignored_terms["epsilon_book_id"]
        assert epsilon_book["total_terms"] == 5
        assert epsilon_book["known_terms"] == 0
        assert epsilon_book["learning_terms"] == 0
        assert epsilon_book["unknown_terms"] == 0  # All terms are ignored, so unknown = 0

        # Verify Zeta Book (no ignored terms - backward compatibility)
        assert zeta_book["book_id"] == books_with_ignored_terms["zeta_book_id"]
        assert zeta_book["total_terms"] == 7
        assert zeta_book["known_terms"] == 3   # study(2) + common(1)
        assert zeta_book["learning_terms"] == 1  # review(1)
        assert zeta_book["unknown_terms"] == 3   # word(3)

    def test_book_summaries_all_terms_ignored_edge_case(self, client: FlaskClient, books_with_ignored_terms: dict[str, int]) -> None:
        """Test edge case where all terms in a book are ignored."""
        # Given
        english_id = books_with_ignored_terms["english_id"]

        # When
        response = client.get(f"/api/books?language_id={english_id}&sort_option=title")

        # Then
        assert response.status_code == 200
        data = response.get_json()
        summaries = data["summaries"]

        epsilon_book = next(s for s in summaries if s["title"] == "Epsilon Book")

        # When all terms are ignored, unknown_terms should be 0
        assert epsilon_book["known_terms"] == 0
        assert epsilon_book["learning_terms"] == 0
        assert epsilon_book["unknown_terms"] == 0
        assert epsilon_book["total_terms"] == 5  # All 5 terms are ignored

    def test_book_summaries_no_ignored_terms_backward_compatibility(self, client: FlaskClient, books_with_ignored_terms: dict[str, int]) -> None:
        """Test that books with no ignored terms work the same as before."""
        # Given
        english_id = books_with_ignored_terms["english_id"]

        # When
        response = client.get(f"/api/books?language_id={english_id}")

        # Then
        assert response.status_code == 200
        data = response.get_json()
        summaries = data["summaries"]

        zeta_book = next(s for s in summaries if s["title"] == "Zeta Book")

        # Verify calculations work correctly when no ignored terms present
        calculated_total = zeta_book["known_terms"] + zeta_book["learning_terms"] + zeta_book["unknown_terms"]
        assert calculated_total == zeta_book["total_terms"]
        assert zeta_book["known_terms"] == 3
        assert zeta_book["learning_terms"] == 1
        assert zeta_book["unknown_terms"] == 3

    def test_book_summaries_term_count_consistency_with_ignored(self, client: FlaskClient, books_with_ignored_terms: dict[str, int]) -> None:
        """Test that term counts remain mathematically consistent when ignored terms are present."""
        # Given
        english_id = books_with_ignored_terms["english_id"]

        # When
        response = client.get(f"/api/books?language_id={english_id}")

        # Then
        assert response.status_code == 200
        data = response.get_json()

        for summary in data["summaries"]:
            # The key insight: known + learning + unknown + ignored = total
            # But the API only returns known + learning + unknown (ignored is internal)
            # So: known + learning + unknown <= total (with equality only when no ignored terms)
            visible_total = summary["known_terms"] + summary["learning_terms"] + summary["unknown_terms"]
            assert visible_total <= summary["total_terms"], (
                f"Visible term count exceeds total for book {summary['title']}: "
                f"known({summary['known_terms']}) + learning({summary['learning_terms']}) + "
                f"unknown({summary['unknown_terms']}) = {visible_total}, "
                f"but total_terms = {summary['total_terms']}"
            )

            # For books with no ignored terms, they should be equal
            if summary["title"] == "Zeta Book":
                assert visible_total == summary["total_terms"]

    def test_book_summaries_sorting_with_ignored_terms(self, client: FlaskClient, books_with_ignored_terms: dict[str, int]) -> None:
        """Test that sorting works correctly when ignored terms affect unknown_terms counts."""
        # Given
        english_id = books_with_ignored_terms["english_id"]

        # When - Sort by unknown terms ascending
        response = client.get(f"/api/books?language_id={english_id}&sort_option=unknown_terms&sort_order=asc")

        # Then
        assert response.status_code == 200
        data = response.get_json()
        summaries = data["summaries"]

        # Should be ordered by unknown_terms ASC: Epsilon(0), Delta(1), Zeta(3)
        unknown_counts = [s["unknown_terms"] for s in summaries]
        assert unknown_counts == [0, 1, 3]
        assert summaries[0]["title"] == "Epsilon Book"  # 0 unknown (all ignored)
        assert summaries[1]["title"] == "Delta Book"    # 1 unknown
        assert summaries[2]["title"] == "Zeta Book"     # 3 unknown

    def test_book_summaries_mixed_ignored_scenarios(self, client: FlaskClient, books_with_ignored_terms: dict[str, int]) -> None:
        """Test multiple books with different ignored term patterns."""
        # Given
        english_id = books_with_ignored_terms["english_id"]

        # When
        response = client.get(f"/api/books?language_id={english_id}&sort_option=learning_terms&sort_order=desc")

        # Then
        assert response.status_code == 200
        data = response.get_json()
        summaries = data["summaries"]

        # Should be ordered by learning_terms DESC: Delta(2), Zeta(1), Epsilon(0)
        learning_counts = [s["learning_terms"] for s in summaries]
        assert learning_counts == [2, 1, 0]

        # Verify each book maintains correct totals despite ignored terms
        for summary in summaries:
            assert summary["known_terms"] >= 0
            assert summary["learning_terms"] >= 0
            assert summary["unknown_terms"] >= 0
            assert summary["total_terms"] > 0

            # The sum of visible terms should never exceed total
            visible_sum = summary["known_terms"] + summary["learning_terms"] + summary["unknown_terms"]
            assert visible_sum <= summary["total_terms"]

    def test_book_summaries_pagination_with_ignored_terms(self, client: FlaskClient, books_with_ignored_terms: dict[str, int]) -> None:
        """Test that pagination works correctly with ignored terms present."""
        # Given
        english_id = books_with_ignored_terms["english_id"]

        # When - Get first page with page size 2
        response = client.get(f"/api/books?language_id={english_id}&page=1&per_page=2&sort_option=title")

        # Then
        assert response.status_code == 200
        data = response.get_json()
        summaries = data["summaries"]
        assert len(summaries) == 2

        # Verify first two books alphabetically
        assert summaries[0]["title"] == "Delta Book"
        assert summaries[1]["title"] == "Epsilon Book"

        # When - Get second page
        response = client.get(f"/api/books?language_id={english_id}&page=2&per_page=2&sort_option=title")

        # Then
        assert response.status_code == 200
        data = response.get_json()
        summaries = data["summaries"]
        assert len(summaries) == 1
        assert summaries[0]["title"] == "Zeta Book"


class TestGetChapterWithHighlights:
    """Test cases for GET /api/books/{book_id}/chapters/{chapter_number} endpoint."""

    def test_get_chapter_with_highlights_success(self, client: FlaskClient, english: Language) -> None:
        """Test successful retrieval of chapter with term highlights."""
        # Given - Create a book with chapters and user term progress
        book = Book(language_id=english.id, title="Test Book")
        db.session.add(book)
        db.session.flush()

        chapter = Chapter(
            book_id=book.id,
            chapter_number=1,
            content="The quick brown fox jumps over the lazy dog. The fox was very happy.",
            word_count=14
        )
        db.session.add(chapter)

        # Create terms with user progress
        term_the = Term(language_id=english.id, norm="the", display="the", token_count=1)
        term_fox = Term(language_id=english.id, norm="fox", display="Fox", token_count=1)
        term_happy = Term(language_id=english.id, norm="happy", display="happy", token_count=1)
        db.session.add_all([term_the, term_fox, term_happy])
        db.session.flush()

        # Add user progress
        progress_the = TermProgress(term_id=term_the.id, status=LearningStatus.KNOWN)
        progress_fox = TermProgress(term_id=term_fox.id, status=LearningStatus.LEARNING, learning_stage=2)
        progress_happy = TermProgress(term_id=term_happy.id, status=LearningStatus.IGNORE)
        db.session.add_all([progress_the, progress_fox, progress_happy])
        db.session.commit()

        # When
        response = client.get(f"/api/books/{book.id}/chapters/1")

        # Then
        assert response.status_code == 200
        data = response.get_json()

        # Verify chapter data
        chapter_data = data["chapter"]
        assert chapter_data["id"] == chapter.id
        assert chapter_data["chapter_number"] == 1
        assert chapter_data["word_count"] == 14
        assert "quick brown fox" in chapter_data["content"]

        # Verify highlights - should only include known/learning terms
        highlights = data["term_highlights"]
        assert {h["display"] for h in highlights} == {term_the.display, term_fox.display, term_happy.display}

        # Verify term positions
        the_highlights = sorted([h for h in highlights if h["display"] == term_the.display], key=lambda x: x["start_pos"])
        assert the_highlights == [
            {
                "term_id": term_the.id,
                "display": term_the.display,
                "status": LearningStatus.KNOWN,
                "learning_stage": None,
                "start_pos": start_pos,
                "end_pos": end_pos
            }
            for start_pos, end_pos in [(0, 3), (31, 34), (45, 48)]
        ]

        fox_highlights = sorted([h for h in highlights if h["display"] == term_fox.display], key=lambda x: x["start_pos"])
        assert fox_highlights == [
            {
                "term_id": term_fox.id,
                "display": term_fox.display,
                "status": LearningStatus.LEARNING,
                "learning_stage": 2,
                "start_pos": start_pos,
                "end_pos": end_pos
            }
            for start_pos, end_pos in [(16, 19), (49, 52)]
        ]

        happy_highlights = [h for h in highlights if h["display"] == term_happy.display]
        assert happy_highlights == [
            {
                "term_id": term_happy.id,
                "display": term_happy.display,
                "status": LearningStatus.IGNORE,
                "learning_stage": None,
                "start_pos": 62,
                "end_pos": 67
            }
        ]

    def test_get_chapter_with_multi_token_highlights(self, client: FlaskClient, english: Language) -> None:
        """Test chapter highlights with multi-token terms."""
        # Given - Create content with multi-token phrases
        book = Book(language_id=english.id, title="Multi-token Book")
        db.session.add(book)
        db.session.flush()

        chapter = Chapter(
            book_id=book.id,
            chapter_number=1,
            content="New York is a big city. I love New York very much.",
            word_count=12
        )
        db.session.add(chapter)

        # Create both single and multi-token terms
        term_new = Term(language_id=english.id, norm="new", display="New", token_count=1)
        term_york = Term(language_id=english.id, norm="york", display="York", token_count=1)
        term_new_york = Term(language_id=english.id, norm="new york", display="New York", token_count=2)
        term_big_city = Term(language_id=english.id, norm="big city", display="big city", token_count=2)
        db.session.add_all([term_new, term_york, term_new_york, term_big_city])
        db.session.flush()

        # Add progress for multi-token term and one single token
        progress_new_york = TermProgress(term_id=term_new_york.id, status=LearningStatus.KNOWN)
        progress_new = TermProgress(term_id=term_new.id, status=LearningStatus.LEARNING, learning_stage=1)
        progress_big_city = TermProgress(term_id=term_big_city.id, status=LearningStatus.LEARNING, learning_stage=3)
        db.session.add_all([progress_new_york, progress_new, progress_big_city])
        db.session.commit()

        # When
        response = client.get(f"/api/books/{book.id}/chapters/1")

        # Then
        assert response.status_code == 200
        data = response.get_json()
        highlights = data["term_highlights"]

        # Should prefer multi-token "New York" over individual "New" tokens
        new_york_highlights = [h for h in highlights if h["display"] == "New York"]
        assert len(new_york_highlights) == 2  # "New York" appears twice

        big_city_highlights = [h for h in highlights if h["display"] == "big city"]
        assert len(big_city_highlights) == 1

        # Individual "new" should not appear where covered by "New York"
        new_highlights = [h for h in highlights if h["display"] == "New"]
        assert len(new_highlights) == 0  # Should be covered by multi-token

        # Verify positions don't overlap
        positions = [(h["start_pos"], h["end_pos"]) for h in highlights]
        for i, (start1, end1) in enumerate(positions):
            for j, (start2, end2) in enumerate(positions):
                if i != j:
                    # No overlapping ranges
                    assert end1 <= start2 or end2 <= start1

    def test_boundaries(self, client: FlaskClient, english: Language) -> None:
        """Test chapter highlights obey token boundaries"""
        # Given - Create content with multi-token phrases
        book = Book(language_id=english.id, title="Multi-token Book")
        db.session.add(book)
        db.session.flush()

        chapter = Chapter(
            book_id=book.id,
            chapter_number=1,
            content="Pancakes do belong, but waffles do not.",
            word_count=7
        )
        db.session.add(chapter)

        # Create terms that should not be matched with the chatper, and one that can
        term_cake = Term(language_id=english.id, norm="cake", display="cake", token_count=1)
        term_long = Term(language_id=english.id, norm="long", display="Long", token_count=1)
        term_belong_bob = Term(language_id=english.id, norm="belong bob", display="Belong Bob", token_count=2)
        term_but_waffle = Term(language_id=english.id, norm="but waffle", display="but waffle", token_count=2)
        term_not = Term(language_id=english.id, norm="not", display="Not", token_count=1)
        db.session.add_all([term_cake, term_long, term_belong_bob, term_but_waffle, term_not])
        db.session.flush()

        # Add progress for multi-token term and one single token
        progress_belong_bob = TermProgress(term_id=term_belong_bob.id, status=LearningStatus.KNOWN)
        progress_cake = TermProgress(term_id=term_cake.id, status=LearningStatus.LEARNING, learning_stage=1)
        progress_long = TermProgress(term_id=term_long.id, status=LearningStatus.LEARNING, learning_stage=3)
        progress_but_waffle = TermProgress(term_id=term_but_waffle.id, status=LearningStatus.IGNORE)
        progress_not = TermProgress(term_id=term_not.id, status=LearningStatus.KNOWN)
        db.session.add_all([progress_belong_bob, progress_cake, progress_long, progress_but_waffle, progress_not])
        db.session.commit()

        # When
        response = client.get(f"/api/books/{book.id}/chapters/1")

        # Then
        assert response.status_code == 200
        data = response.get_json()
        assert data["term_highlights"] == [
            {
                "term_id": term_not.id,
                "display": term_not.display,
                "status": LearningStatus.KNOWN,
                "learning_stage": None,
                "start_pos": 35,
                "end_pos": 38
            }
        ]  # Only "not" should be highlighted

    def test_get_chapter_not_found(self, client: FlaskClient, english: Language) -> None:
        """Test retrieval of non-existent chapter."""
        # Given - Book without the requested chapter
        book = Book(language_id=english.id, title="Test Book")
        db.session.add(book)
        db.session.commit()

        # When
        response = client.get(f"/api/books/{book.id}/chapters/999")

        # Then
        assert response.status_code == 404
        data = response.get_json()
        assert "Chapter 999 not found" in data["msg"]

    def test_get_chapter_book_not_found(self, client: FlaskClient) -> None:
        """Test retrieval with non-existent book."""
        # When
        response = client.get("/api/books/999/chapters/1")

        # Then
        assert response.status_code == 404
        data = response.get_json()
        assert "Book 999 not found" in data["msg"]

    def test_get_chapter_no_user_progress(self, client: FlaskClient, english: Language) -> None:
        """Test chapter with no user term progress."""
        # Given - Chapter with no user progress on any terms
        book = Book(language_id=english.id, title="No Progress Book")
        db.session.add(book)
        db.session.flush()

        chapter = Chapter(
            book_id=book.id,
            chapter_number=1,
            content="Some random text without progress.",
            word_count=5
        )
        db.session.add(chapter)
        db.session.commit()

        # When
        response = client.get(f"/api/books/{book.id}/chapters/1")

        # Then
        assert response.status_code == 200
        data = response.get_json()
        assert data["chapter"]["content"] == "Some random text without progress."
        assert data["term_highlights"] == []

    @pytest.mark.parametrize("status", [LearningStatus.KNOWN, LearningStatus.LEARNING])
    def test_get_chapter_highlights_only_relevant_statuses(
        self, client: FlaskClient, english: Language, status: LearningStatus
    ) -> None:
        """Test that only known/learning terms are highlighted."""
        # Given - Terms with different statuses
        book = Book(language_id=english.id, title="Status Test Book")
        db.session.add(book)
        db.session.flush()

        chapter = Chapter(
            book_id=book.id,
            chapter_number=1,
            content="Test word here",
            word_count=3
        )
        db.session.add(chapter)

        term = Term(language_id=english.id, norm="test", display="Test", token_count=1)
        db.session.add(term)
        db.session.flush()

        progress = TermProgress(term_id=term.id, status=status, learning_stage=1)
        db.session.add(progress)
        db.session.commit()

        # When
        response = client.get(f"/api/books/{book.id}/chapters/1")

        # Then
        assert response.status_code == 200
        data = response.get_json()
        highlights = data["term_highlights"]

        if status in [LearningStatus.KNOWN, LearningStatus.LEARNING]:
            assert len(highlights) == 1
            assert highlights[0]["display"] == "Test"
            assert highlights[0]["status"] == status
        else:
            assert len(highlights) == 0

    def test_get_chapter_early_exit_no_multi_token_terms(self, client: FlaskClient, english: Language) -> None:
        """Test early exit optimization when user has no multi-token terms."""
        # Given - User with only single-token terms
        book = Book(language_id=english.id, title="Single Token Book")
        db.session.add(book)
        db.session.flush()

        chapter = Chapter(
            book_id=book.id,
            chapter_number=1,
            content="Simple test with only single words here.",
            word_count=7
        )
        db.session.add(chapter)

        # Create only single-token terms
        term1 = Term(language_id=english.id, norm="simple", display="Simple", token_count=1)
        term2 = Term(language_id=english.id, norm="test", display="test", token_count=1)
        db.session.add_all([term1, term2])
        db.session.flush()

        # Add progress for single tokens only
        progress1 = TermProgress(term_id=term1.id, status=LearningStatus.KNOWN)
        progress2 = TermProgress(term_id=term2.id, status=LearningStatus.LEARNING, learning_stage=1)
        db.session.add_all([progress1, progress2])
        db.session.commit()

        # When
        response = client.get(f"/api/books/{book.id}/chapters/1")

        # Then - Should work with early exit optimization
        assert response.status_code == 200
        data = response.get_json()
        highlights = data["term_highlights"]

        assert len(highlights) == 2
        highlight_displays = [h["display"] for h in highlights]
        assert "Simple" in highlight_displays
        assert "test" in highlight_displays

    def test_get_chapter_very_long_multi_token_term(self, client: FlaskClient, english: Language) -> None:
        """Test handling of very long multi-token terms (6+ tokens)."""
        # Given - Content with a long phrase
        book = Book(language_id=english.id, title="Long Phrase Book")
        db.session.add(book)
        db.session.flush()

        chapter = Chapter(
            book_id=book.id,
            chapter_number=1,
            content="The President of the United States of America spoke yesterday.",
            word_count=10
        )
        db.session.add(chapter)

        # Create a 7-token term that should be found with term-first approach
        long_term = Term(
            language_id=english.id,
            norm="president of the united states of america",
            display="President of the United States of America",
            token_count=7
        )
        db.session.add(long_term)
        db.session.flush()

        # Add progress
        progress = TermProgress(term_id=long_term.id, status=LearningStatus.LEARNING, learning_stage=2)
        db.session.add(progress)
        db.session.commit()

        # When
        response = client.get(f"/api/books/{book.id}/chapters/1")

        # Then - Should find the long term with term-first approach
        assert response.status_code == 200
        data = response.get_json()
        highlights = data["term_highlights"]

        assert len(highlights) == 1
        highlight = highlights[0]
        assert highlight["display"] == "President of the United States of America"
        assert highlight["status"] == LearningStatus.LEARNING

        # Verify the positions span the entire phrase
        content = data["chapter"]["content"]
        highlighted_text = content[highlight["start_pos"]:highlight["end_pos"]]
        assert "President" in highlighted_text
        assert "America" in highlighted_text


class TestGetBookCountEndpoint:
    """Test cases for GET /api/books/count endpoint."""

    def test_get_book_count_success(self, client: FlaskClient, english: Language) -> None:
        """Test successful book count retrieval for a language with books."""
        # Given - Create some unarchived books
        books = [
            Book(title="Book 1", language_id=english.id, is_archived=False),
            Book(title="Book 2", language_id=english.id, is_archived=False),
            Book(title="Book 3", language_id=english.id, is_archived=False),
        ]
        for book in books:
            db.session.add(book)
        db.session.commit()

        # When
        response = client.get(f"/api/books/count?language_id={english.id}")

        # Then
        assert response.status_code == 200
        data = response.get_json()
        assert "count" in data
        assert data["count"] == 3

    def test_get_book_count_excludes_archived(self, client: FlaskClient, spanish: Language) -> None:
        """Test that archived books are excluded from count."""
        # Given - Create mix of archived and unarchived books
        books = [
            Book(title="Active Book 1", language_id=spanish.id, is_archived=False),
            Book(title="Active Book 2", language_id=spanish.id, is_archived=False),
            Book(title="Archived Book 1", language_id=spanish.id, is_archived=True),
            Book(title="Archived Book 2", language_id=spanish.id, is_archived=True),
        ]
        for book in books:
            db.session.add(book)
        db.session.commit()

        # When
        response = client.get(f"/api/books/count?language_id={spanish.id}")

        # Then
        assert response.status_code == 200
        data = response.get_json()
        assert data["count"] == 2  # Only unarchived books

    def test_get_book_count_language_filtering(self, client: FlaskClient, english: Language, spanish: Language) -> None:
        """Test that books are correctly filtered by language."""
        # Given - Create books for different languages
        english_books = [
            Book(title="English Book 1", language_id=english.id, is_archived=False),
            Book(title="English Book 2", language_id=english.id, is_archived=False),
        ]
        spanish_books = [
            Book(title="Spanish Book 1", language_id=spanish.id, is_archived=False),
            Book(title="Spanish Book 2", language_id=spanish.id, is_archived=False),
            Book(title="Spanish Book 3", language_id=spanish.id, is_archived=False),
        ]
        for book in english_books + spanish_books:
            db.session.add(book)
        db.session.commit()

        # When - Check English books
        response = client.get(f"/api/books/count?language_id={english.id}")

        # Then
        assert response.status_code == 200
        data = response.get_json()
        assert data["count"] == 2

        # When - Check Spanish books
        response = client.get(f"/api/books/count?language_id={spanish.id}")

        # Then
        assert response.status_code == 200
        data = response.get_json()
        assert data["count"] == 3

    def test_get_book_count_no_books(self, client: FlaskClient, german: Language) -> None:
        """Test book count when no books exist for the language."""
        # Given - No books for German language

        # When
        response = client.get(f"/api/books/count?language_id={german.id}")

        # Then
        assert response.status_code == 200
        data = response.get_json()
        assert data["count"] == 0

    def test_get_book_count_missing_language_id(self, client: FlaskClient) -> None:
        """Test validation error when language_id is missing."""
        # When
        response = client.get("/api/books/count")

        # Then
        assert response.status_code == 422  # Validation error

    def test_get_book_count_invalid_language_id_type(self, client: FlaskClient) -> None:
        """Test validation error for invalid language_id type."""
        # When
        response = client.get("/api/books/count?language_id=invalid")

        # Then
        assert response.status_code == 422  # Validation error

    def test_get_book_count_nonexistent_language_id(self, client: FlaskClient) -> None:
        """Test response for non-existent language_id."""
        # When
        response = client.get("/api/books/count?language_id=99999")

        # Then
        assert response.status_code == 200  # Should return 0, not error
        data = response.get_json()
        assert data["count"] == 0

    def test_get_book_count_response_structure(self, client: FlaskClient, english: Language) -> None:
        """Test that response has correct structure."""
        # Given
        book = Book(title="Test Book", language_id=english.id, is_archived=False)
        db.session.add(book)
        db.session.commit()

        # When
        response = client.get(f"/api/books/count?language_id={english.id}")

        # Then
        assert response.status_code == 200
        assert response.content_type == "application/json"

        data = response.get_json()
        assert isinstance(data, dict)
        assert "count" in data
        assert isinstance(data["count"], int)
        assert data["count"] >= 0

    def test_get_book_count_large_number(self, client: FlaskClient, english: Language) -> None:
        """Test book count with a larger number of books."""
        # Given - Create many books
        books = [
            Book(title=f"Book {i}", language_id=english.id, is_archived=False)
            for i in range(50)
        ]
        # Add some archived books that shouldn't be counted
        archived_books = [
            Book(title=f"Archived Book {i}", language_id=english.id, is_archived=True)
            for i in range(10)
        ]

        for book in books + archived_books:
            db.session.add(book)
        db.session.commit()

        # When
        response = client.get(f"/api/books/count?language_id={english.id}")

        # Then
        assert response.status_code == 200
        data = response.get_json()
        assert data["count"] == 50  # Only unarchived books

