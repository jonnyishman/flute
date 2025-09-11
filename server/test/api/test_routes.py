"""Tests for API endpoints"""
from __future__ import annotations

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from flask.testing import FlaskClient


class TestHealthEndpoint:
    """Test cases for health check endpoint."""

    def test_health_check(self, client: FlaskClient) -> None:
        """Test health check endpoint returns successful response."""
        response = client.get("/api/health")
        assert response.status_code == 200

        data = response.get_json()
        assert data["status"] == "healthy"
        assert "message" in data
