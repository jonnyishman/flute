"""API routes for image storage and retrieval operations."""
import contextlib
import uuid
from pathlib import Path

from flask import current_app, request, send_file
from flask_pydantic import validate
from pydantic import BaseModel
from werkzeug.datastructures import FileStorage
from werkzeug.exceptions import BadRequest, NotFound, UnsupportedMediaType

from src.api.routes import api_bp
from src.models import Image, db


class ImageUploadResponse(BaseModel):
    """Response model for image upload."""

    image_id: str
    original_filename: str
    content_type: str
    file_size: int


class ImageMetadataResponse(BaseModel):
    """Response model for image metadata."""

    image_id: str
    original_filename: str
    content_type: str
    file_size: int
    created_at: str
    updated_at: str


# Allowed image file types for security
ALLOWED_EXTENSIONS = {".jpg", ".jpeg", ".png", ".gif", ".webp", ".bmp", ".svg"}
ALLOWED_CONTENT_TYPES = {
    "image/jpeg",
    "image/png",
    "image/gif",
    "image/webp",
    "image/bmp",
    "image/svg+xml"
}

# Maximum file size: 10MB
MAX_FILE_SIZE = 10 * 1024 * 1024


def _validate_image_file(file: FileStorage) -> None:
    """Validate uploaded image file for security and constraints."""
    if not file or not file.filename:
        raise BadRequest("No file provided")

    # Check file extension
    file_ext = Path(file.filename).suffix.lower()
    if file_ext not in ALLOWED_EXTENSIONS:
        raise UnsupportedMediaType(f"File type '{file_ext}' not allowed. Allowed types: {', '.join(ALLOWED_EXTENSIONS)}")

    # Check content type
    if file.content_type not in ALLOWED_CONTENT_TYPES:
        raise UnsupportedMediaType(f"Content type '{file.content_type}' not allowed")

    # Check file size by seeking to end
    file.seek(0, 2)  # Seek to end
    file_size = file.tell()
    file.seek(0)  # Reset to beginning

    if file_size > MAX_FILE_SIZE:
        raise BadRequest(f"File size ({file_size} bytes) exceeds maximum allowed size ({MAX_FILE_SIZE} bytes)")

    if file_size == 0:
        raise BadRequest("File is empty")


def _get_storage_path() -> Path:
    """Get the configured image storage directory path."""
    storage_path = Path(current_app.config["IMAGE_STORAGE_PATH"])

    # Make path absolute if it's relative
    if not storage_path.is_absolute():
        storage_path = Path.cwd() / storage_path

    # Ensure the directory exists
    storage_path.mkdir(parents=True, exist_ok=True)

    return storage_path


def _save_image_file(file: FileStorage, image_id: str) -> Path:
    """Save uploaded file to storage directory with UUID filename."""
    storage_path = _get_storage_path()

    # Use UUID as filename with original extension for uniqueness
    file_ext = Path(file.filename).suffix.lower()
    filename = f"{image_id}{file_ext}"
    file_path = storage_path / filename

    # Save the file
    file.save(str(file_path))

    return file_path


@api_bp.route("/images", methods=["POST"])
def upload_image() -> tuple[ImageUploadResponse, int]:
    """
    Upload an image file for storage.

    Accepts multipart form data with an 'image' file field.
    Returns metadata about the stored image including a unique image_id for retrieval.
    """
    # Get uploaded file from form data
    if "image" not in request.files:
        raise BadRequest("No 'image' field in request")

    file = request.files["image"]

    # Validate the uploaded file
    _validate_image_file(file)

    # Generate unique ID for this image
    image_id = str(uuid.uuid4())

    # Save file to storage
    try:
        file_path = _save_image_file(file, image_id)
    except Exception as exc:
        raise BadRequest(f"Failed to save image file: {exc}") from exc

    # Get actual file size after saving
    file_size = file_path.stat().st_size

    # Create database record
    image = Image(
        id=image_id,
        original_filename=file.filename,
        content_type=file.content_type,
        file_size=file_size,
        file_path=str(file_path)
    )

    try:
        db.session.add(image)
        db.session.commit()
    except Exception as exc:
        # Clean up file if database save fails
        with contextlib.suppress(FileNotFoundError):
            file_path.unlink()
        raise BadRequest(f"Failed to save image metadata: {exc}") from exc

    response = ImageUploadResponse(
        image_id=image_id,
        original_filename=file.filename,
        content_type=file.content_type,
        file_size=file_size
    )
    return response.model_dump(), 201


@api_bp.route("/images/<string:image_id>", methods=["GET"])
def get_image(image_id: str):
    """
    Retrieve an image file by its ID.

    Returns the raw image file with appropriate content type headers.
    """
    # Get image metadata from database
    image = db.session.get(Image, image_id)
    if not image:
        raise NotFound(f"Image with ID '{image_id}' not found")

    # Check if file exists on disk
    file_path = Path(image.file_path)
    if not file_path.exists():
        raise NotFound(f"Image file not found on disk: {file_path}")

    # Return the file with proper content type
    return send_file(
        str(file_path),
        mimetype=image.content_type,
        as_attachment=False,
        download_name=image.original_filename
    )


@api_bp.route("/images/<string:image_id>/metadata", methods=["GET"])
@validate()
def get_image_metadata(image_id: str) -> ImageMetadataResponse:
    """
    Get metadata for an image without downloading the file.

    Returns information about the image including size, type, and timestamps.
    """
    # Get image metadata from database
    image = db.session.get(Image, image_id)
    if not image:
        raise NotFound(f"Image with ID '{image_id}' not found")

    response = ImageMetadataResponse(
        image_id=image.id,
        original_filename=image.original_filename,
        content_type=image.content_type,
        file_size=image.file_size,
        created_at=image.created_at.isoformat(),
        updated_at=image.updated_at.isoformat()
    )
    return response.model_dump()


@api_bp.route("/images/<string:image_id>", methods=["DELETE"])
def delete_image(image_id: str) -> tuple[dict[str, str], int]:
    """
    Delete an image and its associated file.

    Removes both the database record and the file from storage.
    """
    # Get image metadata from database
    image = db.session.get(Image, image_id)
    if not image:
        raise NotFound(f"Image with ID '{image_id}' not found")

    # Delete file from storage if it exists
    file_path = Path(image.file_path)
    try:
        if file_path.exists():
            file_path.unlink()
    except Exception as exc:
        # Log warning but continue with database deletion
        current_app.logger.warning(f"Failed to delete image file {file_path}: {exc}")

    # Delete database record
    try:
        db.session.delete(image)
        db.session.commit()
    except Exception as exc:
        raise BadRequest(f"Failed to delete image metadata: {exc}") from exc

    return {"message": f"Image '{image_id}' deleted successfully"}, 200
