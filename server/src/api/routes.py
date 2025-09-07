"""API routes for the Flask application."""

from flask import Blueprint, jsonify
from flask_pydantic import validate
from sqlalchemy.exc import IntegrityError

from ..models import db, Book, Chapter
from ..models.user import User
from ..schemas import (
    UserCreate, UserUpdate, UserResponse,
    BookCreate, BookResponse, BookWithChaptersResponse,
    ChapterCreate, ChapterResponse
)

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


# Book API endpoints
@api_bp.route("/books", methods=["GET"])
def get_books():
    """Get all books."""
    books = Book.query.all()
    return jsonify([
        BookResponse.model_validate(book).model_dump()
        for book in books
    ])


@api_bp.route("/books/<int:book_id>", methods=["GET"])
def get_book(book_id: int):
    """Get a specific book by ID with all its chapters."""
    book = Book.query.get_or_404(book_id)
    return jsonify(BookWithChaptersResponse.model_validate(book).model_dump())


@api_bp.route("/books", methods=["POST"])
@validate()
def create_book(body: BookCreate):
    """Create a new book."""
    try:
        book = Book(
            title=body.title,
            author=body.author,
            description=body.description,
            cover_image_url=body.cover_image_url
        )
        book.save()
        return jsonify(BookResponse.model_validate(book).model_dump()), 201
    except IntegrityError:
        db.session.rollback()
        return jsonify({"error": "Failed to create book"}), 400


@api_bp.route("/books/<int:book_id>/chapters", methods=["POST"])
@validate()
def create_chapter(book_id: int, body: ChapterCreate):
    """Create a new chapter for a book."""
    book = Book.query.get_or_404(book_id)

    # Check if chapter number already exists for this book
    existing_chapter = Chapter.query.filter_by(
        book_id=book_id, chapter_number=body.chapter_number
    ).first()

    if existing_chapter:
        return jsonify({"error": "Chapter number already exists for this book"}), 400

    try:
        # Calculate word count
        word_count = len(body.content.split())

        chapter = Chapter(
            book_id=book_id,
            chapter_number=body.chapter_number,
            title=body.title,
            content=body.content,
            word_count=word_count
        )
        chapter.save()

        # Update book's total chapters
        book.total_chapters = Chapter.query.filter_by(book_id=book_id).count()
        book.save()

        return jsonify(ChapterResponse.model_validate(chapter).model_dump()), 201
    except IntegrityError:
        db.session.rollback()
        return jsonify({"error": "Failed to create chapter"}), 400


@api_bp.route("/books/<int:book_id>/chapters/<int:chapter_number>", methods=["GET"])
def get_chapter(book_id: int, chapter_number: int):
    """Get a specific chapter by book ID and chapter number."""
    chapter = Chapter.query.filter_by(
        book_id=book_id, chapter_number=chapter_number
    ).first_or_404()

    return jsonify(ChapterResponse.model_validate(chapter).model_dump())


@api_bp.errorhandler(400)
def bad_request(error):
    """Handle 400 errors."""
    return jsonify({"error": "Bad request"}), 400
