"""Tests for base models and mixins."""
from __future__ import annotations

import datetime as dt
from typing import TYPE_CHECKING

from src.models import db
from src.models.language import Language

if TYPE_CHECKING:
    from flask import Flask


class TestAuditMixin:
    """Test cases for AuditMixin."""

    def test_audit_mixin_timestamps_on_create(self, app: Flask):
        """Test that created_at and updated_at are set on creation."""
        # Given
        language = Language(name="Test Language")

        # When
        db.session.add(language)
        db.session.commit()

        # Then
        assert language.created_at is not None
        assert language.updated_at is not None
        assert isinstance(language.created_at, dt.datetime)
        assert isinstance(language.updated_at, dt.datetime)
        # Timestamps should be very close (within 1 second)
        assert abs((language.updated_at - language.created_at).total_seconds()) < 1.0

    def test_audit_mixin_created_at_unchanged_on_update(self, app: Flask):
        """Test that created_at remains unchanged on updates."""
        # Given
        language = Language(name="Test Language")
        db.session.add(language)
        db.session.commit()

        original_created_at = language.created_at

        # When
        language.name = "Modified Name"
        db.session.commit()

        # Then
        assert language.created_at == original_created_at
