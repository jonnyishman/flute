"""Flask application entry point."""

from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_pydantic import validate

from src.api.routes import api_bp
from src.models import db


def create_app(config_name: str = "development") -> Flask:
    """Create and configure the Flask application.
    
    Args:
        config_name: Configuration environment name
        
    Returns:
        Configured Flask application instance
    """
    app = Flask(__name__)
    
    # Load configuration
    if config_name == "development":
        app.config.from_object("src.config.DevelopmentConfig")
    elif config_name == "testing":
        app.config.from_object("src.config.TestingConfig")
    else:
        app.config.from_object("src.config.ProductionConfig")
    
    # Initialize extensions
    db.init_app(app)
    
    # Register blueprints
    app.register_blueprint(api_bp, url_prefix="/api")
    
    # Create database tables
    with app.app_context():
        db.create_all()
    
    return app


if __name__ == "__main__":
    app = create_app()
    app.run(debug=True, host="0.0.0.0", port=5000)