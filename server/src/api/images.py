"""API routes for image storage and retrieval operations."""
import uuid
from pathlib import Path

from flask import current_app, request, send_file
from pydantic import BaseModel
from werkzeug.datastructures import FileStorage
from werkzeug.exceptions import BadRequest, NotFound, UnsupportedMediaType

from src.api.routes import api_bp


class ImageUploadResponse(BaseModel):
    """Response model for image upload."""

    file_path: str
    original_filename: str
    content_type: str
    file_size: int


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


def _save_image_file(file: FileStorage, image_id: str) -> tuple[Path, str]:
    """Save uploaded file to storage directory with UUID filename."""
    storage_path = _get_storage_path()

    # Use UUID as filename with original extension for uniqueness
    file_ext = Path(file.filename).suffix.lower()
    filename = f"{image_id}{file_ext}"
    file_path = storage_path / filename

    # Save the file
    file.save(str(file_path))

    # Return both absolute path and relative path (just the filename for the API)
    return file_path, filename


@api_bp.route("/images", methods=["POST"])
def upload_image() -> tuple[ImageUploadResponse, int]:
    """
    Upload an image file for storage.

    Accepts multipart form data with an 'image' file field.
    Returns the relative file path where the image was stored.
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
        file_path, relative_path = _save_image_file(file, image_id)
    except Exception as exc:
        raise BadRequest(f"Failed to save image file: {exc}") from exc

    # Get actual file size after saving
    file_size = file_path.stat().st_size

    response = ImageUploadResponse(
        file_path=relative_path,
        original_filename=file.filename,
        content_type=file.content_type,
        file_size=file_size
    )
    return response.model_dump(), 201


@api_bp.route("/images/<path:relative_path>", methods=["GET"])
def get_image(relative_path: str):
    """
    Retrieve an image file by its relative path.

    Returns the raw image file with appropriate content type headers.
    """
    storage_path = _get_storage_path()

    # Remove the storage path prefix if it exists in the relative path
    storage_dir_name = Path(current_app.config["IMAGE_STORAGE_PATH"]).name
    if relative_path.startswith(storage_dir_name + "/"):
        relative_path = relative_path[len(storage_dir_name) + 1:]

    # Construct full file path
    file_path = storage_path / relative_path

    # Security: ensure the path is within storage directory
    try:
        file_path = file_path.resolve()
        storage_path = storage_path.resolve()
        file_path.relative_to(storage_path)
    except ValueError:
        raise NotFound("Invalid file path") from None

    # Check if file exists on disk
    if not file_path.exists():
        raise NotFound(f"Image file not found: {relative_path}")

    # Determine MIME type from file extension
    file_ext = file_path.suffix.lower()
    mime_type_map = {
        ".jpg": "image/jpeg",
        ".jpeg": "image/jpeg",
        ".png": "image/png",
        ".gif": "image/gif",
        ".webp": "image/webp",
        ".bmp": "image/bmp",
        ".svg": "image/svg+xml"
    }

    mime_type = mime_type_map.get(file_ext, "application/octet-stream")

    # Return the file with proper content type
    return send_file(
        str(file_path),
        mimetype=mime_type,
        as_attachment=False
    )


@api_bp.route("/images/<path:relative_path>", methods=["DELETE"])
def delete_image(relative_path: str) -> tuple[dict[str, str], int]:
    """
    Delete an image file by its relative path.

    Removes the file from storage.
    """
    storage_path = _get_storage_path()

    # Remove the storage path prefix if it exists in the relative path
    storage_dir_name = Path(current_app.config["IMAGE_STORAGE_PATH"]).name
    if relative_path.startswith(storage_dir_name + "/"):
        relative_path = relative_path[len(storage_dir_name) + 1:]

    # Construct full file path
    file_path = storage_path / relative_path

    # Security: ensure the path is within storage directory
    try:
        file_path = file_path.resolve()
        storage_path = storage_path.resolve()
        file_path.relative_to(storage_path)
    except ValueError:
        raise NotFound("Invalid file path") from None

    # Check if file exists
    if not file_path.exists():
        raise NotFound(f"Image file not found: {relative_path}")

    # Delete file from storage
    try:
        file_path.unlink()
    except Exception as exc:
        raise BadRequest(f"Failed to delete image file: {exc}") from exc

    return {"message": f"Image '{relative_path}' deleted successfully"}, 200
