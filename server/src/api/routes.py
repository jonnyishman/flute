"""API routes for the Flask application."""
from __future__ import annotations

from flask import Blueprint, jsonify
from werkzeug.exceptions import HTTPException

# Create API blueprint
api_bp = Blueprint("api", __name__)


@api_bp.route("/health", methods=["GET"])
def health_check():
    """Health check endpoint."""
    return jsonify({"status": "healthy", "message": "API is running"})


@api_bp.errorhandler(HTTPException)
def client_error(error: HTTPException):
    """Handle werkzeug errors"""
    return jsonify({"error": error.name, "msg": error.description}), error.code


@api_bp.errorhandler(Exception)
def server_error(error: Exception):
    """Handle uncaught exceptions"""
    return jsonify({"error": "Internal Server Error", "msg": str(error)}), 500

