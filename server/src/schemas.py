"""Pydantic schemas for request/response validation."""

from typing import Optional, List
from datetime import datetime
from pydantic import BaseModel, Field, EmailStr


class UserCreate(BaseModel):
    """Schema for creating a new user."""
    
    username: str = Field(..., min_length=3, max_length=80)
    email: EmailStr
    first_name: Optional[str] = Field(None, max_length=50)
    last_name: Optional[str] = Field(None, max_length=50)


class UserUpdate(BaseModel):
    """Schema for updating an existing user."""
    
    username: Optional[str] = Field(None, min_length=3, max_length=80)
    email: Optional[EmailStr] = None
    first_name: Optional[str] = Field(None, max_length=50)
    last_name: Optional[str] = Field(None, max_length=50)
    is_active: Optional[bool] = None


class UserResponse(BaseModel):
    """Schema for user response data."""
    
    id: int
    username: str
    email: str
    first_name: Optional[str] = None
    last_name: Optional[str] = None
    is_active: bool
    full_name: str
    
    class Config:
        """Pydantic configuration."""
        from_attributes = True


# Book and Chapter schemas
class ChapterResponse(BaseModel):
    """Schema for chapter response data."""
    
    id: int
    chapter_number: int
    title: Optional[str] = None
    content: str
    word_count: int
    
    class Config:
        """Pydantic configuration."""
        from_attributes = True


class BookResponse(BaseModel):
    """Schema for book response data."""
    
    id: int
    title: str
    author: str
    description: Optional[str] = None
    cover_image_url: Optional[str] = None
    total_chapters: int
    created_at: datetime
    
    class Config:
        """Pydantic configuration."""
        from_attributes = True


class BookWithChaptersResponse(BookResponse):
    """Schema for book response data with chapters included."""
    
    chapters: List[ChapterResponse] = []


class BookCreate(BaseModel):
    """Schema for creating a new book."""
    
    title: str = Field(..., min_length=1, max_length=200)
    author: str = Field(..., min_length=1, max_length=100)
    description: Optional[str] = None
    cover_image_url: Optional[str] = None


class ChapterCreate(BaseModel):
    """Schema for creating a new chapter."""
    
    chapter_number: int = Field(..., ge=1)
    title: Optional[str] = Field(None, max_length=200)
    content: str = Field(..., min_length=1)