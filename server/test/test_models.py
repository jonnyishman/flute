"""Tests for database models."""

from src.models.user import User


class TestUserModel:
    """Test cases for User model."""
    
    def test_create_user(self, app):
        """Test creating a user instance."""
        with app.app_context():
            user = User(
                username="testuser",
                email="test@example.com",
                first_name="Test",
                last_name="User"
            )
            user.save()
            
            assert user.id is not None
            assert user.username == "testuser"
            assert user.email == "test@example.com"
            assert user.is_active is True
    
    def test_user_full_name(self, app):
        """Test user full_name property."""
        with app.app_context():
            user = User(
                username="testuser",
                email="test@example.com",
                first_name="Test",
                last_name="User"
            )
            user.save()
            
            assert user.full_name == "Test User"
    
    def test_user_full_name_no_names(self, app):
        """Test user full_name property when no first/last names."""
        with app.app_context():
            user = User(
                username="testuser",
                email="test@example.com"
            )
            user.save()
            
            assert user.full_name == "testuser"
    
    def test_user_repr(self, app):
        """Test user string representation."""
        with app.app_context():
            user = User(
                username="testuser",
                email="test@example.com"
            )
            user.save()
            
            assert str(user) == "<User testuser>"
    
    def test_user_to_dict(self, app):
        """Test converting user to dictionary."""
        with app.app_context():
            user = User(
                username="testuser",
                email="test@example.com",
                first_name="Test",
                last_name="User"
            )
            user.save()
            
            user_dict = user.to_dict()
            assert user_dict["username"] == "testuser"
            assert user_dict["email"] == "test@example.com"
            assert user_dict["first_name"] == "Test"
            assert user_dict["last_name"] == "User"
            assert user_dict["is_active"] is True
            assert "id" in user_dict
            assert "created_at" in user_dict
            assert "updated_at" in user_dict