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
    from src.parse.base import AbstractParser, ParsedToken


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


class TermHighlight(BaseModel):
    """A highlighted term in chapter text."""
    term_id: int
    display: str
    start_pos: int
    end_pos: int
    status: LearningStatus
    learning_stage: int | None = None


class ChapterResponse(BaseModel):
    """Chapter details."""
    model_config = ConfigDict(from_attributes=True)

    id: int
    chapter_number: int
    content: str
    word_count: int


class ChapterWithHighlightsResponse(BaseModel):
    """Chapter content with term highlights for user's known/learning terms."""
    chapter: ChapterResponse
    term_highlights: list[TermHighlight]


@api_bp.route("/books/<int:book_id>/chapters/<int:chapter_number>", methods=["GET"])
@validate()
def get_chapter_with_highlights(book_id: int, chapter_number: int) -> ChapterWithHighlightsResponse:
    """
    Get chapter content with highlights for user's known/learning terms.

    Returns chapter text and positions of all terms the user has progress on,
    supporting both single-token and multi-token terms.
    """
    # Get book and verify it exists first
    book_stmt = sa.select(Book).where(Book.id == book_id)
    if not (book := db.session.execute(book_stmt).scalar_one_or_none()):
        abort(404, description=f"Book {book_id} not found")

    # Get chapter and verify it exists
    chapter_stmt = sa.select(Chapter).where(
        Chapter.book_id == book_id,
        Chapter.chapter_number == chapter_number
    )
    if not (chapter := db.session.execute(chapter_stmt).scalar_one_or_none()):
        abort(404, description=f"Chapter {chapter_number} not found in book {book_id}")

    # ULTRA-OPTIMIZED APPROACH: Term-first matching for rare multi-token terms
    # Phase 1: Parse chapter once and extract single tokens
    # Phase 2: Only process multi-token terms if user has any (early exit optimization)

    parser = get_parser(book.language.parser_type)
    parsed_tokens = parser.get_parsed_tokens(chapter.content, book.language)

    # Extract normalized word tokens for single-token matching
    chapter_tokens: set[str] = {token.norm for token in parsed_tokens if token.is_word}

    if not chapter_tokens:
        return ChapterWithHighlightsResponse(
            chapter=ChapterResponse.model_validate(chapter),
            term_highlights=[]
        )

    # Phase 1: Query single-token terms that appear in chapter
    single_token_terms_stmt = (
        sa.select(
            Term.id,
            Term.norm,
            Term.display,
            Term.token_count,
            TermProgress.status,
            TermProgress.learning_stage,
        )
        .select_from(
            sa.join(Term, TermProgress, Term.id == TermProgress.term_id)
        )
        .where(
            Term.norm.in_(chapter_tokens),
            Term.token_count == 1,
            Term.language_id == book.language_id,
            TermProgress.status.in_([LearningStatus.KNOWN, LearningStatus.LEARNING])
        )
    )

    single_token_terms = list(db.session.execute(single_token_terms_stmt).all())

    # Phase 2: Early exit check - does user have ANY multi-token terms?
    has_multi_token_terms = db.session.execute(
        sa.select(sa.func.count(Term.id))
        .select_from(
            sa.join(Term, TermProgress, Term.id == TermProgress.term_id)
        )
        .where(
            Term.language_id == book.language_id,
            Term.token_count > 1,
            TermProgress.status.in_([LearningStatus.KNOWN, LearningStatus.LEARNING])
        )
    ).scalar()

    multi_token_terms = []
    if has_multi_token_terms > 0:
        # Only query multi-token terms if user actually has some
        multi_token_terms_stmt = (
            sa.select(
                Term.id,
                Term.norm,
                Term.display,
                Term.token_count,
                TermProgress.status,
                TermProgress.learning_stage,
            )
            .select_from(
                sa.join(Term, TermProgress, Term.id == TermProgress.term_id)
            )
            .where(
                Term.language_id == book.language_id,
                Term.token_count > 1,
                TermProgress.status.in_([LearningStatus.KNOWN, LearningStatus.LEARNING])
            )
        )
        multi_token_terms = list(db.session.execute(multi_token_terms_stmt).all())

    # Combine results
    all_user_terms = single_token_terms + multi_token_terms

    # Term-first highlighting: optimized for rare multi-token terms
    highlights = _find_term_highlights_term_first(chapter.content, all_user_terms, parsed_tokens, parser, book.language)

    return ChapterWithHighlightsResponse(
        chapter=ChapterResponse.model_validate(chapter),
        term_highlights=highlights
    )


def _find_term_highlights(
    text: str,
    user_terms: list[tuple[int, str, str, int, LearningStatus, int | None]],
    parser: "AbstractParser",
    language: Language
) -> list[TermHighlight]:
    """
    Find positions of user terms in the text using optimized matching algorithm.

    Handles both single and multi-token terms, with preference for longer matches.
    Uses efficient data structures and algorithms for better performance.
    """
    if not user_terms:
        return []

    # Pre-process terms for efficient lookup
    single_token_terms: dict[str, tuple[int, str, LearningStatus, int | None]] = {}
    multi_token_terms: list[tuple[int, list[str], str, int, LearningStatus, int | None]] = []

    for term_id, norm, display, token_count, status, learning_stage in user_terms:
        if token_count == 1:
            single_token_terms[norm] = (term_id, display, status, learning_stage)
        else:
            # Pre-compute normalized tokens to avoid repeated splitting
            norm_tokens = parser.get_lowercase(norm).split()
            if len(norm_tokens) == token_count:  # Validate token count
                multi_token_terms.append((term_id, norm_tokens, display, token_count, status, learning_stage))

    # Parse text into tokens with positions - single pass
    parsed_tokens = parser.get_parsed_tokens(text, language)
    token_positions: list[tuple[str, int, int]] = []
    char_pos = 0

    for token in parsed_tokens:
        token_start = char_pos
        token_end = char_pos + len(token.token)
        if token.is_word:
            token_positions.append((token.norm, token_start, token_end))
        char_pos = token_end

    # Use efficient interval management instead of range objects
    covered_intervals: list[tuple[int, int]] = []  # Sorted list of (start, end) intervals
    highlights: list[TermHighlight] = []

    def is_covered(start: int, end: int) -> bool:
        """Check if interval overlaps with any covered interval using binary search approach."""
        for covered_start, covered_end in covered_intervals:
            if covered_start >= end:  # Since covered_intervals is sorted, no more overlaps possible
                break
            if covered_end > start:  # Overlap detected
                return True
        return False

    def add_interval(start: int, end: int) -> None:
        """Add interval to covered_intervals, maintaining sorted order."""
        # Insert in sorted position
        inserted = False
        for i, (covered_start, _) in enumerate(covered_intervals):
            if start <= covered_start:
                covered_intervals.insert(i, (start, end))
                inserted = True
                break
        if not inserted:
            covered_intervals.append((start, end))

    # Process multi-token terms first (longest first for greedy matching)
    multi_token_terms.sort(key=lambda x: x[3], reverse=True)

    for term_id, norm_tokens, display, token_count, status, learning_stage in multi_token_terms:
        # Use sliding window to find consecutive matches
        for i in range(len(token_positions) - token_count + 1):
            if all(token_positions[i + j][0] == norm_tokens[j] for j in range(token_count)):
                start_pos = token_positions[i][1]
                end_pos = token_positions[i + token_count - 1][2]

                if not is_covered(start_pos, end_pos):
                    highlights.append(TermHighlight(
                        term_id=term_id,
                        display=display,
                        start_pos=start_pos,
                        end_pos=end_pos,
                        status=status,
                        learning_stage=learning_stage
                    ))
                    add_interval(start_pos, end_pos)

    # Process single-token terms
    for norm, start_pos, end_pos in token_positions:
        if norm in single_token_terms and not is_covered(start_pos, end_pos):
            term_id, display, status, learning_stage = single_token_terms[norm]
            highlights.append(TermHighlight(
                term_id=term_id,
                display=display,
                start_pos=start_pos,
                end_pos=end_pos,
                status=status,
                learning_stage=learning_stage
            ))
            add_interval(start_pos, end_pos)

    # Sort highlights by position for consistent output
    highlights.sort(key=lambda h: h.start_pos)
    return highlights


def _find_term_highlights_term_first(
    text: str,
    user_terms: list[tuple[int, str, str, int, LearningStatus, int | None]],
    parsed_tokens: list["ParsedToken"],
    parser: "AbstractParser",
    language: Language
) -> list[TermHighlight]:
    """
    Ultra-optimized term-first highlighting for scenarios where multi-token terms are rare.

    Key optimizations:
    - Early exit if no multi-token terms
    - Hash lookup for single tokens O(1)
    - Targeted search for multi-token terms O(k*n) where k is small
    - No n-gram generation overhead
    - Greedy longest-first matching for overlaps
    """
    if not user_terms:
        return []

    # Separate single and multi-token terms for different processing strategies
    single_token_lookup: dict[str, tuple[int, str, LearningStatus, int | None]] = {}
    multi_token_terms: list[tuple[int, list[str], str, int, LearningStatus, int | None]] = []

    for term_id, norm, display, token_count, status, learning_stage in user_terms:
        if token_count == 1:
            single_token_lookup[norm] = (term_id, display, status, learning_stage)
        else:
            # Pre-validate and parse multi-token terms
            norm_tokens = parser.get_lowercase(norm).split()
            if len(norm_tokens) == token_count and token_count > 1:  # Validate token count
                multi_token_terms.append((term_id, norm_tokens, display, token_count, status, learning_stage))

    # Build token positions from pre-parsed tokens (single pass)
    token_positions: list[tuple[str, int, int]] = []
    char_pos = 0
    for token in parsed_tokens:
        token_start = char_pos
        token_end = char_pos + len(token.token)
        if token.is_word:
            token_positions.append((token.norm, token_start, token_end))
        char_pos = token_end

    if not token_positions:
        return []

    # Efficient interval management for overlap detection
    covered_intervals: list[tuple[int, int]] = []
    highlights: list[TermHighlight] = []

    def is_covered(start: int, end: int) -> bool:
        """Check if interval overlaps with covered intervals. O(k) where k is small."""
        for covered_start, covered_end in covered_intervals:
            if covered_start >= end:  # Early termination due to sorted order
                break
            if covered_end > start:  # Overlap detected
                return True
        return False

    def add_interval(start: int, end: int) -> None:
        """Add interval maintaining sorted order. O(k) insertion."""
        for i, (covered_start, _) in enumerate(covered_intervals):
            if start <= covered_start:
                covered_intervals.insert(i, (start, end))
                return
        covered_intervals.append((start, end))

    # Phase 1: Process multi-token terms first (greedy longest-first)
    # Sort by token count descending for greedy matching
    multi_token_terms.sort(key=lambda x: x[3], reverse=True)

    for term_id, norm_tokens, display, token_count, status, learning_stage in multi_token_terms:
        # Targeted sliding window search - only search for this specific term
        for i in range(len(token_positions) - token_count + 1):
            # Check if consecutive tokens match this term
            if all(token_positions[i + j][0] == norm_tokens[j] for j in range(token_count)):
                start_pos = token_positions[i][1]
                end_pos = token_positions[i + token_count - 1][2]

                # Only add if not already covered by longer term
                if not is_covered(start_pos, end_pos):
                    highlights.append(TermHighlight(
                        term_id=term_id,
                        display=display,
                        start_pos=start_pos,
                        end_pos=end_pos,
                        status=status,
                        learning_stage=learning_stage
                    ))
                    add_interval(start_pos, end_pos)

    # Phase 2: Process single tokens with O(1) hash lookup
    for norm, start_pos, end_pos in token_positions:
        if norm in single_token_lookup and not is_covered(start_pos, end_pos):
            term_id, display, status, learning_stage = single_token_lookup[norm]
            highlights.append(TermHighlight(
                term_id=term_id,
                display=display,
                start_pos=start_pos,
                end_pos=end_pos,
                status=status,
                learning_stage=learning_stage
            ))
            add_interval(start_pos, end_pos)

    # Sort by position for frontend consumption
    highlights.sort(key=lambda h: h.start_pos)
    return highlights


def _find_term_highlights_optimized(
    text: str,
    user_terms: list[tuple[int, str, str, int, LearningStatus, int | None]],
    parsed_tokens: list["ParsedToken"],
    parser: "AbstractParser",
    language: Language
) -> list[TermHighlight]:
    """
    Optimized version that reuses pre-parsed tokens to avoid re-parsing.

    This version is more efficient as it doesn't need to re-parse the chapter text.
    """
    if not user_terms:
        return []

    # Pre-process terms for efficient lookup
    single_token_terms: dict[str, tuple[int, str, LearningStatus, int | None]] = {}
    multi_token_terms: list[tuple[int, list[str], str, int, LearningStatus, int | None]] = []

    for term_id, norm, display, token_count, status, learning_stage in user_terms:
        if token_count == 1:
            single_token_terms[norm] = (term_id, display, status, learning_stage)
        else:
            # Pre-compute normalized tokens to avoid repeated splitting
            norm_tokens = parser.get_lowercase(norm).split()
            if len(norm_tokens) == token_count:  # Validate token count
                multi_token_terms.append((term_id, norm_tokens, display, token_count, status, learning_stage))

    # Build token positions from pre-parsed tokens (avoid re-parsing)
    token_positions: list[tuple[str, int, int]] = []
    char_pos = 0

    for token in parsed_tokens:
        token_start = char_pos
        token_end = char_pos + len(token.token)
        if token.is_word:
            token_positions.append((token.norm, token_start, token_end))
        char_pos = token_end

    # Use efficient interval management
    covered_intervals: list[tuple[int, int]] = []  # Sorted list of (start, end) intervals
    highlights: list[TermHighlight] = []

    def is_covered(start: int, end: int) -> bool:
        """Check if interval overlaps with any covered interval."""
        for covered_start, covered_end in covered_intervals:
            if covered_start >= end:  # Since covered_intervals is sorted, no more overlaps possible
                break
            if covered_end > start:  # Overlap detected
                return True
        return False

    def add_interval(start: int, end: int) -> None:
        """Add interval to covered_intervals, maintaining sorted order."""
        # Insert in sorted position
        inserted = False
        for i, (covered_start, _) in enumerate(covered_intervals):
            if start <= covered_start:
                covered_intervals.insert(i, (start, end))
                inserted = True
                break
        if not inserted:
            covered_intervals.append((start, end))

    # Process multi-token terms first (longest first for greedy matching)
    multi_token_terms.sort(key=lambda x: x[3], reverse=True)

    for term_id, norm_tokens, display, token_count, status, learning_stage in multi_token_terms:
        # Use sliding window to find consecutive matches
        for i in range(len(token_positions) - token_count + 1):
            if all(token_positions[i + j][0] == norm_tokens[j] for j in range(token_count)):
                start_pos = token_positions[i][1]
                end_pos = token_positions[i + token_count - 1][2]

                if not is_covered(start_pos, end_pos):
                    highlights.append(TermHighlight(
                        term_id=term_id,
                        display=display,
                        start_pos=start_pos,
                        end_pos=end_pos,
                        status=status,
                        learning_stage=learning_stage
                    ))
                    add_interval(start_pos, end_pos)

    # Process single-token terms
    for norm, start_pos, end_pos in token_positions:
        if norm in single_token_terms and not is_covered(start_pos, end_pos):
            term_id, display, status, learning_stage = single_token_terms[norm]
            highlights.append(TermHighlight(
                term_id=term_id,
                display=display,
                start_pos=start_pos,
                end_pos=end_pos,
                status=status,
                learning_stage=learning_stage
            ))
            add_interval(start_pos, end_pos)

    # Sort highlights by position for consistent output
    highlights.sort(key=lambda h: h.start_pos)
    return highlights


def _find_term_highlights_term_first(
    text: str,
    user_terms: list[tuple[int, str, str, int, LearningStatus, int | None]],
    parsed_tokens: list["ParsedToken"],
    parser: "AbstractParser",
    language: Language
) -> list[TermHighlight]:
    """
    Ultra-optimized term-first highlighting for scenarios where multi-token terms are rare.

    Key optimizations:
    - Early exit if no multi-token terms
    - Hash lookup for single tokens O(1)
    - Targeted search for multi-token terms O(k*n) where k is small
    - No n-gram generation overhead
    - Greedy longest-first matching for overlaps
    """
    if not user_terms:
        return []

    # Separate single and multi-token terms for different processing strategies
    single_token_lookup: dict[str, tuple[int, str, LearningStatus, int | None]] = {}
    multi_token_terms: list[tuple[int, list[str], str, int, LearningStatus, int | None]] = []

    for term_id, norm, display, token_count, status, learning_stage in user_terms:
        if token_count == 1:
            single_token_lookup[norm] = (term_id, display, status, learning_stage)
        else:
            # Pre-validate and parse multi-token terms
            norm_tokens = parser.get_lowercase(norm).split()
            if len(norm_tokens) == token_count and token_count > 1:  # Validate token count
                multi_token_terms.append((term_id, norm_tokens, display, token_count, status, learning_stage))

    # Build token positions from pre-parsed tokens (single pass)
    token_positions: list[tuple[str, int, int]] = []
    char_pos = 0
    for token in parsed_tokens:
        token_start = char_pos
        token_end = char_pos + len(token.token)
        if token.is_word:
            token_positions.append((token.norm, token_start, token_end))
        char_pos = token_end

    if not token_positions:
        return []

    # Efficient interval management for overlap detection
    covered_intervals: list[tuple[int, int]] = []
    highlights: list[TermHighlight] = []

    def is_covered(start: int, end: int) -> bool:
        """Check if interval overlaps with covered intervals. O(k) where k is small."""
        for covered_start, covered_end in covered_intervals:
            if covered_start >= end:  # Early termination due to sorted order
                break
            if covered_end > start:  # Overlap detected
                return True
        return False

    def add_interval(start: int, end: int) -> None:
        """Add interval maintaining sorted order. O(k) insertion."""
        for i, (covered_start, _) in enumerate(covered_intervals):
            if start <= covered_start:
                covered_intervals.insert(i, (start, end))
                return
        covered_intervals.append((start, end))

    # Phase 1: Process multi-token terms first (greedy longest-first)
    # Sort by token count descending for greedy matching
    multi_token_terms.sort(key=lambda x: x[3], reverse=True)

    for term_id, norm_tokens, display, token_count, status, learning_stage in multi_token_terms:
        # Targeted sliding window search - only search for this specific term
        for i in range(len(token_positions) - token_count + 1):
            # Check if consecutive tokens match this term
            if all(token_positions[i + j][0] == norm_tokens[j] for j in range(token_count)):
                start_pos = token_positions[i][1]
                end_pos = token_positions[i + token_count - 1][2]

                # Only add if not already covered by longer term
                if not is_covered(start_pos, end_pos):
                    highlights.append(TermHighlight(
                        term_id=term_id,
                        display=display,
                        start_pos=start_pos,
                        end_pos=end_pos,
                        status=status,
                        learning_stage=learning_stage
                    ))
                    add_interval(start_pos, end_pos)

    # Phase 2: Process single tokens with O(1) hash lookup
    for norm, start_pos, end_pos in token_positions:
        if norm in single_token_lookup and not is_covered(start_pos, end_pos):
            term_id, display, status, learning_stage = single_token_lookup[norm]
            highlights.append(TermHighlight(
                term_id=term_id,
                display=display,
                start_pos=start_pos,
                end_pos=end_pos,
                status=status,
                learning_stage=learning_stage
            ))
            add_interval(start_pos, end_pos)

    # Sort by position for frontend consumption
    highlights.sort(key=lambda h: h.start_pos)
    return highlights
