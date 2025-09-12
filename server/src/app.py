"""Flask application entry point."""
from __future__ import annotations

from flask import Flask
from sqlalchemy import event
from sqlalchemy.engine import Engine

from src.api.routes import api_bp
from src.config import AppConfig
from src.models import db


# Enable foreign key constraints for SQLite
@event.listens_for(Engine, "connect")
def set_sqlite_pragma(dbapi_connection, connection_record):
    """Enable foreign key constraints for SQLite."""
    if 'sqlite' in str(dbapi_connection):
        cursor = dbapi_connection.cursor()
        cursor.execute("PRAGMA journal_mode=WAL;")
        cursor.execute("PRAGMA foreign_keys=ON;")
        cursor.close()


def create_app(config: AppConfig | None = None) -> Flask:
    """Create the flask WSGI app instance. Register blueprints, extensions, and error handlers"""
    app = Flask(__name__)

    # Load configuration
    if config is None:
        config = AppConfig() # pyright: ignore[reportCallIssue]
    app.config.from_object(config)

    # Initialize extensions
    db.init_app(app)

    # Register blueprints
    app.register_blueprint(api_bp, url_prefix="/api")

    # Create database tables (for now while we're prototyping)
    with app.app_context():
        db.create_all()

    return app


if __name__ == "__main__":
    app = create_app()
    app.run(debug=True, host="0.0.0.0", port=5000)
