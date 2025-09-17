"""API routes for book-related operations"""
import enum
from typing import TYPE_CHECKING, cast

import sqlalchemy as sa
from flask import abort
from flask_pydantic import validate
from more_itertools import chunked
from pydantic import BaseModel, ConfigDict, Field
from sqlalchemy.dialects.sqlite import insert
from sqlalchemy.exc import IntegrityError

from src.api.routes import api_bp
from src.models import (
    Book,
    BookTotals,
    BookVocab,
    Chapter,
    Language,
    LearningStatus,
    Term,
    TermProgress,
    db,
)
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


class SortOption(str, enum.Enum):
    TITLE = "title"
    LAST_READ = "last_read"
    LEARNING_TERMS = "learning_terms"
    UNKNOWN_TERMS = "unknown_terms"


class SortOrder(str, enum.Enum):
    ASC = "asc"
    DESC = "desc"


class BookSummariesRequest(BaseModel):
    language_id: int
    sort_option: SortOption | None = None
    sort_order: SortOrder = SortOrder.ASC
    page: int = Field(default=1, ge=1)
    per_page: int = Field(default=50, ge=1, le=100)


class BookSummary(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    book_id: int
    title: str
    cover_art_filepath: str | None
    total_terms: int
    known_terms: int
    learning_terms: int
    unknown_terms: int


class BookSummariesResponse(BaseModel):
    summaries: list[BookSummary]


@api_bp.route("/books", methods=["GET"])
@validate()
def get_book_summaries(query: BookSummariesRequest) -> BookSummariesResponse:
    """
    Retrieves paginated summaries of books in a given language, includes aggregated term counts for each book
    """
    # filters
    base_where = [Book.is_archived.is_(False), Book.language_id == query.language_id]

    # progress CTE, aggregate only over terms with progress for all books
    progress = (
        sa.select(
            BookVocab.book_id,
            sa.func.sum(sa.case((TermProgress.status == LearningStatus.KNOWN, BookVocab.term_count), else_=0)).label("known_terms"),
            sa.func.sum(sa.case((TermProgress.status == LearningStatus.LEARNING, BookVocab.term_count), else_=0)).label("learning_terms"),
            sa.func.sum(sa.case((TermProgress.status == LearningStatus.IGNORE, BookVocab.term_count), else_=0)).label("ignored_terms"),
        )
        .select_from(
            sa.join(TermProgress, BookVocab, TermProgress.term_id == BookVocab.term_id)
            .join(Book, BookVocab.book_id == Book.id)
        )
        .where(*base_where)
        .group_by(BookVocab.book_id)
    ).cte("progress")

    # expressions for select and sort
    total_terms = sa.func.coalesce(BookTotals.total_terms, 0)
    known_terms = sa.func.coalesce(progress.c.known_terms, 0)
    learning_terms = sa.func.coalesce(progress.c.learning_terms, 0)
    ignored_terms = sa.func.coalesce(progress.c.ignored_terms, 0)
    unknown_terms = total_terms - known_terms - learning_terms - ignored_terms
    # title collation (SQLite NOCASE for a natural sort)
    title_expr = sa.collate(Book.title, "NOCASE")

    if query.sort_option == SortOption.LEARNING_TERMS:
        sort = learning_terms
    elif query.sort_option == SortOption.UNKNOWN_TERMS:
        sort = unknown_terms
    elif query.sort_option == SortOption.LAST_READ:
        sort = Book.last_read
    else:  # Default to TITLE
        sort = title_expr

    sort = sort.asc() if query.sort_order == SortOrder.ASC else sort.desc()

    # main query
    stmt = (
        sa.select(
            Book.id.label("book_id"),
            Book.title.label("title"),
            Book.cover_art_filepath.label("cover_art_filepath"),
            total_terms.label("total_terms"),
            known_terms.label("known_terms"),
            learning_terms.label("learning_terms"),
            unknown_terms.label("unknown_terms"),
        )
        .select_from(
            sa.outerjoin(Book, BookTotals, BookTotals.book_id == Book.id)
            .outerjoin(progress, progress.c.book_id == Book.id)
        )
        .where(*base_where)
        .order_by(sort)
        .limit(query.per_page)
        .offset((query.page - 1) * query.per_page)
    )
    rows = db.session.execute(stmt).all()
    return BookSummariesResponse(summaries=[BookSummary.model_validate(row) for row in rows])
