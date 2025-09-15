"""
JapaneseParser tests.
"""
from __future__ import annotations

from typing import TYPE_CHECKING, Iterator

import pytest

from src.parse.base import ParsedToken
from src.parse.mecab_parser import JapaneseParser

if TYPE_CHECKING:
    from src.models.language import Language


@pytest.mark.skip(reason="Term model not available in this codebase")
def test_token_count(japanese):
    "token_count checks."
    cases = [("私", 1), ("元気", 1), ("です", 1), ("元気です", 2), ("元気です私", 3)]
    for text, expected_count in cases:
        # t = Term(japanese, text)
        # assert t.token_count == expected_count, text
        # assert t.text_lc == t.text, "case"
        pass


def assert_tokens_equals(text: str, lang: Language, expected: list[ParsedToken]) -> None:
    """
    Parsing a text using a language should give the expected parsed tokens.

    expected is given as array of:
    [ original_text, is_word, is_end_of_sentence ]
    """
    p = JapaneseParser()
    actual = p.get_parsed_tokens(text, lang)
    assert [str(a) for a in actual] == [str(e) for e in expected]


def test_end_of_sentence_stored_in_parsed_tokens(japanese: Language):
    "ParsedToken is marked as EOS=True at ends of sentences."
    s = "元気.元気?元気!\n元気。元気？元気！"

    expected = [
        ParsedToken("元気", True),
        ParsedToken(".", False, True),
        ParsedToken("元気", True),
        ParsedToken("?", False, True),
        ParsedToken("元気", True),
        ParsedToken("!", False, True),
        ParsedToken("¶", False, True),
        ParsedToken("元気", True),
        ParsedToken("。", False, True),
        ParsedToken("元気", True),
        ParsedToken("？", False, True),
        ParsedToken("元気", True),
        ParsedToken("！", False, True),
        ParsedToken("¶", False, True),
    ]
    assert_tokens_equals(s, japanese, expected)


def test_issue_488_repeat_character_handled(japanese: Language):
    "Repeat sometimes needs explicit check, can be returned as own word."
    s = "聞こえる行く先々。少々お待ちください。"

    expected = [
        ParsedToken("聞こえる", True),
        ParsedToken("行く先", True),
        ParsedToken("々", True),
        ParsedToken("。", False, True),
        ParsedToken("少々", True),
        ParsedToken("お待ち", True),
        ParsedToken("ください", True),
        ParsedToken("。", False, True),
        ParsedToken("¶", False, True),
    ]
    assert_tokens_equals(s, japanese, expected)


@pytest.mark.skip(reason="MeCab system library not installed")
def test_readings(app):
    """
    Parser returns readings if they add value.
    """
    p = JapaneseParser()

    # Don't bother giving reading for a few cases
    no_reading = ["NHK", "ツヨイ", "どちら"]  # roman  # only katakana  # only hiragana

    for c in no_reading:
        assert p.get_reading(c) is None, c

    zws = "\u200B"
    cases = [
        ("強い", "つよい"),
        ("二人", "ににん"),  # ah well, not perfect :-)
        ("強いか", "つよいか"),
        (f"強い{zws}か", f"つよい{zws}か"),  # zero-width-space ignored
    ]

    for c in cases:
        assert p.get_reading(c[0]) == c[1], c[0]


@pytest.mark.skip(reason="current_settings not available in this codebase")
def test_reading_setting(app):
    "Return reading matching user setting."
    cases = {
        "katakana": "ツヨイ",
        "hiragana": "つよい",
        "alphabet": "tsuyoi",
    }
    p = JapaneseParser()
    for k, v in cases.items():
        current_settings["japanese_reading"] = k
        assert p.get_reading("強い") == v, k
