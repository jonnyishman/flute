"""Tests for term API endpoints."""
from __future__ import annotations

from typing import TYPE_CHECKING

import sqlalchemy as sa

from src.models import LearningStatus, Term, TermProgress, db

if TYPE_CHECKING:
    from flask.testing import FlaskClient

    from src.models.language import Language


class TestCreateTermEndpoint:
    """Test cases for POST /api/terms endpoint."""

    def test_create_term_success_minimal(self, client: FlaskClient, english: Language) -> None:
        """Test successful term creation with minimal required fields."""
        # Given
        request_data = {
            "term": "hello",
            "language_id": english.id,
            "status": LearningStatus.LEARNING,
            "learning_stage": 1  # explicit default
        }

        # When
        response = client.post("/api/terms", json=request_data)

        # Then
        assert response.status_code == 200
        response_data = response.json
        assert "term_id" in response_data
        term_id = response_data["term_id"]

        # Verify term was created
        term = db.session.execute(
            sa.select(Term).where(Term.id == term_id)
        ).scalar_one()
        assert term.norm == "hello"
        assert term.display == "hello"  # defaults to term when display not provided
        assert term.language_id == english.id
        assert term.token_count == 1

        # Verify term progress was created
        progress = db.session.execute(
            sa.select(TermProgress).where(TermProgress.term_id == term_id)
        ).scalar_one()
        assert progress.status == LearningStatus.LEARNING
        assert progress.learning_stage == 1  # default value
        assert progress.translation is None

    def test_multiterm(self, client: FlaskClient, english: Language) -> None:
        """Test successful term creation with minimal required fields."""
        # Given
        request_data = {
            "term": "Hello you.",
            "language_id": english.id,
            "status": LearningStatus.LEARNING,
            "learning_stage": 1  # explicit default
        }

        # When
        response = client.post("/api/terms", json=request_data)

        # Then
        assert response.status_code == 200
        response_data = response.json
        assert "term_id" in response_data
        term_id = response_data["term_id"]

        # Verify term was created
        term = db.session.execute(
            sa.select(Term).where(Term.id == term_id)
        ).scalar_one()
        assert term.norm == "hello you."
        assert term.display == "Hello you."
        assert term.language_id == english.id
        assert term.token_count == 2

        # Verify term progress was created
        progress = db.session.execute(
            sa.select(TermProgress).where(TermProgress.term_id == term_id)
        ).scalar_one()
        assert progress.status == LearningStatus.LEARNING
        assert progress.learning_stage == 1  # default value
        assert progress.translation is None

    def test_create_term_success_all_fields(self, client: FlaskClient, english: Language) -> None:
        """Test successful term creation with all fields provided."""
        # Given
        request_data = {
            "term": "Hello",
            "language_id": english.id,
            "status": LearningStatus.KNOWN,
            "learning_stage": 3,
            "display": "hello",
            "translation": "greeting"
        }

        # When
        response = client.post("/api/terms", json=request_data)

        # Then
        assert response.status_code == 200
        response_data = response.json
        term_id = response_data["term_id"]

        # Verify term was created with correct values
        term = db.session.execute(
            sa.select(Term).where(Term.id == term_id)
        ).scalar_one()
        assert term.norm == "hello"  # normalized from "Hello"
        assert term.display == "hello"  # explicit display value
        assert term.language_id == english.id
        assert term.token_count == 1

        # Verify term progress
        progress = db.session.execute(
            sa.select(TermProgress).where(TermProgress.term_id == term_id)
        ).scalar_one()
        assert progress.status == LearningStatus.KNOWN
        assert progress.learning_stage == 3
        assert progress.translation == "greeting"

    def test_create_term_upsert_existing_term(self, client: FlaskClient, english: Language) -> None:
        """Test that creating an existing term updates it (upsert behavior)."""
        # Given - Create initial term
        existing_term = Term(
            norm="world",
            display="World",
            language_id=english.id,
            token_count=1
        )
        db.session.add(existing_term)
        db.session.commit()
        existing_term_id = existing_term.id

        request_data = {
            "term": "WORLD",  # Different case, same normalized form
            "language_id": english.id,
            "status": LearningStatus.LEARNING,
            "display": "world",  # Update display
            "translation": "the planet"
        }

        # When
        response = client.post("/api/terms", json=request_data)

        # Then
        assert response.status_code == 200
        response_data = response.json
        returned_term_id = response_data["term_id"]
        assert returned_term_id == existing_term_id  # Same term ID returned

        # Verify term display was updated
        updated_term = db.session.execute(
            sa.select(Term).where(Term.id == existing_term_id)
        ).scalar_one()
        assert updated_term.display == "world"  # Updated display
        assert updated_term.norm == "world"  # Norm unchanged

        # Verify term progress was created
        progress = db.session.execute(
            sa.select(TermProgress).where(TermProgress.term_id == existing_term_id)
        ).scalar_one()
        assert progress.status == LearningStatus.LEARNING
        assert progress.translation == "the planet"

    def test_create_term_upsert_existing_without_display_update(self, client: FlaskClient, english: Language) -> None:
        """Test upsert behavior when display is not provided - should not update existing display."""
        # Given
        existing_term = Term(
            norm="test",
            display="TEST",
            language_id=english.id,
            token_count=1
        )
        db.session.add(existing_term)
        db.session.commit()
        existing_term_id = existing_term.id

        request_data = {
            "term": "test",
            "language_id": english.id,
            "status": LearningStatus.KNOWN
            # No display provided
        }

        # When
        response = client.post("/api/terms", json=request_data)

        # Then
        assert response.status_code == 200
        response_data = response.json
        returned_term_id = response_data["term_id"]
        assert returned_term_id == existing_term_id

        # Verify original display was preserved
        updated_term = db.session.execute(
            sa.select(Term).where(Term.id == existing_term_id)
        ).scalar_one()
        assert updated_term.display == "TEST"  # Original display preserved

    def test_create_term_invalid_language_id(self, client: FlaskClient) -> None:
        """Test error handling for non-existent language_id."""
        # Given
        request_data = {
            "term": "hello",
            "language_id": 99999,
            "status": LearningStatus.LEARNING
        }

        # When
        response = client.post("/api/terms", json=request_data)

        # Then
        assert response.status_code == 404
        assert response.json == {"error": "Not Found", "msg": "invalid language_id: '99999'"}

    def test_create_term_invalid_display_normalization(self, client: FlaskClient, english: Language) -> None:
        """Test error when display doesn't match normalized form."""
        # Given
        request_data = {
            "term": "hello",
            "language_id": english.id,
            "status": LearningStatus.LEARNING,
            "display": "goodbye"  # Doesn't normalize to "hello"
        }

        # When
        response = client.post("/api/terms", json=request_data)

        # Then
        assert response.status_code == 400
        assert response.json == {
            "error": "Bad Request",
            "msg": "display must match the term's normalized form"
        }

    def test_create_term_display_case_changes_allowed(self, client: FlaskClient, english: Language) -> None:
        """Test that display case changes are allowed if they normalize to the same form."""
        # Given
        request_data = {
            "term": "hello",
            "language_id": english.id,
            "status": LearningStatus.LEARNING,
            "display": "HELLO"  # Same normalized form, different case
        }

        # When
        response = client.post("/api/terms", json=request_data)

        # Then
        assert response.status_code == 200
        response_data = response.json
        term_id = response_data["term_id"]

        # Verify display was stored correctly
        term = db.session.execute(
            sa.select(Term).where(Term.id == term_id)
        ).scalar_one()
        assert term.display == "HELLO"
        assert term.norm == "hello"

    def test_create_term_missing_required_fields(self, client: FlaskClient) -> None:
        """Test validation errors for missing required fields."""
        test_cases = [
            {},  # All fields missing
            {"term": "hello"},  # Missing language_id and status
            {"language_id": 1},  # Missing term and status
            {"status": LearningStatus.LEARNING},  # Missing term and language_id
            {"term": "hello", "language_id": 1},  # Missing status
            {"term": "hello", "status": LearningStatus.LEARNING},  # Missing language_id
        ]

        for request_data in test_cases:
            # When
            response = client.post("/api/terms", json=request_data)

            # Then
            assert response.status_code == 422  # Validation error

    def test_create_term_invalid_status(self, client: FlaskClient, english: Language) -> None:
        """Test validation error for invalid status value."""
        # Given
        request_data = {
            "term": "hello",
            "language_id": english.id,
            "status": "INVALID_STATUS"
        }

        # When
        response = client.post("/api/terms", json=request_data)

        # Then
        assert response.status_code == 422  # Validation error

    def test_create_term_invalid_learning_stage_bounds(self, client: FlaskClient, english: Language) -> None:
        """Test validation for learning_stage bounds."""
        invalid_stages = [0, 6, -1, 100]

        for invalid_stage in invalid_stages:
            request_data = {
                "term": "test",
                "language_id": english.id,
                "status": LearningStatus.LEARNING,
                "learning_stage": invalid_stage
            }

            # When
            response = client.post("/api/terms", json=request_data)

            # Then
            assert response.status_code == 422  # Validation error

    def test_create_term_valid_learning_stage_bounds(self, client: FlaskClient, english: Language) -> None:
        """Test that valid learning_stage values are accepted."""
        valid_stages = [1, 2, 3, 4, 5]

        for stage in valid_stages:
            request_data = {
                "term": f"test{stage}",
                "language_id": english.id,
                "status": LearningStatus.LEARNING,
                "learning_stage": stage
            }

            # When
            response = client.post("/api/terms", json=request_data)

            # Then
            assert response.status_code == 200

            # Verify learning_stage was stored correctly
            response_data = response.json
            term_id = response_data["term_id"]
            progress = db.session.execute(
                sa.select(TermProgress).where(TermProgress.term_id == term_id)
            ).scalar_one()
            assert progress.learning_stage == stage

    def test_create_term_different_learning_statuses(self, client: FlaskClient, english: Language) -> None:
        """Test creating terms with different learning status values."""
        statuses_to_test = [
            LearningStatus.LEARNING,
            LearningStatus.KNOWN,
            LearningStatus.IGNORE
        ]

        for i, status in enumerate(statuses_to_test):
            request_data = {
                "term": f"status_test_{i}",
                "language_id": english.id,
                "status": status
            }

            # When
            response = client.post("/api/terms", json=request_data)

            # Then
            assert response.status_code == 200

            # Verify status was stored correctly
            response_data = response.json
            term_id = response_data["term_id"]
            progress = db.session.execute(
                sa.select(TermProgress).where(TermProgress.term_id == term_id)
            ).scalar_one()
            assert progress.status == status

    def test_create_term_response_structure(self, client: FlaskClient, english: Language) -> None:
        """Test the structure of successful create term response."""
        # Given
        request_data = {
            "term": "response_test",
            "language_id": english.id,
            "status": LearningStatus.LEARNING
        }

        # When
        response = client.post("/api/terms", json=request_data)

        # Then
        assert response.status_code == 200
        response_data = response.json
        assert isinstance(response_data, dict)
        assert "term_id" in response_data
        assert isinstance(response_data["term_id"], int)
        assert response_data["term_id"] > 0


class TestUpdateTermEndpoint:
    """Test cases for PATCH /api/terms/<int:term_id> endpoint."""

    def test_update_term_success(self, client: FlaskClient, english: Language) -> None:
        """Test successful term update with all fields."""
        # Given - Create a term first
        term = Term(
            norm="hello",
            display="Hello",
            language_id=english.id,
            token_count=1
        )
        db.session.add(term)
        db.session.commit()
        term_id = term.id

        request_data = {
            "status": LearningStatus.LEARNING,
            "learning_stage": 3,
            "display": "hello",
            "translation": "greeting"
        }

        # When
        response = client.patch(f"/api/terms/{term_id}", json=request_data)

        # Then
        assert response.status_code == 204

        # Verify term was updated
        updated_term = db.session.execute(
            sa.select(Term).where(Term.id == term_id)
        ).scalar_one()
        assert updated_term.display == "hello"

        # Verify term progress was created/updated
        progress = db.session.execute(
            sa.select(TermProgress).where(TermProgress.term_id == term_id)
        ).scalar_one()
        assert progress.status == LearningStatus.LEARNING
        assert progress.learning_stage == 3
        assert progress.translation == "greeting"

    def test_update_term_minimal_data(self, client: FlaskClient, english: Language) -> None:
        """Test term update with only required fields."""
        # Given
        term = Term(
            norm="world",
            display="World",
            language_id=english.id,
            token_count=1
        )
        db.session.add(term)
        db.session.commit()
        term_id = term.id

        request_data = {
            "status": LearningStatus.KNOWN,
            "learning_stage": 1
        }

        # When
        response = client.patch(f"/api/terms/{term_id}", json=request_data)

        # Then
        assert response.status_code == 204

        # Verify term progress was created
        progress = db.session.execute(
            sa.select(TermProgress).where(TermProgress.term_id == term_id)
        ).scalar_one()
        assert progress.status == LearningStatus.KNOWN
        assert progress.learning_stage == 1
        assert progress.translation is None

    def test_update_term_display_only(self, client: FlaskClient, english: Language) -> None:
        """Test updating only the display field."""
        # Given
        term = Term(
            norm="test",
            display="TEST",
            language_id=english.id,
            token_count=1
        )
        db.session.add(term)
        db.session.commit()
        term_id = term.id

        request_data = {
            "status": LearningStatus.LEARNING,
            "display": "Test"
        }

        # When
        response = client.patch(f"/api/terms/{term_id}", json=request_data)

        # Then
        assert response.status_code == 204

        # Verify display was updated
        updated_term = db.session.execute(
            sa.select(Term).where(Term.id == term_id)
        ).scalar_one()
        assert updated_term.display == "Test"

    def test_update_term_translation_only(self, client: FlaskClient, english: Language) -> None:
        """Test updating only the translation field."""
        # Given
        term = Term(
            norm="cat",
            display="cat",
            language_id=english.id,
            token_count=1
        )
        db.session.add(term)
        db.session.commit()
        term_id = term.id

        request_data = {
            "status": LearningStatus.LEARNING,
            "translation": "feline animal"
        }

        # When
        response = client.patch(f"/api/terms/{term_id}", json=request_data)

        # Then
        assert response.status_code == 204

        # Verify translation was set
        progress = db.session.execute(
            sa.select(TermProgress).where(TermProgress.term_id == term_id)
        ).scalar_one()
        assert progress.translation == "feline animal"

    def test_update_term_progress_upsert(self, client: FlaskClient, english: Language) -> None:
        """Test that updating an existing term progress record works correctly."""
        # Given - Create term with existing progress
        term = Term(
            norm="dog",
            display="dog",
            language_id=english.id,
            token_count=1
        )
        db.session.add(term)
        db.session.flush()

        existing_progress = TermProgress(
            term_id=term.id,
            status=LearningStatus.LEARNING,
            learning_stage=1,
            translation="initial translation"
        )
        db.session.add(existing_progress)
        db.session.commit()
        term_id = term.id

        request_data = {
            "status": LearningStatus.KNOWN,
            "learning_stage": 5,
            "translation": "updated translation"
        }

        # When
        response = client.patch(f"/api/terms/{term_id}", json=request_data)

        # Then
        assert response.status_code == 204

        # Verify progress was updated, not duplicated
        progress_count = db.session.execute(
            sa.select(sa.func.count()).select_from(TermProgress).where(TermProgress.term_id == term_id)
        ).scalar()
        assert progress_count == 1

        progress = db.session.execute(
            sa.select(TermProgress).where(TermProgress.term_id == term_id)
        ).scalar_one()
        assert progress.status == LearningStatus.KNOWN
        assert progress.learning_stage == 5
        assert progress.translation == "updated translation"

    def test_update_term_invalid_display_normalization(self, client: FlaskClient, english: Language) -> None:
        """Test that display changes are rejected if they don't match the normalized form."""
        # Given
        term = Term(
            norm="hello",
            display="Hello",
            language_id=english.id,
            token_count=1
        )
        db.session.add(term)
        db.session.commit()
        term_id = term.id

        request_data = {
            "status": LearningStatus.LEARNING,
            "display": "goodbye"  # This normalizes to "goodbye", not "hello"
        }

        # When
        response = client.patch(f"/api/terms/{term_id}", json=request_data)

        # Then
        assert response.status_code == 400
        assert response.json == {
            "error": "Bad Request",
            "msg": "display must match the term's normalized form"
        }

        # Verify term display was not changed
        unchanged_term = db.session.execute(
            sa.select(Term).where(Term.id == term_id)
        ).scalar_one()
        assert unchanged_term.display == "Hello"

    def test_update_term_display_case_changes_allowed(self, client: FlaskClient, english: Language) -> None:
        """Test that display case changes are allowed if they normalize to the same form."""
        # Given
        term = Term(
            norm="hello",
            display="hello",
            language_id=english.id,
            token_count=1
        )
        db.session.add(term)
        db.session.commit()
        term_id = term.id

        request_data = {
            "status": LearningStatus.LEARNING,
            "display": "HELLO"  # Same normalized form, different case
        }

        # When
        response = client.patch(f"/api/terms/{term_id}", json=request_data)

        # Then
        assert response.status_code == 204

        # Verify display was updated
        updated_term = db.session.execute(
            sa.select(Term).where(Term.id == term_id)
        ).scalar_one()
        assert updated_term.display == "HELLO"

    def test_update_term_nonexistent_id(self, client: FlaskClient) -> None:
        """Test error handling for non-existent term_id."""
        # Given
        request_data = {
            "status": LearningStatus.LEARNING,
            "learning_stage": 1
        }

        # When
        response = client.patch("/api/terms/99999", json=request_data)

        # Then
        assert response.status_code == 404
        assert response.json == {"error": "Not Found", "msg": "invalid term_id: '99999'"}

    def test_update_term_missing_status(self, client: FlaskClient, english: Language) -> None:
        """Test validation error for missing status field."""
        # Given
        term = Term(
            norm="test",
            display="test",
            language_id=english.id,
            token_count=1
        )
        db.session.add(term)
        db.session.commit()
        term_id = term.id

        request_data = {
            "learning_stage": 1
        }

        # When
        response = client.patch(f"/api/terms/{term_id}", json=request_data)

        # Then
        assert response.status_code == 422  # Validation error

    def test_update_term_invalid_status(self, client: FlaskClient, english: Language) -> None:
        """Test validation error for invalid status value."""
        # Given
        term = Term(
            norm="test",
            display="test",
            language_id=english.id,
            token_count=1
        )
        db.session.add(term)
        db.session.commit()
        term_id = term.id

        request_data = {
            "status": "INVALID_STATUS",
            "learning_stage": 1
        }

        # When
        response = client.patch(f"/api/terms/{term_id}", json=request_data)

        # Then
        assert response.status_code == 422  # Validation error

    def test_update_term_invalid_learning_stage_constraint(self, client: FlaskClient, english: Language) -> None:
        """Test that invalid learning stage values are rejected by database constraints."""
        # Given
        term = Term(
            norm="test",
            display="test",
            language_id=english.id,
            token_count=1
        )
        db.session.add(term)
        db.session.commit()
        term_id = term.id

        request_data = {
            "status": LearningStatus.LEARNING,
            "learning_stage": -1  # Invalid for LEARNING status (must be 1-5)
        }

        # When
        response = client.patch(f"/api/terms/{term_id}", json=request_data)

        # Then should fail due to validation
        assert response.status_code == 422

    def test_update_term_response_has_no_content(self, client: FlaskClient, english: Language) -> None:
        """Test that successful update returns empty response body."""
        # Given
        term = Term(
            norm="test",
            display="test",
            language_id=english.id,
            token_count=1
        )
        db.session.add(term)
        db.session.commit()
        term_id = term.id

        request_data = {
            "status": LearningStatus.LEARNING
        }

        # When
        response = client.patch(f"/api/terms/{term_id}", json=request_data)

        # Then
        assert response.status_code == 204

    def test_update_term_different_learning_statuses(self, client: FlaskClient, english: Language) -> None:
        """Test updating terms with different learning status values."""
        # Given
        term = Term(
            norm="status_test",
            display="status_test",
            language_id=english.id,
            token_count=1
        )
        db.session.add(term)
        db.session.commit()
        term_id = term.id

        statuses_to_test = [
            LearningStatus.LEARNING,
            LearningStatus.KNOWN,
            LearningStatus.IGNORE
        ]

        for status in statuses_to_test:
            request_data = {
                "status": status,
                "learning_stage": 2
            }

            # When
            response = client.patch(f"/api/terms/{term_id}", json=request_data)

            # Then
            assert response.status_code == 204

            # Verify status was updated
            progress = db.session.execute(
                sa.select(TermProgress).where(TermProgress.term_id == term_id)
            ).scalar_one()
            assert progress.status == status
