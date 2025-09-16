"""API routes for book-related operations"""
from typing import TYPE_CHECKING, cast

import sqlalchemy as sa
from flask import abort
from flask_pydantic import validate
from more_itertools import chunked
from pydantic import BaseModel
from sqlalchemy.dialects.sqlite import insert
from sqlalchemy.exc import IntegrityError

from src.api.routes import api_bp
from src.models import Book, BookTotals, BookVocab, Chapter, Language, Term, db
from src.parse.registry import get_parser

if TYPE_CHECKING:
    from src.parse.base import ParsedToken


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


@api_bp.route("/books", methods=["POST"])
@validate()
def create_book(body: CreateBookRequest) -> tuple[CreateBookResponse, int]:
    """
    Creates a new book with chapters, builds token directionary, populates inverted index
    and per-book totals.
    """
    # Check language exists and grab parser
    if not (language := db.session.get(Language, body.language_id)):
        abort(404, description=f"invalid language_id: '{body.language_id}'")

    try:
        parser = get_parser(language.parser_type)
    except ValueError as exc:
        abort(400, description=str(exc))

    # Tokenise chapters and compute word counts
    chapter_term_counts: list[dict[ParsedToken, int]] = []
    for chapter in body.chapters:
        parsed_tokens = parser.get_parsed_tokens(chapter.strip(), language)
        term_counts: dict[ParsedToken, int] = {}
        for token in parsed_tokens:
            if token.is_word:
                term_counts[token] = term_counts.get(token, 0) + 1
        chapter_term_counts.append(term_counts)

    book_term_counts: dict[ParsedToken, int] = {}
    for counts in chapter_term_counts:
        for token, count in counts.items():
            book_term_counts[token] = book_term_counts.get(token, 0) + count

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
            "word_count": sum(term_counts.values()),
        }
        for i, (content, term_counts)
        in enumerate(zip(body.chapters, chapter_term_counts, strict=True), start=1)
    ]
    if params:  # Only insert if there are chapters
        db.session.execute(insert(Chapter), params)

    # Upsert tokens into the global token table, chunked to avoid too many parameters
    all_tokens = list(book_term_counts.keys())
    stmt = insert(Term).on_conflict_do_nothing(index_elements=["language_id", "norm"])
    for chunk in chunked(all_tokens, 500):
        params = [
            {
                "language_id": body.language_id,
                "norm": token.norm,
                "display": token.token,
                "token_count": 1,
            }
            for token in chunk
        ]
        db.session.execute(stmt, params)

    # Get mapping of token norms to IDs
    term_to_id: dict[str, int] = {}
    for chunk in chunked(all_tokens, 500):
        rows = db.session.execute(
            sa.select(Term.id, Term.norm).where(
                Term.language_id == body.language_id,
                Term.norm.in_(token.norm for token in chunk)
            )
        ).all()
        term_to_id.update({norm: id for id, norm in rows})

    # Build inverted index for book
    params = [
        {"book_id": book_id, "term_id": term_id, "term_count": count}
        for term, count in book_term_counts.items()
        if (term_id := term_to_id.get(term.norm))
    ]
    for chunk in chunked(params, 500):
        db.session.execute(insert(BookVocab), chunk)

    # Upsert per-book totals
    total_tokens = sum(book_term_counts.values())
    total_types = len(book_term_counts)
    db.session.execute(BookTotals.upsert_stmt(book_id, total_tokens, total_types))

    db.session.commit()
    return CreateBookResponse(book_id=book_id), 201
