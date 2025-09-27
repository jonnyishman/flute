"""Tests for language API endpoints."""
from __future__ import annotations

from typing import TYPE_CHECKING

import sqlalchemy as sa

from src.models import Language, db

if TYPE_CHECKING:
    from flask.testing import FlaskClient


class TestGetLanguageSummariesEndpoint:
    """Test cases for GET /api/languages endpoint."""

    def test_get_language_summaries_empty(self, client: FlaskClient) -> None:
        """Test retrieving language summaries when no languages exist."""
        # When
        response = client.get("/api/languages")

        # Then
        assert response.status_code == 200
        response_data = response.json
        assert response_data == {"languages": []}

    def test_get_language_summaries_single(self, client: FlaskClient, english: Language) -> None:
        """Test retrieving language summaries with one language."""
        # When
        response = client.get("/api/languages")

        # Then
        assert response.status_code == 200
        response_data = response.json
        assert "languages" in response_data
        assert len(response_data["languages"]) == 1

        language = response_data["languages"][0]
        assert language["id"] == english.id
        assert language["name"] == english.name
        # Should only have id, name, and flag_image_filepath, not full details
        assert set(language.keys()) == {"id", "name", "flag_image_filepath"}

    def test_get_language_summaries_multiple_sorted(self, client: FlaskClient) -> None:
        """Test retrieving multiple language summaries sorted by name."""
        # Given
        lang_z = Language(name="Zulu")
        lang_a = Language(name="Arabic")
        lang_m = Language(name="Mandarin")

        db.session.add_all([lang_z, lang_a, lang_m])
        db.session.commit()

        # When
        response = client.get("/api/languages")

        # Then
        assert response.status_code == 200
        response_data = response.json
        assert len(response_data["languages"]) == 3

        # Should be sorted by name
        names = [lang["name"] for lang in response_data["languages"]]
        assert names == ["Arabic", "Mandarin", "Zulu"]

    def test_get_language_summaries_response_structure(self, client: FlaskClient, english: Language) -> None:
        """Test the response structure for language summaries."""
        # When
        response = client.get("/api/languages")

        # Then
        assert response.status_code == 200
        response_data = response.json
        assert isinstance(response_data, dict)
        assert "languages" in response_data
        assert isinstance(response_data["languages"], list)

        if response_data["languages"]:
            language = response_data["languages"][0]
            assert isinstance(language, dict)
            assert "id" in language
            assert "name" in language
            assert isinstance(language["id"], int)
            assert isinstance(language["name"], str)

    def test_get_language_summaries_with_books_filter(self, client: FlaskClient, english: Language) -> None:
        """Test filtering languages to only those with books."""
        from src.models import Book

        # Create a language without books and one with books
        lang_no_books = Language(name="No Books Language")
        db.session.add(lang_no_books)
        db.session.flush()

        # Create a book for the English language
        book = Book(title="Test Book", language_id=english.id)
        db.session.add(book)
        db.session.commit()

        # Test without filter - should return all languages
        response = client.get("/api/languages")
        assert response.status_code == 200
        all_languages = response.json["languages"]
        assert len(all_languages) == 2

        # Test with filter - should return only languages with books
        response = client.get("/api/languages?with_books=true")
        assert response.status_code == 200
        filtered_languages = response.json["languages"]
        assert len(filtered_languages) == 1
        assert filtered_languages[0]["name"] == english.name

        # Test with filter=false - should return all languages
        response = client.get("/api/languages?with_books=false")
        assert response.status_code == 200
        all_languages_false = response.json["languages"]
        assert len(all_languages_false) == 2


class TestGetLanguageDetailEndpoint:
    """Test cases for GET /api/languages/<int:language_id> endpoint."""

    def test_get_language_detail_success(self, client: FlaskClient, english: Language) -> None:
        """Test successful retrieval of language details."""
        # When
        response = client.get(f"/api/languages/{english.id}")

        # Then
        assert response.status_code == 200
        response_data = response.json

        # Should have all language fields
        assert response_data["id"] == english.id
        assert response_data["name"] == english.name
        assert response_data["flag_image_filepath"] == english.flag_image_filepath
        assert response_data["character_substitutions"] == english.character_substitutions
        assert response_data["regexp_split_sentences"] == english.regexp_split_sentences
        assert response_data["exceptions_split_sentences"] == english.exceptions_split_sentences
        assert response_data["word_characters"] == english.word_characters
        assert response_data["right_to_left"] == english.right_to_left
        assert response_data["show_romanization"] == english.show_romanization
        assert response_data["parser_type"] == english.parser_type

    def test_get_language_detail_nonexistent_id(self, client: FlaskClient) -> None:
        """Test error handling for non-existent language_id."""
        # When
        response = client.get("/api/languages/99999")

        # Then
        assert response.status_code == 404
        assert response.json == {"error": "Not Found", "msg": "Language with id '99999' not found"}

    def test_get_language_detail_response_structure(self, client: FlaskClient, english: Language) -> None:
        """Test the response structure for language detail."""
        # When
        response = client.get(f"/api/languages/{english.id}")

        # Then
        assert response.status_code == 200
        response_data = response.json

        expected_fields = {
            "id", "name", "flag_image_filepath", "character_substitutions", "regexp_split_sentences",
            "exceptions_split_sentences", "word_characters", "right_to_left",
            "show_romanization", "parser_type"
        }
        assert set(response_data.keys()) == expected_fields


class TestUpdateLanguageEndpoint:
    """Test cases for PATCH /api/languages/<int:language_id> endpoint."""

    def test_update_language_success_single_field(self, client: FlaskClient, english: Language) -> None:
        """Test successful language update with single field."""
        # Given
        request_data = {"name": "Updated English"}

        # When
        response = client.patch(f"/api/languages/{english.id}", json=request_data)

        # Then
        assert response.status_code == 204

        # Verify language was updated
        updated_language = db.session.execute(
            sa.select(Language).where(Language.id == english.id)
        ).scalar_one()
        assert updated_language.name == "Updated English"
        # Other fields should remain unchanged
        assert updated_language.parser_type == english.parser_type

    def test_update_language_success_multiple_fields(self, client: FlaskClient, english: Language) -> None:
        """Test successful language update with multiple fields."""
        # Given
        request_data = {
            "name": "Modified English",
            "parser_type": "mecab",
            "right_to_left": True,
            "show_romanization": True,
            "word_characters": "a-zA-Z"
        }

        # When
        response = client.patch(f"/api/languages/{english.id}", json=request_data)

        # Then
        assert response.status_code == 204

        # Verify all fields were updated
        updated_language = db.session.execute(
            sa.select(Language).where(Language.id == english.id)
        ).scalar_one()
        assert updated_language.name == "Modified English"
        assert updated_language.parser_type == "mecab"
        assert updated_language.right_to_left is True
        assert updated_language.show_romanization is True
        assert updated_language.word_characters == "a-zA-Z"
        # Unchanged fields should remain the same
        assert updated_language.character_substitutions == english.character_substitutions

    def test_update_language_success_all_fields(self, client: FlaskClient, english: Language) -> None:
        """Test successful language update with all fields."""
        # Given
        request_data = {
            "name": "Complete Update",
            "character_substitutions": "new_substitutions",
            "regexp_split_sentences": "new_regexp",
            "exceptions_split_sentences": "new_exceptions",
            "word_characters": "new_word_chars",
            "right_to_left": True,
            "show_romanization": True,
            "parser_type": "custom"
        }

        # When
        response = client.patch(f"/api/languages/{english.id}", json=request_data)

        # Then
        assert response.status_code == 204

        # Verify all fields were updated
        updated_language = db.session.execute(
            sa.select(Language).where(Language.id == english.id)
        ).scalar_one()
        assert updated_language.name == "Complete Update"
        assert updated_language.character_substitutions == "new_substitutions"
        assert updated_language.regexp_split_sentences == "new_regexp"
        assert updated_language.exceptions_split_sentences == "new_exceptions"
        assert updated_language.word_characters == "new_word_chars"
        assert updated_language.right_to_left is True
        assert updated_language.show_romanization is True
        assert updated_language.parser_type == "custom"

    def test_update_language_partial_update(self, client: FlaskClient, english: Language) -> None:
        """Test that partial updates don't affect unspecified fields."""
        # Given - Store original values
        original_parser_type = english.parser_type
        original_right_to_left = english.right_to_left

        request_data = {"name": "Partially Updated"}

        # When
        response = client.patch(f"/api/languages/{english.id}", json=request_data)

        # Then
        assert response.status_code == 204

        # Verify only name was updated
        updated_language = db.session.execute(
            sa.select(Language).where(Language.id == english.id)
        ).scalar_one()
        assert updated_language.name == "Partially Updated"
        assert updated_language.parser_type == original_parser_type
        assert updated_language.right_to_left == original_right_to_left

    def test_update_language_nonexistent_id(self, client: FlaskClient) -> None:
        """Test error handling for non-existent language_id."""
        # Given
        request_data = {"name": "Non-existent"}

        # When
        response = client.patch("/api/languages/99999", json=request_data)

        # Then
        assert response.status_code == 404
        assert response.json == {"error": "Not Found", "msg": "Language with id '99999' not found"}

    def test_update_language_empty_request(self, client: FlaskClient, english: Language) -> None:
        """Test update with empty request body."""
        # Given
        original_name = english.name
        request_data = {}

        # When
        response = client.patch(f"/api/languages/{english.id}", json=request_data)

        # Then
        assert response.status_code == 204

        # Verify nothing was changed
        updated_language = db.session.execute(
            sa.select(Language).where(Language.id == english.id)
        ).scalar_one()
        assert updated_language.name == original_name

    def test_update_language_response_has_no_content(self, client: FlaskClient, english: Language) -> None:
        """Test that successful update returns empty response body."""
        # Given
        request_data = {"name": "Test Response"}

        # When
        response = client.patch(f"/api/languages/{english.id}", json=request_data)

        # Then
        assert response.status_code == 204


class TestCreateLanguageEndpoint:
    """Test cases for POST /api/languages endpoint."""

    def test_create_language_success_minimal(self, client: FlaskClient) -> None:
        """Test successful language creation with minimal required fields."""
        # Given
        request_data = {"name": "Test Language"}

        # When
        response = client.post("/api/languages", json=request_data)

        # Then
        assert response.status_code == 201
        response_data = response.json
        assert "language_id" in response_data
        language_id = response_data["language_id"]

        # Verify language was created with defaults
        language = db.session.execute(
            sa.select(Language).where(Language.id == language_id)
        ).scalar_one()
        assert language.name == "Test Language"
        # Should have default values
        assert language.character_substitutions == "´='|`='|'='|'='|...=…|..=‥"
        assert language.regexp_split_sentences == ".!?"
        assert language.exceptions_split_sentences == "Mr.|Mrs.|Dr.|[A-Z].|Vd.|Vds."
        assert language.word_characters == "a-zA-ZÀ-ÖØ-öø-ȳáéíóúÁÉÍÓÚñÑ"
        assert language.right_to_left is False
        assert language.show_romanization is False
        assert language.parser_type == "spacedel"

    def test_create_language_success_all_fields(self, client: FlaskClient) -> None:
        """Test successful language creation with all fields provided."""
        # Given
        request_data = {
            "name": "Custom Language",
            "character_substitutions": "custom_subs",
            "regexp_split_sentences": "custom_regexp",
            "exceptions_split_sentences": "custom_exceptions",
            "word_characters": "custom_chars",
            "right_to_left": True,
            "show_romanization": True,
            "parser_type": "custom_parser"
        }

        # When
        response = client.post("/api/languages", json=request_data)

        # Then
        assert response.status_code == 201
        response_data = response.json
        language_id = response_data["language_id"]

        # Verify language was created with correct values
        language = db.session.execute(
            sa.select(Language).where(Language.id == language_id)
        ).scalar_one()
        assert language.name == "Custom Language"
        assert language.character_substitutions == "custom_subs"
        assert language.regexp_split_sentences == "custom_regexp"
        assert language.exceptions_split_sentences == "custom_exceptions"
        assert language.word_characters == "custom_chars"
        assert language.right_to_left is True
        assert language.show_romanization is True
        assert language.parser_type == "custom_parser"

    def test_create_language_partial_fields(self, client: FlaskClient) -> None:
        """Test language creation with some custom fields and some defaults."""
        # Given
        request_data = {
            "name": "Partial Language",
            "parser_type": "custom",
            "right_to_left": True
        }

        # When
        response = client.post("/api/languages", json=request_data)

        # Then
        assert response.status_code == 201
        response_data = response.json
        language_id = response_data["language_id"]

        # Verify custom and default values
        language = db.session.execute(
            sa.select(Language).where(Language.id == language_id)
        ).scalar_one()
        assert language.name == "Partial Language"
        assert language.parser_type == "custom"
        assert language.right_to_left is True
        # These should have defaults
        assert language.character_substitutions == "´='|`='|'='|'='|...=…|..=‥"
        assert language.show_romanization is False

    def test_create_language_missing_name(self, client: FlaskClient) -> None:
        """Test validation error for missing name field."""
        # Given
        request_data = {"parser_type": "test"}

        # When
        response = client.post("/api/languages", json=request_data)

        # Then
        assert response.status_code == 422  # Validation error

    def test_create_language_empty_request(self, client: FlaskClient) -> None:
        """Test validation error for empty request."""
        # When
        response = client.post("/api/languages", json={})

        # Then
        assert response.status_code == 422  # Validation error

    def test_create_language_response_structure(self, client: FlaskClient) -> None:
        """Test the structure of successful create language response."""
        # Given
        request_data = {"name": "Response Test"}

        # When
        response = client.post("/api/languages", json=request_data)

        # Then
        assert response.status_code == 201
        response_data = response.json
        assert isinstance(response_data, dict)
        assert "language_id" in response_data
        assert isinstance(response_data["language_id"], int)
        assert response_data["language_id"] > 0

    def test_create_language_boolean_fields(self, client: FlaskClient) -> None:
        """Test creating language with boolean field variations."""
        test_cases = [
            {"name": "Test True", "right_to_left": True, "show_romanization": True},
            {"name": "Test False", "right_to_left": False, "show_romanization": False},
        ]

        for request_data in test_cases:
            # When
            response = client.post("/api/languages", json=request_data)

            # Then
            assert response.status_code == 201
            response_data = response.json
            language_id = response_data["language_id"]

            # Verify boolean values were stored correctly
            language = db.session.execute(
                sa.select(Language).where(Language.id == language_id)
            ).scalar_one()
            assert language.right_to_left == request_data["right_to_left"]
            assert language.show_romanization == request_data["show_romanization"]

    def test_create_language_with_flag_image_filepath(self, client: FlaskClient) -> None:
        """Test creating language with flag image filepath."""
        # Given
        request_data = {
            "name": "Test Flag Language",
            "flag_image_filepath": "/images/flags/test.png"
        }

        # When
        response = client.post("/api/languages", json=request_data)

        # Then
        assert response.status_code == 201
        response_data = response.json
        language_id = response_data["language_id"]

        # Verify flag image filepath was stored correctly
        language = db.session.execute(
            sa.select(Language).where(Language.id == language_id)
        ).scalar_one()
        assert language.flag_image_filepath == "/images/flags/test.png"

    def test_update_language_flag_image_filepath(self, client: FlaskClient, english: Language) -> None:
        """Test updating language flag image filepath."""
        # Given
        request_data = {"flag_image_filepath": "/images/flags/uk.png"}

        # When
        response = client.patch(f"/api/languages/{english.id}", json=request_data)

        # Then
        assert response.status_code == 204

        # Verify flag image filepath was updated
        updated_language = db.session.execute(
            sa.select(Language).where(Language.id == english.id)
        ).scalar_one()
        assert updated_language.flag_image_filepath == "/images/flags/uk.png"
