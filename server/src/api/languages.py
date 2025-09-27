"""API routes for language-related operations"""

import sqlalchemy as sa
from flask import abort
from flask_pydantic import validate
from pydantic import BaseModel, ConfigDict, Field

from src.api.routes import api_bp
from src.models import Book, Language, db


class LanguageSummary(BaseModel):
    """Summary model for language listing."""
    model_config = ConfigDict(from_attributes=True)

    id: int
    name: str
    flag_image_filepath: str | None


class LanguageDetail(BaseModel):
    """Detailed model for a single language."""
    model_config = ConfigDict(from_attributes=True)

    id: int
    name: str
    flag_image_filepath: str | None
    character_substitutions: str
    regexp_split_sentences: str
    exceptions_split_sentences: str
    word_characters: str
    right_to_left: bool
    show_romanization: bool
    parser_type: str


class LanguageCreate(BaseModel):
    """Request model for creating a new language."""

    name: str = Field(max_length=40)
    flag_image_filepath: str | None = Field(default=None, max_length=500)
    character_substitutions: str = Field(default="´='|`='|'='|'='|...=…|..=‥", max_length=500)
    regexp_split_sentences: str = Field(default=".!?", max_length=500)
    exceptions_split_sentences: str = Field(default="Mr.|Mrs.|Dr.|[A-Z].|Vd.|Vds.", max_length=500)
    word_characters: str = Field(default="a-zA-ZÀ-ÖØ-öø-ȳáéíóúÁÉÍÓÚñÑ", max_length=500)
    right_to_left: bool = Field(default=False)
    show_romanization: bool = Field(default=False)
    parser_type: str = Field(default="spacedel", max_length=20)


class LanguageUpdate(BaseModel):
    """Request model for updating an existing language."""

    name: str | None = Field(None, max_length=40)
    flag_image_filepath: str | None = Field(None, max_length=500)
    character_substitutions: str | None = Field(None, max_length=500)
    regexp_split_sentences: str | None = Field(None, max_length=500)
    exceptions_split_sentences: str | None = Field(None, max_length=500)
    word_characters: str | None = Field(None, max_length=500)
    right_to_left: bool | None = None
    show_romanization: bool | None = None
    parser_type: str | None = Field(None, max_length=20)


class LanguageCreateResponse(BaseModel):
    """Response model for language creation."""

    language_id: int


class LanguageSummariesRequest(BaseModel):
    """Request model for language summaries."""

    with_books: bool = False


class LanguageSummariesResponse(BaseModel):
    """Response model for language summaries."""

    languages: list[LanguageSummary]


@api_bp.route("/languages", methods=["GET"])
@validate()
def get_language_summaries(query: LanguageSummariesRequest) -> LanguageSummariesResponse:
    """
    Retrieve summary of all languages.

    Returns basic language information (ID, name, and flag image filepath).
    Query parameter 'with_books=true' filters to languages with at least one book.
    """
    stmt = sa.select(Language.id, Language.name, Language.flag_image_filepath)

    if query.with_books:
        stmt = stmt.where(
            sa.exists().where(Book.language_id == Language.id)
        )

    stmt = stmt.order_by(Language.name)
    rows = db.session.execute(stmt).all()
    return LanguageSummariesResponse(
        languages=[LanguageSummary.model_validate(row) for row in rows]
    )


@api_bp.route("/languages/<int:language_id>", methods=["GET"])
@validate()
def get_language_detail(language_id: int) -> LanguageDetail:
    """
    Retrieve full details for a single language.

    Returns all language fields including parsing configuration.
    """
    if not (language := db.session.get(Language, language_id)):
        abort(404, description=f"Language with id '{language_id}' not found")

    return LanguageDetail.model_validate(language)


@api_bp.route("/languages/<int:language_id>", methods=["PATCH"])
@validate()
def update_language(language_id: int, body: LanguageUpdate) -> tuple[str, int]:
    """
    Update details for an existing language.

    Updates only the fields provided in the request body.
    """
    if not (language := db.session.get(Language, language_id)):
        abort(404, description=f"Language with id '{language_id}' not found")

    # Update only the fields that were provided
    update_data = body.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        setattr(language, field, value)

    db.session.commit()
    return "", 204


@api_bp.route("/languages", methods=["POST"])
@validate()
def create_language(body: LanguageCreate) -> tuple[LanguageCreateResponse, int]:
    """
    Create a new language.

    Creates a language with the provided configuration.
    """
    language = Language(**body.model_dump())
    db.session.add(language)
    db.session.commit()

    return LanguageCreateResponse(language_id=language.id), 201
