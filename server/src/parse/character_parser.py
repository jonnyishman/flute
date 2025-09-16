"""Parsing for single-character languages.

The parser uses some Language settings (e.g., word characters) to
perform the actual parsing.

Includes classes:
- ClassicalChineseParser
"""
from __future__ import annotations

import re
from typing import TYPE_CHECKING

from src.parse.base import AbstractParser, ParsedToken

if TYPE_CHECKING:
    from src.models.language import Language


class ClassicalChineseParser(AbstractParser):
    """A parser for Classical Chinese single-character text."""

    @classmethod
    def name(cls) -> str:
        return "Classical Chinese"

    def get_parsed_tokens(self, text: str, language: Language) -> list[ParsedToken]:
        """Returns ParsedToken array for given language."""
        text = re.sub(r"[ \t]+", "", text)

        for replacement in language.character_substitutions.split("|"):
            if (fromto := replacement.strip().split("=")) and len(fromto) >= 2:
                rfrom, rto = fromto[0].strip(), fromto[1].strip()
                text = text.replace(rfrom, rto)

        text = (text.replace("\r\n", "\n")
                   .replace("{", "[")
                   .replace("}", "]")
                   .replace("\n", "¶")
                   .strip())

        pattern = f"[{language.word_characters}]"
        tokens: list[ParsedToken] = []
        for char in text:
            is_word_char = bool(re.match(pattern, char))
            is_end_of_sentence = (char in language.regexp_split_sentences or
                                char == "¶")
            tokens.append(ParsedToken(char, char, is_word_char, is_end_of_sentence))

        return tokens
