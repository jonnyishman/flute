"""SQLAlchemy database instance and base model."""
from __future__ import annotations

import datetime as dt

from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import DateTime, func
from sqlalchemy.orm import DeclarativeBase, Mapped, declarative_mixin, mapped_column


class Base(DeclarativeBase):
    """Base model class with common fields."""

    pass


# Create database instance
db = SQLAlchemy(model_class=Base)


@declarative_mixin
class AuditMixin:
    created_at: Mapped[dt.datetime] = mapped_column(
        DateTime,
        server_default=func.current_timestamp(),
        nullable=False
    )
    updated_at: Mapped[dt.datetime] = mapped_column(
        DateTime,
        server_default=func.current_timestamp(),
        onupdate=func.current_timestamp(),
        nullable=False
    )
