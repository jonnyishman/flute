"""Chapter model for storing book chapters."""

from typing import TYPE_CHECKING

from .base import BaseModel, db

if TYPE_CHECKING:
    from .book import Book


class Chapter(BaseModel):
    """Chapter model representing individual chapters within books."""

    __tablename__ = "chapters"

    book_id = db.Column(db.Integer, db.ForeignKey("books.id"), nullable=False)
    chapter_number = db.Column(db.Integer, nullable=False)
    word_count = db.Column(db.Integer, nullable=False, default=0)
    content = db.Column(db.Text, nullable=False)

    # Unique constraint on book_id + chapter_number
    __table_args__ = (
        db.UniqueConstraint("book_id", "chapter_number", name="uq_book_chapter"),
    )

    # Relationship to book
    book = db.relationship(
        "Book",
        back_populates="chapters",
        lazy="select"
    )

    def __repr__(self) -> str:
        """String representation of the chapter."""
        return f"<Chapter {self.chapter_number} of Book {self.book_id}>"

    @property
    def title(self) -> str:
        """Generate a display title for the chapter."""
        return f"Chapter {self.chapter_number}"