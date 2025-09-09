"""Tests for API endpoints."""

import json


class TestHealthEndpoint:
    """Test cases for health check endpoint."""

    def test_health_check(self, client):
        """Test health check endpoint returns successful response."""
        response = client.get("/api/health")
        assert response.status_code == 200

        data = json.loads(response.data)
        assert data["status"] == "healthy"
        assert "message" in data
