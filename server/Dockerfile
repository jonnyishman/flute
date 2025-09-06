# Backend Development Dockerfile  
FROM python:3.12-slim

# Set working directory
WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    gcc \
    && rm -rf /var/lib/apt/lists/*

# Copy project files for dependency installation
COPY pyproject.toml ./

# Install Python dependencies including dev dependencies
RUN pip install -e ".[dev]"

# Expose port for Flask dev server
EXPOSE 5000

# Set environment variables for development
ENV FLASK_ENV=development
ENV FLASK_DEBUG=1

# Start Flask development server
CMD ["python", "app.py"]