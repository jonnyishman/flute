"""SQLAlchemy models package."""

from src.models.base import db
from src.models.books import Book, Chapter

__all__ = ["db", "Book", "Chapter"]
