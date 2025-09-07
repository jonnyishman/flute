"""Book and Chapter models for the Flask application."""

from typing import List
from sqlalchemy import Column, Integer, String, Text, ForeignKey, DateTime
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func

from .base import BaseModel


class Book(BaseModel):
    """Book model."""
    
    __tablename__ = "books"
    
    id = Column(Integer, primary_key=True, index=True)
    title = Column(String(200), nullable=False, index=True)
    author = Column(String(100), nullable=False)
    description = Column(Text)
    cover_image_url = Column(String(500))
    total_chapters = Column(Integer, nullable=False, default=0)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    
    # Relationship to chapters
    chapters = relationship("Chapter", back_populates="book", cascade="all, delete-orphan")
    
    def __repr__(self):
        return f"<Book(id={self.id}, title='{self.title}', author='{self.author}')>"


class Chapter(BaseModel):
    """Chapter model."""
    
    __tablename__ = "chapters"
    
    id = Column(Integer, primary_key=True, index=True)
    book_id = Column(Integer, ForeignKey("books.id"), nullable=False, index=True)
    chapter_number = Column(Integer, nullable=False)
    title = Column(String(200))
    content = Column(Text, nullable=False)
    word_count = Column(Integer, nullable=False, default=0)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    
    # Relationship to book
    book = relationship("Book", back_populates="chapters")
    
    def __repr__(self):
        return f"<Chapter(id={self.id}, book_id={self.book_id}, chapter_number={self.chapter_number})>"