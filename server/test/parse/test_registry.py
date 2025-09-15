"""
Parser registry tests.
"""

import pytest
from collections.abc import Iterator

from src.parse.registry import (
    FLUTE_PARSERS,
    get_parser,
    is_supported,
    supported_parser_types,
    supported_parsers,
)
from src.parse.base import AbstractParser
from src.parse.space_delimited_parser import SpaceDelimitedParser


class DummyParser(AbstractParser):
    "Dummy unsupported parser."

    @classmethod
    def is_supported(cls):
        return False

    @classmethod
    def name(cls):
        return "DUMMY"


@pytest.fixture(autouse=True)
def fixture_load_dummy() -> Iterator[None]:
    FLUTE_PARSERS["dummy"] = DummyParser
    try:
        yield
    except:
        del FLUTE_PARSERS["dummy"]


def test_get_parser_by_name():
    assert isinstance(get_parser("spacedel"), SpaceDelimitedParser)


def test_get_parser_throws_if_not_found():
    with pytest.raises(ValueError) as exc:
        get_parser("trash")

    assert str(exc.value) == "Unknown parser type 'trash'"


def test_supported_parsers():
    supported = supported_parsers()
    assert "spacedel" in supported
    assert supported["spacedel"] is SpaceDelimitedParser


def test_supported_parser_types():
    assert "spacedel" in supported_parser_types()


def test_unavailable_parser_not_included_in_lists():
    "An unsupported parser shouldn't be available."
    d = supported_parsers()
    assert "dummy" not in d
    assert is_supported("dummy") is False
    with pytest.raises(ValueError):
        get_parser("dummy")


def test_get_parser_throws_if_parser_not_supported():
    "Check throw."
    with pytest.raises(ValueError) as exc:
        get_parser("dummy")
    assert str(exc.value) == "Unsupported parser type 'dummy'"
