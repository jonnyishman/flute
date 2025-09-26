"""Image models for file storage and metadata."""
from __future__ import annotations

import uuid

from sqlalchemy import Integer, String
from sqlalchemy.orm import Mapped, mapped_column

from src.models.base import AuditMixin, db


class Image(AuditMixin, db.Model):
    """Model for storing image metadata and file references."""

    __tablename__ = "images"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    original_filename: Mapped[str] = mapped_column(String(255), nullable=False)
    content_type: Mapped[str] = mapped_column(String(100), nullable=False)
    file_size: Mapped[int] = mapped_column(Integer, nullable=False)
    file_path: Mapped[str] = mapped_column(String(500), nullable=False)

    def __repr__(self) -> str:
        """String representation of Image."""
        return f"<Image {self.id}: {self.original_filename}>"
