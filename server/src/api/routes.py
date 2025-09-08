"""API routes for the Flask application."""

from flask import Blueprint, jsonify
from flask_pydantic import validate
from sqlalchemy.exc import IntegrityError

from ..models import db
from ..models.user import User
from ..schemas import UserCreate, UserResponse, UserUpdate

# Create API blueprint
api_bp = Blueprint("api", __name__)


@api_bp.route("/health", methods=["GET"])
def health_check():
    """Health check endpoint."""
    return jsonify({"status": "healthy", "message": "API is running"})


@api_bp.route("/users", methods=["GET"])
def get_users():
    """Get all users."""
    users = User.query.all()
    return jsonify([
        UserResponse.model_validate(user).model_dump()
        for user in users
    ])


@api_bp.route("/users/<int:user_id>", methods=["GET"])
def get_user(user_id: int):
    """Get a specific user by ID."""
    user = User.query.get_or_404(user_id)
    return jsonify(UserResponse.model_validate(user).model_dump())


@api_bp.route("/users", methods=["POST"])
@validate()
def create_user(body: UserCreate):
    """Create a new user."""
    try:
        user = User(
            username=body.username,
            email=body.email,
            first_name=body.first_name,
            last_name=body.last_name
        )
        user.save()
        return jsonify(UserResponse.model_validate(user).model_dump()), 201
    except IntegrityError:
        db.session.rollback()
        return jsonify({"error": "User with this username or email already exists"}), 400


@api_bp.route("/users/<int:user_id>", methods=["PUT"])
@validate()
def update_user(user_id: int, body: UserUpdate):
    """Update an existing user."""
    user = User.query.get_or_404(user_id)

    # Update only provided fields
    for field, value in body.model_dump(exclude_unset=True).items():
        setattr(user, field, value)

    try:
        user.save()
        return jsonify(UserResponse.model_validate(user).model_dump())
    except IntegrityError:
        db.session.rollback()
        return jsonify({"error": "Username or email already exists"}), 400


@api_bp.route("/users/<int:user_id>", methods=["DELETE"])
def delete_user(user_id: int):
    """Delete a user."""
    user = User.query.get_or_404(user_id)
    user.delete()
    return "", 204


@api_bp.errorhandler(404)
def not_found(error):
    """Handle 404 errors."""
    return jsonify({"error": "Resource not found"}), 404


@api_bp.errorhandler(400)
def bad_request(error):
    """Handle 400 errors."""
    return jsonify({"error": "Bad request"}), 400
