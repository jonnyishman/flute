"""SQLAlchemy database instance and base model."""
from __future__ import annotations

import datetime as dt

from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.orm import DeclarativeBase


class Base(DeclarativeBase):
    """Base model class with common fields."""

    pass


# Create database instance
db = SQLAlchemy(model_class=Base)


class BaseModel(db.Model):
    """Base model with common fields and methods."""

    __abstract__ = True

    id = db.Column(db.Integer, primary_key=True)
    created_at = db.Column(db.DateTime, default=dt.datetime.now(dt.UTC), nullable=False)
    updated_at = db.Column(
        db.DateTime,
        default=dt.datetime.now(dt.UTC),
        onupdate=dt.datetime.now(dt.UTC),
        nullable=False
    )
