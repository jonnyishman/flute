# Flute Server

A Flask-based API server for the Flute application, built with Flask-SQLAlchemy and Flask-Pydantic.

## Project Structure

```
server/
├── src/
│   ├── api/          # API routes and endpoints
│   ├── models/       # SQLAlchemy database models
│   ├── config.py     # Application configuration
│   └── schemas.py    # Pydantic schemas for validation
├── test/             # Test files
├── app.py           # Application entry point
├── requirements.txt # Python dependencies
└── pyproject.toml   # Project configuration
```

## Setup

1. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```

2. Run the application:
   ```bash
   python app.py
   ```

The server will start on `http://localhost:5000`.

## API Endpoints

- `GET /api/health` - Health check
- `GET /api/users` - Get all users
- `GET /api/users/<id>` - Get user by ID
- `POST /api/users` - Create new user
- `PUT /api/users/<id>` - Update user
- `DELETE /api/users/<id>` - Delete user

## Development

### Running Tests

```bash
pytest
```

### Linting and Type Checking

```bash
ruff check .
ruff format .
mypy src/
```

## Configuration

The application uses SQLite by default. Environment variables can be set to override defaults:

- `SECRET_KEY`: Flask secret key
- `DATABASE_URL`: Database connection string