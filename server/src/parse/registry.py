"""
Parser registry.

List of available parsers.
"""
from __future__ import annotations

from importlib.metadata import entry_points

from src.parse.base import AbstractParser
from src.parse.character_parser import ClassicalChineseParser
from src.parse.mecab_parser import JapaneseParser
from src.parse.space_delimited_parser import SpaceDelimitedParser, TurkishParser

FLUTE_PARSERS: dict[str, type[AbstractParser]] = {
    "spacedel": SpaceDelimitedParser,
    "turkish": TurkishParser,
    "japanese": JapaneseParser,
    "classicalchinese": ClassicalChineseParser,
}


def init_parser_plugins() -> None:
    """Initialize parsers from plugins."""
    for custom_parser_ep in entry_points().select(group="lute.plugin.parse"):
        name = custom_parser_ep.name
        klass = custom_parser_ep.load()
        if issubclass(klass, AbstractParser):
            FLUTE_PARSERS[name] = klass
        else:
            raise ValueError(f"{name} is not a subclass of AbstractParser")


def get_parser(parser_name: str) -> AbstractParser:
    """Return the supported parser with the given name."""
    if parser_name not in FLUTE_PARSERS:
        raise ValueError(f"Unknown parser type '{parser_name}'")
    pclass = FLUTE_PARSERS[parser_name]
    if not pclass.is_supported():
        raise ValueError(f"Unsupported parser type '{parser_name}'")
    return pclass()


def is_supported(parser_name: str) -> bool:
    """Return True if the specified parser is present and supported."""
    if (parser := FLUTE_PARSERS.get(parser_name)) is None:
        return False
    return parser.is_supported()


def supported_parsers() -> dict[str, type[AbstractParser]]:
    """List of supported parser strings and classes."""
    return {k: v for k, v in FLUTE_PARSERS.items() if v.is_supported()}


def supported_parser_types() -> set[str]:
    """List of supported Language.parser_types."""
    return set(supported_parsers().keys())
