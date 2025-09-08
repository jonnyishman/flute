"""Book and Chapter models for storing book information."""

from .base import BaseModel, db


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


class Chapter(BaseModel):
    """Chapter model representing individual chapters within books."""

    __tablename__ = "chapters"

    book_id = db.Column(db.Integer, db.ForeignKey("books.id"), nullable=False)
    chapter_number = db.Column(db.Integer, nullable=False)
    word_count = db.Column(db.Integer, default=0, nullable=False)
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
