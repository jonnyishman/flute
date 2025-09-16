"""Parsing using MeCab.

Uses natto-py (https://github.com/buruzaemon/natto-py) package and
MeCab to do parsing.

Includes classes:
- JapaneseParser
"""
from __future__ import annotations

import os
import re
import sys
from io import StringIO
from typing import TYPE_CHECKING

import jaconv
from natto import MeCab

from src.parse.base import AbstractParser, ParsedToken

if TYPE_CHECKING:
    from src.models.language import Language


class JapaneseParser(AbstractParser):
    """Japanese parser.

    This is only supported if mecab is installed.

    The parser uses natto-py library, and so should be able to find mecab
    automatically; if it can't, you may need to set the MECAB_PATH env variable.
    """

    _is_supported: bool | None = None
    _old_mecab_path: str | None = None

    @classmethod
    def is_supported(cls) -> bool:
        """True if a natto MeCab can be instantiated, otherwise false."""
        mecab_path = os.environ.get("MECAB_PATH", "").strip()
        path_unchanged = mecab_path == cls._old_mecab_path
        if path_unchanged and cls._is_supported is not None:
            return cls._is_supported

        env_key = "MECAB_PATH"
        if mecab_path:
            os.environ[env_key] = mecab_path
        else:
            os.environ.pop(env_key, None)

        mecab_works = False
        temp_err = StringIO()
        try:
            sys.stderr = temp_err
            MeCab()
            mecab_works = True
        except Exception:
            mecab_works = False
        finally:
            sys.stderr = sys.__stderr__

        cls._old_mecab_path = mecab_path
        cls._is_supported = mecab_works
        return mecab_works

    @classmethod
    def name(cls) -> str:
        return "Japanese"

    def get_parsed_tokens(self, text: str, language: Language) -> list[ParsedToken]:
        """Parse the string using MeCab."""
        text = re.sub(r"[ \t]+", " ", text).strip()

        # If the string contains a "\n", MeCab appears to silently
        # remove it.  Splitting it works (ref test_JapaneseParser).
        # Flags: ref https://github.com/buruzaemon/natto-py:
        #    -F = node format
        #    -U = unknown format
        #    -E = EOP format
        lines: list[str] = []
        with MeCab(r"-F %m\t%t\t%h\n -U %m\t%t\t%h\n -E EOP\t3\t7\n") as nm:
            for para in text.split("\n"):
                for node in nm.parse(para, as_nodes=True):
                    lines.append(node.feature)

        parsed_lines = [
            line.strip().split("\t")
            for line in lines
            if line and line.strip()
        ]

        # Filter out problematic "0\t4" tokens that can appear before EOP
        valid_lines = [line for line in parsed_lines if len(line) == 3]

        def line_to_token(lin: list[str]) -> ParsedToken:
            """Convert parsed line to a ParsedToken."""
            term, node_type, third = lin
            is_eos = term in language.regexp_split_sentences
            if term == "EOP" and third == "7":
                term = "¶"

            # Node type values ref
            # https://github.com/buruzaemon/natto-py/wiki/
            #    Node-Parsing-char_type
            #
            # The repeat character is sometimes returned as a "symbol"
            # (node type = 3), so handle that specifically.
            is_word = node_type in "2678" or term == "々"
            return ParsedToken(term, term, is_word, is_eos or term == "¶")

        return [line_to_token(line) for line in valid_lines]

    def _char_is_hiragana(self, char: str) -> bool:
        """Check if character is hiragana (U+3040 - U+309F)."""
        return "\u3040" <= char <= "\u309F"

    def _string_is_hiragana(self, text: str) -> bool:
        """Check if all characters in string are hiragana."""
        return all(self._char_is_hiragana(char) for char in text)

    def get_reading(self, text: str) -> str | None:
        """Get the pronunciation for the given text.

        Returns None if the text is all hiragana, or the pronunciation
        doesn't add value (same as text).
        """
        if self._string_is_hiragana(text):
            return None

        jp_reading_setting = os.environ.get("JAPANESE_READING", "").strip()
        if not jp_reading_setting:
            return None

        readings: list[str] = []
        with MeCab("-O yomi") as mecab:
            for node in mecab.parse(text, as_nodes=True):
                readings.append(node.feature)

        reading_result = "".join(
            reading.strip()
            for reading in readings
            if reading and reading.strip()
        ).strip()

        if not reading_result or reading_result == text:
            return None

        match jp_reading_setting:
            case "katakana":
                return reading_result
            case "hiragana":
                return jaconv.kata2hira(reading_result)
            case "alphabet":
                return jaconv.kata2alphabet(reading_result)
            case _:
                raise RuntimeError(f"Bad reading type {jp_reading_setting}")
