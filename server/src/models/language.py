"""Language and dictionary models"""
from __future__ import annotations

from sqlalchemy import Boolean, ForeignKey, Integer, SmallInteger, String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from src.models.base import AuditMixin, db


class Language(db.Model, AuditMixin):
    __tablename__ = "languages"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    name: Mapped[str] = mapped_column(String(40), nullable=False)

    character_substitutions: Mapped[str] = mapped_column(
        String(500), nullable=False, default="´='|`='|'='|'='|...=…|..=‥"
    )
    regexp_split_sentences: Mapped[str] = mapped_column(
        String(500), nullable=False, default=".!?"
    )
    exceptions_split_sentences: Mapped[str] = mapped_column(
        String(500), nullable=False, default="Mr.|Mrs.|Dr.|[A-Z].|Vd.|Vds."
    )
    word_characters: Mapped[str] = mapped_column(
        String(500), nullable=False, default="a-zA-ZÀ-ÖØ-öø-ȳáéíóúÁÉÍÓÚñÑ"
    )
    right_to_left: Mapped[bool] = mapped_column(Boolean, nullable=False, default=False)
    show_romanization: Mapped[bool] = mapped_column(Boolean, nullable=False, default=False)
    parser_type: Mapped[str] = mapped_column(String(20), nullable=False, default="spacedel")

    # relationship
    dictionaries: Mapped[list[LanguageDictionary]] = relationship(
        back_populates="language",
        order_by="LanguageDictionary.sort_order",
        lazy="subquery",
        cascade="all, delete-orphan",
    )

    def __repr__(self) -> str:
        return f"<Language {self.id} '{self.name}'>"


class LanguageDictionary(db.Model):
    __tablename__ = "language_dicts"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)

    language_id: Mapped[int] = mapped_column(Integer, ForeignKey(Language.id), nullable=False)
    use_for: Mapped[str] = mapped_column(String(20), nullable=False)
    dict_type: Mapped[str] = mapped_column(String(20), nullable=False)
    dict_uri: Mapped[str] = mapped_column(String(200), nullable=False)
    is_active: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)
    sort_order: Mapped[int] = mapped_column(SmallInteger, nullable=False)

    # relationships
    language: Mapped[Language] = relationship(back_populates="dictionaries")
