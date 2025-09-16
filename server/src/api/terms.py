"""API routes for term-related operations"""

import sqlalchemy as sa
from flask import abort
from flask_pydantic import validate
from pydantic import BaseModel, Field
from sqlalchemy.dialects.sqlite import insert

from src.api.routes import api_bp
from src.models import (
    Language,
    LearningStatus,
    Term,
    TermProgress,
    db,
)
from src.parse.registry import get_parser


class UpdateTerm(BaseModel):
    """Request model for updating a term"""

    status: LearningStatus
    learning_stage: int = Field(default=1, ge=1, le=5)
    display: str | None = None
    translation: str | None = None


class CreateTerm(UpdateTerm):
    term: str
    language_id: int


class TermId(BaseModel):
    term_id: int


@api_bp.route("/terms", methods=["POST"])
@validate()
def create_term(body: CreateTerm) -> TermId:
    if not (language := db.session.get(Language, body.language_id)):
        abort(404, description=f"invalid language_id: '{body.language_id}'")

    parser = get_parser(language.parser_type)
    norm = parser.get_lowercase(body.term)
    if body.display is not None and parser.get_lowercase(body.display) != norm:
        abort(400, description="display must match the term's normalized form")

    stmt = insert(Term).values({
        "language_id": body.language_id,
        "norm": norm,
        "token_count": parser.get_token_count(norm, language),
        "display": body.display if body.display is not None else body.term,
    })

    if body.display is not None:
        stmt = stmt.on_conflict_do_update(
            index_elements=["language_id", "norm"], set_={"display": body.display}
        ).returning(Term.id)
        term_id = db.session.execute(stmt).scalar_one()
    else:
        # Allow for edge cases where term does actually already exist
        stmt = stmt.on_conflict_do_nothing(index_elements=["language_id", "norm"]).returning(Term.id)
        if (term_id := db.session.execute(stmt).scalar_one_or_none()) is None:
            # RETURNING doesn't return anything if no actual insertion, so extra fetch required
            term_id = db.session.execute(
                sa.select(Term.id).where(Term.language_id == body.language_id, Term.norm == norm)
            ).scalar_one()

    upsert_term_progress(term_id, body)
    db.session.commit()
    return TermId(term_id=term_id)


@api_bp.route("/terms/<int:term_id>", methods=["PATCH"])
@validate()
def update_term(term_id: int, body: UpdateTerm) -> tuple[str, int]:
    """
    Update a term's details.
    """
    if not (term := db.session.get(Term, term_id)):
        abort(404, description=f"invalid term_id: '{term_id}'")

    # Display changes only allowed if the normalised form is unchanged
    if body.display is not None:
        parser = get_parser(term.language.parser_type)
        if parser.get_lowercase(body.display) != term.norm:
            abort(400, description="display must match the term's normalized form")
        term.display = body.display

    upsert_term_progress(term.id, body)
    db.session.commit()
    return "", 204


def upsert_term_progress(term_id: int, request: UpdateTerm) -> None:
    params: dict[str, str | int] = {
        "term_id": term_id,
        "status": request.status,
        "learning_stage": request.learning_stage,
    }
    if request.translation is not None:
        params["translation"] = request.translation

    db.session.execute(
        insert(TermProgress)
        .values(params)
        .on_conflict_do_update(index_elements=[TermProgress.term_id], set_=params)
    )
