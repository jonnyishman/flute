"""API routes for book-related operations"""
from typing import cast

import sqlalchemy as sa
from flask import abort
from flask_pydantic import validate
from more_itertools import chunked
from pydantic import BaseModel
from sqlalchemy.dialects.sqlite import insert
from sqlalchemy.exc import IntegrityError

from src.api.routes import api_bp
from src.models import Book, BookTotals, BookVocab, Chapter, Token, TokenKind, db


class CreateBookRequest(BaseModel):
    """Request model for creating a new book."""

    title: str
    language_id: int
    chapters: list[str]
    source: str | None = None
    cover_art_filepath: str | None = None


class CreateBookResponse(BaseModel):
    """Response model for book creation"""

    book_id: int


# Super basic for now, will replace with proper ones later
def tokenise_and_count(context: str) -> dict[str, int]:
    """Tokenises the given context and returns a word count dictionary."""
    # Simple whitespace tokenizer; replace with a more sophisticated one if needed
    tokens = context.split()
    word_count: dict[str, int] = {}
    for token in tokens:
        token = token.lower().strip(".,!?;:\"'()[]{}")
        if token:
            word_count[token] = word_count.get(token, 0) + 1
    return word_count


@api_bp.route("/books", methods=["POST"])
@validate()
def create_book(body: CreateBookRequest) -> tuple[CreateBookResponse, int]:
    """
    Creates a new book with chapters, builds token directionary, populates inverted index
    and per-book totals.
    """
    # Tokenise chapters and compute word counts
    chapter_token_counts = [tokenise_and_count(chapter) for chapter in body.chapters]
    chapter_word_counts = [sum(counts.values()) for counts in chapter_token_counts]
    book_token_counts = {}
    for counts in chapter_token_counts:
        for token, count in counts.items():
            book_token_counts[token] = book_token_counts.get(token, 0) + count

    # Insert book, get book ID
    insert_book_stmt = insert(Book).values(
        language_id=body.language_id,
        title=body.title,
        cover_art_filepath=body.cover_art_filepath,
        source=body.source,
        is_archived=False,
    )
    try:
        result = db.session.execute(insert_book_stmt)
    except IntegrityError:
        abort(404, description=f"invalid language_id: '{body.language_id}'")

    book_id = cast("list[int]", result.inserted_primary_key)[0]

    # Insert chapters with their computed word_count
    params = [
        {
            "book_id": book_id,
            "chapter_number": i,
            "content": content,
            "word_count": word_count,
        }
        for i, (content, word_count)
        in enumerate(zip(body.chapters, chapter_word_counts, strict=True), start=1)
    ]
    if params:  # Only insert if there are chapters
        db.session.execute(insert(Chapter), params)

    # Upsert tokens into the global token table, chunked to avoid too many parameters
    all_tokens = list(book_token_counts.keys())
    stmt = insert(Token).on_conflict_do_nothing(index_elements=["language_id", "norm"])
    for chunk in chunked(all_tokens, 500):
        params = [
            {
                "language_id": body.language_id,
                "norm": token,
                "kind": TokenKind.WORD.value,
            }
            for token in chunk
        ]
        db.session.execute(stmt, params)

    # Get mapping of token norms to IDs
    # TODO: see if this can be replaced with RETURNING in the insert above
    token_to_id: dict[str, int] = {}
    for chunk in chunked(all_tokens, 500):
        rows = db.session.execute(
            sa.select(Token.id, Token.norm).where(
                Token.language_id == body.language_id,
                Token.norm.in_(chunk)
            )
        ).all()
        token_to_id.update({norm: id for id, norm in rows})

    # Build inverted index for book
    params = [
        {"book_id": book_id, "token_id": token_to_id[token], "token_count": count}
        for token, count in book_token_counts.items()
    ]
    for chunk in chunked(params, 500):
        db.session.execute(insert(BookVocab), chunk)

    # Upsert per-book totals
    total_tokens = sum(book_token_counts.values())
    total_types = len(book_token_counts)
    db.session.execute(BookTotals.upsert_stmt(book_id, total_tokens, total_types))

    db.session.commit()
    return CreateBookResponse(book_id=book_id), 201
