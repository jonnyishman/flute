"""
JapaneseParser tests.
"""
from __future__ import annotations

from typing import TYPE_CHECKING

from src.parse.base import ParsedToken
from src.parse.character_parser import ClassicalChineseParser

if TYPE_CHECKING:
    from src.models.language import Language


def assert_tokens_equals(text: str, lang: Language, expected: list[ParsedToken]):
    """
    Parsing a text using a language should give the expected parsed tokens.

    expected is given as array of:
    [ original_text, is_word, is_end_of_sentence ]
    """
    p = ClassicalChineseParser()
    print("passing text:")
    print(text)
    actual = p.get_parsed_tokens(text, lang)
    assert [str(a) for a in actual] == [str(e) for e in expected]


def test_sample_1(classical_chinese: Language):
    "Sample text parsed."
    s = "學而時習之，不亦說乎？"

    expected = [
        ParsedToken("學", "學", True),
        ParsedToken("而", "而", True),
        ParsedToken("時", "時", True),
        ParsedToken("習", "習", True),
        ParsedToken("之", "之", True),
        ParsedToken("，", "，", False),
        ParsedToken("不", "不", True),
        ParsedToken("亦", "亦", True),
        ParsedToken("說", "說", True),
        ParsedToken("乎", "乎", True),
        ParsedToken("？", "？", False, True),
    ]
    assert_tokens_equals(s, classical_chinese, expected)


def test_sample_2(classical_chinese: Language):
    "Sample text parsed, spaces removed."
    s = """學  而時習 之，不亦說乎？
有朋    自遠方來，不亦樂乎？"""

    expected = [
        ParsedToken("學", "學", True),
        ParsedToken("而", "而", True),
        ParsedToken("時", "時", True),
        ParsedToken("習", "習", True),
        ParsedToken("之", "之", True),
        ParsedToken("，", "，", False),
        ParsedToken("不", "不", True),
        ParsedToken("亦", "亦", True),
        ParsedToken("說", "說", True),
        ParsedToken("乎", "乎", True),
        ParsedToken("？", "？", False, True),
        ParsedToken("¶", "¶", False, True),
        ParsedToken("有", "有", True),
        ParsedToken("朋", "朋", True),
        ParsedToken("自", "自", True),
        ParsedToken("遠", "遠", True),
        ParsedToken("方", "方", True),
        ParsedToken("來", "來", True),
        ParsedToken("，", "，", False),
        ParsedToken("不", "不", True),
        ParsedToken("亦", "亦", True),
        ParsedToken("樂", "樂", True),
        ParsedToken("乎", "乎", True),
        ParsedToken("？", "？", False, True),
    ]
    assert_tokens_equals(s, classical_chinese, expected)
