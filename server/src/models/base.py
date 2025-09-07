"""SQLAlchemy database instance and base model."""

from datetime import datetime
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
    created_at = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)
    updated_at = db.Column(
        db.DateTime,
        default=datetime.utcnow,
        onupdate=datetime.utcnow,
        nullable=False
    )

    def to_dict(self) -> dict:
        """Convert model instance to dictionary.

        Returns:
            Dictionary representation of the model
        """
        return {
            column.name: getattr(self, column.name)
            for column in self.__table__.columns
        }

    def save(self) -> None:
        """Save the model instance to the database."""
        db.session.add(self)
        db.session.commit()

    def delete(self) -> None:
        """Delete the model instance from the database."""
        db.session.delete(self)
        db.session.commit()
