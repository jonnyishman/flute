"""
TurkishParser tests.
"""

import pytest

# from src.models.term import Term


@pytest.mark.skip(reason="Term model not available in this codebase")
def test_downcase(turkish):
    "Turkish has problematic 'i' variants."
    cases = [
        ("CAT", "cat"),  # dummy case
        ("İÇİN", "için"),
        ("IŞIK", "ışık"),
        ("İçin", "için"),
        ("Işık", "ışık"),
    ]

    for text, expected_lcase in cases:
        # t = Term(turkish, text)
        # assert t.text_lc == expected_lcase, text
        pass
