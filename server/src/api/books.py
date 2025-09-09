"""Books API endpoints."""

import math
from typing import Any

from flask import Blueprint
from flask_pydantic import validate
from sqlalchemy import func, select

from src.models import db
from src.models.book import Book, Chapter
from src.schemas import BookListResponse, BookQueryParams, BookSummary, SortField

# Create books blueprint
books_bp = Blueprint("books", __name__)


@books_bp.route("", methods=["GET"])
@validate()
def get_books(query: BookQueryParams) -> dict[str, Any]:
    """Get paginated and sorted list of book summaries.
    
    Args:
        query: Validated query parameters
        
    Returns:
        JSON response with book summaries and pagination info
    """
    # Build base query using SQLAlchemy Core for efficiency
    # Calculate word_count as sum of all chapter word counts per book
    word_count_subquery = (
        select(
            Chapter.book_id,
            func.coalesce(func.sum(Chapter.word_count), 0).label("total_word_count")
        )
        .group_by(Chapter.book_id)
        .subquery()
    )
    
    # Main query to get books with aggregated word count
    books_query = (
        select(
            Book.id,
            Book.title,
            Book.cover_art_filepath,
            Book.source,
            Book.last_visited_chapter,
            Book.last_visited_word_index,
            func.coalesce(word_count_subquery.c.total_word_count, 0).label("word_count")
        )
        .outerjoin(word_count_subquery, Book.id == word_count_subquery.c.book_id)
        .where(~Book.is_archived)  # Only include non-archived books
    )
    
    # Apply sorting
    if query.sort_field == SortField.ALPHABETICAL:
        if query.sort_order.value == "desc":
            books_query = books_query.order_by(Book.title.desc())
        else:
            books_query = books_query.order_by(Book.title.asc())
    elif query.sort_field == SortField.WORD_COUNT:
        if query.sort_order.value == "desc":
            books_query = books_query.order_by(func.coalesce(word_count_subquery.c.total_word_count, 0).desc())
        else:
            books_query = books_query.order_by(func.coalesce(word_count_subquery.c.total_word_count, 0).asc())
    else:
        # Default sort by ID
        books_query = books_query.order_by(Book.id)
    
    # Get total count for pagination
    count_query = select(func.count()).select_from(
        select(Book.id).where(~Book.is_archived)
    )
    total = db.session.execute(count_query).scalar()
    
    # Apply pagination
    offset = (query.page - 1) * query.per_page
    books_query = books_query.offset(offset).limit(query.per_page)
    
    # Execute query
    result = db.session.execute(books_query).all()
    
    # Convert to response format
    books = [
        BookSummary(
            id=row.id,
            title=row.title,
            cover_art_filepath=row.cover_art_filepath,
            source=row.source,
            last_visited_chapter=row.last_visited_chapter,
            last_visited_word_index=row.last_visited_word_index,
            word_count=row.word_count
        )
        for row in result
    ]
    
    # Calculate pagination info
    total_pages = math.ceil(total / query.per_page) if total > 0 else 0
    
    response = BookListResponse(
        books=books,
        page=query.page,
        per_page=query.per_page,
        total=total,
        total_pages=total_pages
    )
    
    return response.model_dump()