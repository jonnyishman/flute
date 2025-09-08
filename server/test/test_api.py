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


class TestUserEndpoints:
    """Test cases for user endpoints."""

    def test_get_empty_users(self, client):
        """Test getting users when none exist."""
        response = client.get("/api/users")
        assert response.status_code == 200

        data = json.loads(response.data)
        assert data == []

    def test_create_user(self, client):
        """Test creating a new user."""
        user_data = {
            "username": "testuser",
            "email": "test@example.com",
            "first_name": "Test",
            "last_name": "User"
        }

        response = client.post(
            "/api/users",
            data=json.dumps(user_data),
            content_type="application/json"
        )

        assert response.status_code == 201
        data = json.loads(response.data)
        assert data["username"] == user_data["username"]
        assert data["email"] == user_data["email"]
        assert data["id"] is not None

    def test_get_user_by_id(self, client):
        """Test getting a user by ID."""
        # First create a user
        user_data = {
            "username": "testuser",
            "email": "test@example.com"
        }

        create_response = client.post(
            "/api/users",
            data=json.dumps(user_data),
            content_type="application/json"
        )

        created_user = json.loads(create_response.data)
        user_id = created_user["id"]

        # Then get the user
        response = client.get(f"/api/users/{user_id}")
        assert response.status_code == 200

        data = json.loads(response.data)
        assert data["id"] == user_id
        assert data["username"] == user_data["username"]

    def test_get_nonexistent_user(self, client):
        """Test getting a user that doesn't exist."""
        response = client.get("/api/users/999")
        assert response.status_code == 404

        data = json.loads(response.data)
        assert "error" in data

    def test_create_user_missing_email(self, client):
        """Test creating a user without required email field."""
        user_data = {
            "username": "testuser"
        }

        response = client.post(
            "/api/users",
            data=json.dumps(user_data),
            content_type="application/json"
        )

        assert response.status_code == 400
