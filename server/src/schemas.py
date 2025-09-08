"""Pydantic schemas for request/response validation."""


from pydantic import BaseModel, EmailStr, Field


class UserCreate(BaseModel):
    """Schema for creating a new user."""

    username: str = Field(..., min_length=3, max_length=80)
    email: EmailStr
    first_name: str | None = Field(None, max_length=50)
    last_name: str | None = Field(None, max_length=50)


class UserUpdate(BaseModel):
    """Schema for updating an existing user."""

    username: str | None = Field(None, min_length=3, max_length=80)
    email: EmailStr | None = None
    first_name: str | None = Field(None, max_length=50)
    last_name: str | None = Field(None, max_length=50)
    is_active: bool | None = None


class UserResponse(BaseModel):
    """Schema for user response data."""

    id: int
    username: str
    email: str
    first_name: str | None = None
    last_name: str | None = None
    is_active: bool
    full_name: str

    class Config:
        """Pydantic configuration."""
        from_attributes = True
