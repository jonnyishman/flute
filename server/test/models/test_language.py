"""Tests for language models."""
from __future__ import annotations

from typing import TYPE_CHECKING

import sqlalchemy as sa

from src.models import db
from src.models.language import Language, LanguageDictionary

if TYPE_CHECKING:
    from flask import Flask


class TestLanguageModel:
    """Test cases for Language model."""

    def test_create_language(self, app: Flask):
        """Test creating a language instance."""
        # Given
        language = Language(name="Spanish")

        # When
        db.session.add(language)
        db.session.commit()

        # Then
        assert language.id is not None
        assert language.name == "Spanish"
        assert language.character_substitutions == "´='|`='|'='|'='|...=…|..=‥"
        assert language.regexp_split_sentences == ".!?"
        assert language.exceptions_split_sentences == "Mr.|Mrs.|Dr.|[A-Z].|Vd.|Vds."
        assert language.word_characters == "a-zA-ZÀ-ÖØ-öø-ȳáéíóúÁÉÍÓÚñÑ"
        assert language.right_to_left is False
        assert language.show_romanization is False
        assert language.parser_type == "spacedel"

    def test_language_repr(self, app: Flask):
        """Test language string representation."""
        # Given
        language = Language(name="French")
        db.session.add(language)
        db.session.commit()

        # When
        repr_str = repr(language)

        # Then
        assert f"<Language {language.id} 'French'>" == repr_str

    def test_language_dictionary_relationship(self, app: Flask):
        """Test language-dictionary relationship."""
        # Given
        language = Language(name="German")
        dict1 = LanguageDictionary(
            language=language,
            use_for="translation",
            dict_type="web",
            dict_uri="https://example.com/dict1",
            sort_order=1
        )
        dict2 = LanguageDictionary(
            language=language,
            use_for="lookup",
            dict_type="local",
            dict_uri="/path/to/dict2",
            sort_order=2
        )

        # When
        db.session.add_all([language, dict1, dict2])
        db.session.commit()

        # Then
        assert len(language.dictionaries) == 2
        assert dict1 in language.dictionaries
        assert dict2 in language.dictionaries
        assert language.dictionaries[0].sort_order == 1
        assert language.dictionaries[1].sort_order == 2

    def test_language_cascade_delete(self, app: Flask):
        """Test that deleting a language cascades to dictionaries."""
        # Given
        language = Language(name="Italian")
        dictionary = LanguageDictionary(
            language=language,
            use_for="translation",
            dict_type="web",
            dict_uri="https://example.com/dict",
            sort_order=1
        )
        db.session.add_all([language, dictionary])
        db.session.commit()

        # When
        db.session.delete(language)
        db.session.commit()

        # Then
        dictionaries = list(db.session.execute(sa.select(LanguageDictionary)).all())
        assert not dictionaries


class TestLanguageDictionaryModel:
    """Test cases for LanguageDictionary model."""

    def test_create_language_dictionary(self, app: Flask):
        """Test creating a language dictionary instance."""
        # Given
        language = Language(name="Portuguese")
        db.session.add(language)
        db.session.commit()

        dictionary = LanguageDictionary(
            language_id=language.id,
            use_for="translation",
            dict_type="web",
            dict_uri="https://translate.google.com",
            is_active=True,
            sort_order=1
        )

        # When
        db.session.add(dictionary)
        db.session.commit()

        # Then
        assert dictionary.id is not None
        assert dictionary.language_id == language.id
        assert dictionary.use_for == "translation"
        assert dictionary.dict_type == "web"
        assert dictionary.dict_uri == "https://translate.google.com"
        assert dictionary.is_active is True
        assert dictionary.sort_order == 1

    def test_language_dictionary_default_active(self, app: Flask):
        """Test dictionary defaults to active."""
        # Given
        language = Language(name="Japanese")
        db.session.add(language)
        db.session.commit()

        dictionary = LanguageDictionary(
            language_id=language.id,
            use_for="lookup",
            dict_type="local",
            dict_uri="/path/to/dict",
            sort_order=1
        )

        # When
        db.session.add(dictionary)
        db.session.commit()

        # Then
        assert dictionary.is_active is True

    def test_language_dictionary_foreign_key_constraint(self, app: Flask):
        """Test dictionary requires valid language."""
        # Given
        language = Language(name="Korean")
        db.session.add(language)
        db.session.commit()

        # Valid dictionary should work
        valid_dict = LanguageDictionary(
            language_id=language.id,
            use_for="translation",
            dict_type="web",
            dict_uri="https://example.com",
            sort_order=1
        )

        # When
        db.session.add(valid_dict)
        db.session.commit()

        # Then
        assert valid_dict.language_id == language.id

    def test_language_dictionary_relationship(self, app: Flask):
        """Test dictionary-language relationship."""
        # Given
        language = Language(name="Russian")
        dictionary = LanguageDictionary(
            language=language,
            use_for="translation",
            dict_type="web",
            dict_uri="https://example.com",
            sort_order=1
        )

        # When
        db.session.add_all([language, dictionary])
        db.session.commit()

        # Then
        assert dictionary.language == language
        assert dictionary.language.name == "Russian"
