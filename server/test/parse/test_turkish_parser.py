"""
TurkishParser tests.
"""
from __future__ import annotations

from src.parse.space_delimited_parser import TurkishParser


def test_downcase() -> None:
    "Turkish has problematic 'i' variants."
    cases = [
        ("CAT", "cat"),  # dummy case
        ("İÇİN", "için"),
        ("IŞIK", "ışık"),
        ("İçin", "için"),
        ("Işık", "ışık"),
    ]

    for text, expected_lcase in cases:
        assert TurkishParser().get_lowercase(text) == expected_lcase
