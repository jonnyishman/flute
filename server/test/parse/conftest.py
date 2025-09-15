"""
Pytest fixtures for parse tests.
"""

import pytest

from src.models.language import Language


@pytest.fixture(name="spanish")
def fixture_spanish():
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
    return lang


@pytest.fixture(name="english")
def fixture_english():
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
    return lang


@pytest.fixture(name="german")
def fixture_german():
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
    return lang


@pytest.fixture(name="hindi")
def fixture_hindi():
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
    return lang


@pytest.fixture(name="japanese")
def fixture_japanese():
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
    return lang


@pytest.fixture(name="turkish")
def fixture_turkish():
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
    return lang


@pytest.fixture(name="classical_chinese")
def fixture_classical_chinese():
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
    return lang


@pytest.fixture(name="generic")
def fixture_generic():
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
    return lang
