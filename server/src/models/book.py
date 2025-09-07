"""Book and Chapter models for the Flask application."""

from .base import BaseModel, db


class Book(BaseModel):
    """Book model."""

    __tablename__ = "books"
    title = db.Column(db.String(200), nullable=False, index=True)
    author = db.Column(db.String(100), nullable=False)
    description = db.Column(db.Text)
    cover_image_url = db.Column(db.String(500))
    total_chapters = db.Column(db.Integer, nullable=False, default=0)

    # Relationship to chapters
    chapters = db.relationship("Chapter", back_populates="book", cascade="all, delete-orphan")
    def __repr__(self):
        return f"<Book(id={self.id}, title='{self.title}', author='{self.author}')>"


class Chapter(BaseModel):
    """Chapter model."""

    __tablename__ = "chapters"
    book_id = db.Column(db.Integer, db.ForeignKey("books.id"), nullable=False, index=True)
    chapter_number = db.Column(db.Integer, nullable=False)
    title = db.Column(db.String(200))
    content = db.Column(db.Text, nullable=False)
    word_count = db.Column(db.Integer, nullable=False, default=0)

    # Relationship to book
    book = db.relationship("Book", back_populates="chapters")
    def __repr__(self):
        return f"<Chapter(id={self.id}, book_id={self.book_id}, chapter_number={self.chapter_number})>"