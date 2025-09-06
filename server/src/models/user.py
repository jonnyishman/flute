"""User model for the application."""

from .base import BaseModel, db


class User(BaseModel):
    """User model representing application users."""
    
    __tablename__ = "users"
    
    username = db.Column(db.String(80), unique=True, nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    first_name = db.Column(db.String(50), nullable=True)
    last_name = db.Column(db.String(50), nullable=True)
    is_active = db.Column(db.Boolean, default=True, nullable=False)
    
    def __repr__(self) -> str:
        """String representation of the user."""
        return f"<User {self.username}>"
    
    @property
    def full_name(self) -> str:
        """Get the user's full name."""
        if self.first_name and self.last_name:
            return f"{self.first_name} {self.last_name}"
        return self.username