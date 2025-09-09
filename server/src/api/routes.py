"""API routes for the Flask application."""

from flask import Blueprint, jsonify

from .books import books_bp

# Create API blueprint
api_bp = Blueprint("api", __name__)

# Register sub-blueprints
api_bp.register_blueprint(books_bp, url_prefix="/books")


@api_bp.route("/health", methods=["GET"])
def health_check():
    """Health check endpoint."""
    return jsonify({"status": "healthy", "message": "API is running"})


@api_bp.errorhandler(404)
def not_found(error):
    """Handle 404 errors."""
    return jsonify({"error": "Resource not found"}), 404


@api_bp.errorhandler(400)
def bad_request(error):
    """Handle 400 errors."""
    return jsonify({"error": "Bad request"}), 400
