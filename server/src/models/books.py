"""Book and Chapter models for storing book information."""
from __future__ import annotations

import datetime as dt
from enum import IntEnum

from sqlalchemy import (
    Boolean,
    CheckConstraint,
    DateTime,
    ForeignKey,
    Index,
    Integer,
    SmallInteger,
    String,
    Text,
)
from sqlalchemy.dialects.sqlite import insert
from sqlalchemy.orm import Mapped, mapped_column, relationship

from src.models.base import AuditMixin, db
from src.models.language import Language


class Book(db.Model, AuditMixin):
    """Book model representing books in the application."""

    __tablename__ = "books"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)

    language_id: Mapped[int] = mapped_column(Integer, ForeignKey(Language.id), nullable=False, index=True)
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
    language = relationship(Language)


class Chapter(db.Model, AuditMixin):
    """Chapter model representing individual chapters within books."""

    __tablename__ = "chapters"
    __table_args__ = (
        Index("ix_chapter_book_id_chapter_number", "book_id", "chapter_number", unique=True),
    )

    id: Mapped[int] = mapped_column(Integer, primary_key=True)

    book_id: Mapped[int] = mapped_column(Integer, ForeignKey(Book.id), nullable=False)
    chapter_number: Mapped[int] = mapped_column(Integer, nullable=False)
    content: Mapped[str] = mapped_column(Text, nullable=False)
    word_count: Mapped[int] = mapped_column(Integer, nullable=False)

    # Relationships
    book: Mapped[Book] = relationship("Book", back_populates="chapters", lazy="select")


class Term(db.Model):
    """One row per normalised term (word or phrase)"""
    __tablename__ = "terms"
    __table_args__ = (
        Index("ix_term_language_id_norm", "language_id", "norm", unique=True),
    )

    id: Mapped[int] = mapped_column(Integer, primary_key=True)

    language_id: Mapped[int] = mapped_column(Integer, ForeignKey(Language.id), nullable=False)
    norm: Mapped[str] = mapped_column(String(255), nullable=False)
    display: Mapped[str] = mapped_column(String(255), nullable=False)
    token_count: Mapped[int] = mapped_column(SmallInteger, nullable=False)

    # Relationships
    language = relationship(Language)


class BookVocab(db.Model):
    """
    Inverted index; which terms appear in which book, with term counts.
    Primary key is (book_id, term_id) so we can optionally use WITHOUT ROWID.
    """
    __tablename__ = "book_vocab"
    __table_args__ = (
        # Covering index in the other direction
        Index("ix_book_vocab_term_book_count", "term_id", "book_id", "term_count"),
        {"sqlite_with_rowid": False},
    )

    # Composite primary key: (book_id, term_id)
    book_id: Mapped[int] = mapped_column(Integer, ForeignKey(Book.id), primary_key=True)
    term_id: Mapped[int] = mapped_column(Integer, ForeignKey(Term.id), primary_key=True)
    term_count: Mapped[int] = mapped_column(Integer, nullable=False)


class LearningStatus(IntEnum):
    LEARNING = 1
    KNOWN = 2
    IGNORE = 3


NUM_LEARNING_STAGES = 5


class TermProgress(db.Model, AuditMixin):
    """Tracking user progress through unique terms"""
    __tablename__ = "term_progress"
    __table_args__ = (
        CheckConstraint("status IN (1, 2, 3)", name="ck_term_progress_status_valid"),
        CheckConstraint(
            "(status != 1) OR (learning_stage BETWEEN 1 AND 5)",
            name="ck_term_progress_learning_stage_valid"
        ),
        # For fast lookup of all learning/known terms
        Index("ix_term_progress_status_term", "status", "term_id"),
    )

    term_id: Mapped[int] = mapped_column(Integer, ForeignKey(Term.id), primary_key=True)
    status: Mapped[int] = mapped_column(SmallInteger, nullable=False)
    learning_stage: Mapped[int | None] = mapped_column(SmallInteger, nullable=True)
    translation: Mapped[str | None] = mapped_column(String(500), nullable=True)


class BookTotals(db.Model):
    """Per-book totals that don't change unless the book test changes"""
    __tablename__ = "book_totals"

    book_id: Mapped[int] = mapped_column(Integer, ForeignKey(Book.id, ondelete="CASCADE"), primary_key=True)
    total_terms: Mapped[int] = mapped_column(Integer, nullable=False)
    total_types: Mapped[int] = mapped_column(Integer, nullable=False)

    @classmethod
    def upsert_stmt(cls, book_id: int, total_terms: int, total_types: int):
        """Return an upsert statement for the given book totals."""
        return insert(cls).values(
            book_id=book_id,
            total_terms=total_terms,
            total_types=total_types,
        ).on_conflict_do_update(
            index_elements=[cls.book_id],
            set_={
                "total_terms": total_terms,
                "total_types": total_types,
            }
        )
