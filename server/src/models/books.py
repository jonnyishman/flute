"""Book and Chapter models for storing book information."""
from __future__ import annotations

from enum import IntEnum
from typing import TYPE_CHECKING

from sqlalchemy import (
    Boolean,
    CheckConstraint,
    DateTime,
    ForeignKey,
    Index,
    Integer,
    String,
    Text,
    UniqueConstraint,
    func,
)
from sqlalchemy.orm import Mapped, declarative_mixin, mapped_column, relationship

from src.models.base import db

if TYPE_CHECKING:
    import datetime as dt


@declarative_mixin
class AuditMixin:
    created_at: Mapped[dt.datetime] = mapped_column(
        DateTime,
        server_default=func.current_timestamp(),
        nullable=False
    )
    updated_at: Mapped[dt.datetime] = mapped_column(
        DateTime,
        server_default=func.current_timestamp(),
        onupdate=func.current_timestamp(),
        nullable=False
    )


class Book(db.Model, AuditMixin):
    """Book model representing books in the application."""

    __tablename__ = "books"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)

    title: Mapped[str] = mapped_column(String(500), nullable=False)
    cover_art_filepath: Mapped[str | None] = mapped_column(String(500), nullable=True)
    source: Mapped[str | None] = mapped_column(String(500), nullable=True)

    is_archived: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)
    last_visited_chapter: Mapped[int | None] = mapped_column(Integer, nullable=True)
    last_visited_word_index: Mapped[int | None] = mapped_column(Integer, nullable=True)
    last_read: Mapped[dt.datetime | None] = mapped_column(DateTime, nullable=True)

    # Relationships
    chapters = relationship(
        "Chapter",
        back_populates="book",
        lazy="dynamic",
        cascade="all, delete-orphan"
    )


class Chapter(db.Model, AuditMixin):
    """Chapter model representing individual chapters within books."""

    __tablename__ = "chapters"
    __table_args__ = (
        # Unique constraint on book_id + chapter_number
        UniqueConstraint("book_id", "chapter_number", name="uq_book_chapter"),
    )

    id: Mapped[int] = mapped_column(Integer, primary_key=True)

    book_id: Mapped[int] = mapped_column(Integer, ForeignKey(Book.id), nullable=False)
    chapter_number: Mapped[int] = mapped_column(Integer, nullable=False)
    content: Mapped[str] = mapped_column(Text, nullable=False)

    # Relationships
    book: Mapped[Book] = relationship("Book", back_populates="chapters", lazy="select")


class TokenKind(IntEnum):
    WORD = 1
    PHRASE = 2


class Token(db.Model):
    """One row per normalised token (word or phrase)"""
    __tablename__ = "tokens"
    __table_args__ = (
        CheckConstraint("kind IN (1, 2)", name="ck_token_kind_valid"),
    )

    id: Mapped[int] = mapped_column(Integer, primary_key=True)

    norm: Mapped[str] = mapped_column(String(255), unique=True, nullable=False)
    kind: Mapped[int] = mapped_column(
        Integer,
        nullable=False,
        server_default=str(TokenKind.WORD.value)
    )


class BookVocab(db.Model):
    """
    Inverted index; which tokens appear in which book, with token counts.
    Primary key is (book_id, token_id) so we can optionally use WITHOUT ROWID.
    """
    __tablename__ = "book_vocab"
    __table_args__ = (
        # Covering index in the other direction
        Index("ix_book_vocab_token_book_count", "token_id", "book_id", "token_count"),
        {"sqlite_with_rowid": False},
    )

    # Composite primary key: (book_id, token_id)
    book_id: Mapped[int] = mapped_column(Integer, ForeignKey(Book.id), primary_key=True)
    token_id: Mapped[int] = mapped_column(Integer, ForeignKey(Token.id), primary_key=True)
    token_count: Mapped[int] = mapped_column(Integer, nullable=False)


class LearningStatus(IntEnum):
    LEARNING = 1
    KNOWN = 2
    IGNORE = 3


NUM_LEARNING_STAGES = 5


class TokenProgress(db.Model, AuditMixin):
    """Tracking user progress through unique tokens"""
    __tablename__ = "token_progress"
    __table_args__ = (
        CheckConstraint("status IN (1, 2, 3)", name="ck_token_progress_status_valid"),
        CheckConstraint(
            "(status != 1) OR (learning_stage BETWEEN 1 AND 5)",
            name="ck_token_progress_learning_stage_valid"
        ),
        # For fast lookup of all learning/known tokens
        Index("ix_token_progress_status_token", "status", "token_id"),
    )

    token_id: Mapped[int] = mapped_column(Integer, ForeignKey(Token.id), primary_key=True)
    status: Mapped[int] = mapped_column(Integer, nullable=False)
    learning_stage: Mapped[int | None] = mapped_column(Integer, nullable=True)
    translation: Mapped[str | None] = mapped_column(String(500), nullable=True)


class BookTotals(db.Model):
    """Per-book totals that don't change unless the book test changes"""
    __tablename__ = "book_totals"

    book_id: Mapped[int] = mapped_column(Integer, ForeignKey(Book.id, ondelete="CASCADE"), primary_key=True)
    total_tokens: Mapped[int] = mapped_column(Integer, nullable=False)
    total_types: Mapped[int] = mapped_column(Integer, nullable=False)
