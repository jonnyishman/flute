"""Common classes used for all parsing."""
from __future__ import annotations

from typing import TYPE_CHECKING

from abc import ABC, abstractmethod
from dataclasses import dataclass

if TYPE_CHECKING:
    from src.models.language import Language 


@dataclass(frozen=True)
class ParsedToken:
    """A single parsed token from an input text.

    As tokens are created, the class counters (starting with cls_) are
    assigned to the ParsedToken and then incremented appropriately.
    """

    token: str
    is_word: bool
    is_end_of_sentence: bool = False

    @property
    def is_end_of_paragraph(self) -> bool:
        """Check if token represents end of paragraph."""
        return self.token.strip() == "¶"

    def __repr__(self) -> str:
        attrs = [
            f"word: {self.is_word}",
            f"eos: {self.is_end_of_sentence}",
        ]
        return f'<"{self.token}" ({", ".join(attrs)})>'


class AbstractParser(ABC):
    """Abstract parser, inherited from by all parsers.

    Attributes:
        data_directory: Optional full path to a directory that the parser uses.
            Should be initialized with init_data_directory().
    """

    data_directory: str | None = None

    @classmethod
    def uses_data_directory(cls) -> bool:
        """True if the parser needs user-supplied data."""
        return False

    @classmethod
    def init_data_directory(cls) -> None:
        """Initialize the data_directory if needed.

        Not necessary for all parsers.
        """

    @classmethod
    def is_supported(cls) -> bool:
        """True if the parser will work on the current system.

        Some parsers, such as Japanese, require external components to be
        present and configured. If missing, this should return False.
        """
        return True

    @classmethod
    @abstractmethod
    def name(cls) -> str:
        """Parser name, for displaying in UI."""

    @abstractmethod
    def get_parsed_tokens(self, text: str, language: Language) -> list[ParsedToken]:
        """Get an array of ParsedTokens from the input text for the given language."""

    def get_reading(self, text: str) -> str | None:
        """Get the pronunciation for the given text.

        For most languages, this can't be automated.
        """

    def get_lowercase(self, text: str) -> str:
        """Return the lowercase text.

        Most languages can use the built-in lowercase operation,
        but some (like Turkish) need special handling.
        """
        return text.lower()
