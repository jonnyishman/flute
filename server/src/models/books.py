"""Book and Chapter models for storing book information."""
from __future__ import annotations

import datetime as dt

from sqlalchemy import (
    Boolean,
    DateTime,
    ForeignKey,
    Integer,
    String,
    Text,
    UniqueConstraint,
)
from sqlalchemy.orm import Mapped, mapped_column, relationship

from src.models.base import db


class Book(db.Model):
    """Book model representing books in the application."""

    __tablename__ = "books"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)

    title: Mapped[str] = mapped_column(String(500), nullable=False)
    cover_art_filepath: Mapped[str | None] = mapped_column(String(500), nullable=True)
    source: Mapped[str | None] = mapped_column(String(500), nullable=True)

    is_archived: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)
    last_visited_chapter: Mapped[int | None] = mapped_column(Integer, nullable=True)
    last_visited_word_index: Mapped[int | None] = mapped_column(Integer, nullable=True)

    created_at: Mapped[dt.datetime] = mapped_column(DateTime, default=dt.datetime.now(dt.UTC), nullable=False)

    # Relationship to chapters
    chapters = relationship(
        "Chapter",
        back_populates="book",
        lazy="dynamic",
        cascade="all, delete-orphan"
    )


class Chapter(db.Model):
    """Chapter model representing individual chapters within books."""

    __tablename__ = "chapters"
    # Unique constraint on book_id + chapter_number
    __table_args__ = (
        UniqueConstraint("book_id", "chapter_number", name="uq_book_chapter"),
    )

    id: Mapped[int] = mapped_column(Integer, primary_key=True)

    book_id: Mapped[int] = mapped_column(Integer, ForeignKey(Book.id), nullable=False)
    chapter_number: Mapped[int] = mapped_column(Integer, nullable=False)
    content: Mapped[str] = mapped_column(Text, nullable=False)

    word_count: Mapped[int] = mapped_column(Integer, nullable=False)

    created_at: Mapped[dt.datetime] = mapped_column(DateTime, default=dt.datetime.now(dt.UTC), nullable=False)
    updated_at: Mapped[dt.datetime] = mapped_column(
        DateTime,
        default=dt.datetime.now(dt.UTC),
        onupdate=dt.datetime.now(dt.UTC),
        nullable=False
    )

    # Relationship to book
    book: Mapped[Book] = relationship(
        "Book",
        back_populates="chapters",
        lazy="select"
    )
