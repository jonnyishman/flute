"""SQLAlchemy database instance and base model."""
from __future__ import annotations

from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.orm import DeclarativeBase


class Base(DeclarativeBase):
    """Base model class with common fields."""

    pass


# Create database instance
db = SQLAlchemy(model_class=Base)
