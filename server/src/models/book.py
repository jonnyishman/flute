"""Book model for storing book information."""

from typing import TYPE_CHECKING

from .base import BaseModel, db

if TYPE_CHECKING:
    from .chapter import Chapter


class Book(BaseModel):
    """Book model representing books in the application."""

    __tablename__ = "books"

    title = db.Column(db.String(255), nullable=False)
    cover_art_filepath = db.Column(db.String(500), nullable=True)
    source = db.Column(db.String(255), nullable=True)
    is_archived = db.Column(db.Boolean, default=False, nullable=False)
    last_visited_chapter = db.Column(db.Integer, nullable=True)
    last_visited_word_index = db.Column(db.Integer, nullable=True)

    # Relationship to chapters
    chapters = db.relationship(
        "Chapter",
        back_populates="book",
        lazy="dynamic",
        cascade="all, delete-orphan"
    )

    def __repr__(self) -> str:
        """String representation of the book."""
        return f"<Book {self.title}>"

    @property
    def chapter_count(self) -> int:
        """Get the total number of chapters in this book."""
        return self.chapters.count()