"""Pytest configuration and fixtures."""
from __future__ import annotations

from typing import TYPE_CHECKING

import pytest

from src.app import create_app
from src.config import AppConfig
from src.models import Language, db

if TYPE_CHECKING:
    from collections.abc import Iterator

    from flask import Flask
    from flask.testing import FlaskClient, FlaskCliRunner


@pytest.fixture(scope="session")
def config() -> AppConfig:
    import tempfile
    from pathlib import Path

    return AppConfig(
        SQLITE_PATH=":memory:",
        SECRET_KEY="test_secret",
        IMAGE_STORAGE_PATH=str(Path(tempfile.mkdtemp()) / "images"),
    )


@pytest.fixture
def app(config: AppConfig) -> Iterator[Flask]:
    """Create application for testing."""
    app_ = create_app(config)
    app_.config["TESTING"] = True
    with app_.app_context():
        db.create_all()
        yield app_
        db.drop_all()


@pytest.fixture
def client(app: Flask) -> FlaskClient:
    """Create test client."""
    return app.test_client()


@pytest.fixture
def runner(app: Flask) -> FlaskCliRunner:
    """Create test CLI runner."""
    return app.test_cli_runner()


@pytest.fixture(name="spanish")
def fixture_spanish(app: Flask):
    """Spanish language fixture."""
    lang = Language()
    lang.name = "Spanish"
    lang.character_substitutions = "´='|`='|'='|'='|...=…|..=‥"
    lang.regexp_split_sentences = ".!?"
    lang.exceptions_split_sentences = "Sr.|Sra.|Dr.|[A-Z].|Vd.|Vds."
    lang.word_characters = "a-zA-ZÀ-ÖØ-öø-ȳáéíóúÁÉÍÓÚñÑ"
    lang.right_to_left = False
    lang.show_romanization = False
    lang.parser_type = "spacedel"
    db.session.add(lang)
    db.session.commit()
    return lang


@pytest.fixture(name="english")
def fixture_english(app: Flask):
    """English language fixture."""
    lang = Language()
    lang.name = "English"
    lang.character_substitutions = "´='|`='|'='|'='|...=…|..=‥"
    lang.regexp_split_sentences = ".!?"
    lang.exceptions_split_sentences = "Mr.|Mrs.|Dr.|[A-Z].|Jr.|Sr.|vs.|etc.|Inc.|Ltd.|Co."
    lang.word_characters = "a-zA-Z"
    lang.right_to_left = False
    lang.show_romanization = False
    lang.parser_type = "spacedel"
    db.session.add(lang)
    db.session.commit()
    return lang


@pytest.fixture(name="german")
def fixture_german(app: Flask):
    """German language fixture."""
    lang = Language()
    lang.name = "German"
    lang.character_substitutions = "´='|`='|'='|'='|...=…|..=‥"
    lang.regexp_split_sentences = ".!?"
    lang.exceptions_split_sentences = "Dr.|Prof.|Mr.|Mrs.|[A-Z].|etc.|bzw.|z.B.|u.a."
    lang.word_characters = "a-zA-ZÄÖÜäöüß\u200c"  # Include zero-width non-joiner
    lang.right_to_left = False
    lang.show_romanization = False
    lang.parser_type = "spacedel"
    db.session.add(lang)
    db.session.commit()
    return lang


@pytest.fixture(name="hindi")
def fixture_hindi(app: Flask):
    """Hindi language fixture."""
    lang = Language()
    lang.name = "Hindi"
    lang.character_substitutions = "´='|`='|'='|'='|...=…|..=‥"
    lang.regexp_split_sentences = ".!?।"
    lang.exceptions_split_sentences = ""
    lang.word_characters = "a-zA-Z\u0900-\u097F\u200d"  # Include zero-width joiner
    lang.right_to_left = False
    lang.show_romanization = False
    lang.parser_type = "spacedel"
    db.session.add(lang)
    db.session.commit()
    return lang


@pytest.fixture(name="japanese")
def fixture_japanese(app: Flask):
    """Japanese language fixture."""
    lang = Language()
    lang.name = "Japanese"
    lang.character_substitutions = "´='|`='|'='|'='|...=…|..=‥"
    lang.regexp_split_sentences = ".!?。？！"
    lang.exceptions_split_sentences = ""
    lang.word_characters = "a-zA-Z\u3040-\u309F\u30A0-\u30FF\u4E00-\u9FAF"  # Hiragana, Katakana, Kanji
    lang.right_to_left = False
    lang.show_romanization = False
    lang.parser_type = "japanese"
    db.session.add(lang)
    db.session.commit()
    return lang


@pytest.fixture(name="turkish")
def fixture_turkish(app: Flask):
    """Turkish language fixture."""
    lang = Language()
    lang.name = "Turkish"
    lang.character_substitutions = "´='|`='|'='|'='|...=…|..=‥"
    lang.regexp_split_sentences = ".!?"
    lang.exceptions_split_sentences = "Dr.|Prof.|[A-Z].|etc."
    lang.word_characters = "a-zA-ZÇÖÜİĞŞçöüığş"
    lang.right_to_left = False
    lang.show_romanization = False
    lang.parser_type = "turkish"
    db.session.add(lang)
    db.session.commit()
    return lang


@pytest.fixture(name="classical_chinese")
def fixture_classical_chinese(app: Flask):
    """Classical Chinese language fixture."""
    lang = Language()
    lang.name = "Classical Chinese"
    lang.character_substitutions = "´='|`='|'='|'='|...=…|..=‥"
    lang.regexp_split_sentences = ".!?。？！"
    lang.exceptions_split_sentences = ""
    lang.word_characters = "\u4E00-\u9FAF\u3400-\u4DBF"  # CJK Unified Ideographs
    lang.right_to_left = False
    lang.show_romanization = False
    lang.parser_type = "classicalchinese"
    db.session.add(lang)
    db.session.commit()
    return lang


@pytest.fixture(name="generic")
def fixture_generic(app: Flask):
    """Generic language fixture for testing default word patterns."""
    lang = Language()
    lang.name = "Generic"
    lang.character_substitutions = "´='|`='|'='|'='|...=…|..=‥"
    lang.regexp_split_sentences = ".!?"
    lang.exceptions_split_sentences = "Mr.|Mrs.|Dr.|[A-Z]."
    lang.word_characters = ""  # Empty to use default pattern
    lang.right_to_left = False
    lang.show_romanization = False
    lang.parser_type = "spacedel"
    db.session.add(lang)
    db.session.commit()
    return lang
