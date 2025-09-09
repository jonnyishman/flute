"""Pydantic schemas for request/response validation."""

from enum import Enum
from typing import Optional

from pydantic import BaseModel, Field


class SortField(str, Enum):
    """Valid sort fields for books."""
    
    ALPHABETICAL = "alphabetical"
    WORD_COUNT = "word_count"


class SortOrder(str, Enum):
    """Valid sort orders."""
    
    ASC = "asc"
    DESC = "desc"


class BookQueryParams(BaseModel):
    """Query parameters for books endpoint."""
    
    page: int = Field(default=1, ge=1, description="Page number")
    per_page: int = Field(default=10, ge=1, le=100, description="Items per page")
    sort_field: Optional[SortField] = Field(
        default=None, description="Field to sort by"
    )
    sort_order: SortOrder = Field(default=SortOrder.ASC, description="Sort order")


class BookSummary(BaseModel):
    """Book summary response model."""
    
    id: int
    title: str
    cover_art_filepath: Optional[str]
    source: Optional[str]
    last_visited_chapter: Optional[int]
    last_visited_word_index: Optional[int]
    word_count: int


class BookListResponse(BaseModel):
    """Books list response with pagination."""
    
    books: list[BookSummary]
    page: int
    per_page: int
    total: int
    total_pages: int
