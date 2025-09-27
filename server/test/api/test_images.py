"""Tests for image API endpoints."""
from __future__ import annotations

from io import BytesIO
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from flask.testing import FlaskClient


class TestImageUploadEndpoint:
    """Test cases for POST /api/images endpoint."""

    def test_upload_image_success_jpeg(self, client: FlaskClient) -> None:
        """Test successful image upload with JPEG file."""
        # Given - Create a test JPEG image
        image_data = b"\xff\xd8\xff\xe0\x00\x10JFIF\x00\x01\x01\x01\x00H\x00H\x00\x00\xff\xdb\x00C\x00\x08\x06\x06\x07\x06\x05\x08\x07\x07\x07\t\t\x08\n\x0c\x14\r\x0c\x0b\x0b\x0c\x19\x12\x13\x0f\x14\x1d\x1a\x1f\x1e\x1d\x1a\x1c\x1c $.' \",#\x1c\x1c(7),01444\x1f'9=82<.342\xff\xc0\x00\x11\x08\x00\x01\x00\x01\x01\x01\x11\x00\x02\x11\x01\x03\x11\x01\xff\xc4\x00\x14\x00\x01\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x08\xff\xc4\x00\x14\x10\x01\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\xff\xda\x00\x0c\x03\x01\x00\x02\x11\x03\x11\x00\x3f\x00\xaa\xff\xd9"

        # When
        response = client.post(
            "/api/images",
            data={"image": (BytesIO(image_data), "test.jpg")},
            content_type="multipart/form-data"
        )

        # Then
        assert response.status_code == 201
        data = response.get_json()
        assert "file_path" in data
        assert data["original_filename"] == "test.jpg"
        assert data["content_type"] == "image/jpeg"
        assert data["file_size"] == len(image_data)

        # Verify file was saved
        file_path = data["file_path"]
        assert file_path.endswith(".jpg")

    def test_upload_image_success_png(self, client: FlaskClient) -> None:
        """Test successful image upload with PNG file."""
        # Given - Create a minimal PNG image
        png_data = b"\x89PNG\r\n\x1a\n\x00\x00\x00\rIHDR\x00\x00\x00\x01\x00\x00\x00\x01\x08\x02\x00\x00\x00\x90wS\xde\x00\x00\x00\x0cIDATx\x9cc\xf8\x00\x00\x00\x01\x00\x01Z:;\x97\x00\x00\x00\x00IEND\xaeB`\x82"

        # When
        response = client.post(
            "/api/images",
            data={"image": (BytesIO(png_data), "test.png")},
            content_type="multipart/form-data"
        )

        # Then
        assert response.status_code == 201
        data = response.get_json()
        assert "file_path" in data
        assert data["original_filename"] == "test.png"
        assert data["content_type"] == "image/png"
        assert data["file_size"] == len(png_data)

    def test_upload_image_no_file(self, client: FlaskClient) -> None:
        """Test upload endpoint with no file provided."""
        # When
        response = client.post("/api/images", data={}, content_type="multipart/form-data")

        # Then
        assert response.status_code == 400
        assert "No 'image' field in request" in response.get_json()["msg"]

    def test_upload_image_empty_filename(self, client: FlaskClient) -> None:
        """Test upload endpoint with empty filename."""
        # When
        response = client.post(
            "/api/images",
            data={"image": (BytesIO(b"fake image data"), "")},
            content_type="multipart/form-data"
        )

        # Then
        assert response.status_code == 400

    def test_upload_image_invalid_extension(self, client: FlaskClient) -> None:
        """Test upload endpoint with invalid file extension."""
        # When
        response = client.post(
            "/api/images",
            data={"image": (BytesIO(b"fake image data"), "test.txt")},
            content_type="multipart/form-data"
        )

        # Then
        assert response.status_code == 415
        assert "File type '.txt' not allowed" in response.get_json()["msg"]

    def test_upload_image_invalid_content_type(self, client: FlaskClient) -> None:
        """Test upload endpoint with invalid content type."""
        # When
        response = client.post(
            "/api/images",
            data={"image": (BytesIO(b"fake image data"), "test.jpg", "text/plain")},
            content_type="multipart/form-data"
        )

        # Then
        assert response.status_code == 415
        assert "Content type 'text/plain' not allowed" in response.get_json()["msg"]

    def test_upload_image_empty_file(self, client: FlaskClient) -> None:
        """Test upload endpoint with empty file."""
        # When
        response = client.post(
            "/api/images",
            data={"image": (BytesIO(b""), "test.jpg")},
            content_type="multipart/form-data"
        )

        # Then
        assert response.status_code == 400
        assert "File is empty" in response.get_json()["msg"]

    def test_upload_image_file_too_large(self, client: FlaskClient) -> None:
        """Test upload endpoint with file exceeding size limit."""
        # Given - Create a file larger than 10MB
        large_data = b"x" * (11 * 1024 * 1024)  # 11MB

        # When
        response = client.post(
            "/api/images",
            data={"image": (BytesIO(large_data), "large.jpg")},
            content_type="multipart/form-data"
        )

        # Then
        assert response.status_code == 400
        assert "exceeds maximum allowed size" in response.get_json()["msg"]


class TestImageRetrievalEndpoint:
    """Test cases for GET /api/images/<path> endpoint."""

    def test_get_image_success(self, client: FlaskClient) -> None:
        """Test successful image retrieval."""
        # Given - Upload an image first
        image_data = b"\xff\xd8\xff\xe0\x00\x10JFIF\x00\x01\x01\x01\x00H\x00H\x00\x00\xff\xdb\x00C\x00\x08\x06\x06\x07\x06\x05\x08\x07\x07\x07\t\t\x08\n\x0c\x14\r\x0c\x0b\x0b\x0c\x19\x12\x13\x0f\x14\x1d\x1a\x1f\x1e\x1d\x1a\x1c\x1c $.' \",#\x1c\x1c(7),01444\x1f'9=82<.342\xff\xc0\x00\x11\x08\x00\x01\x00\x01\x01\x01\x11\x00\x02\x11\x01\x03\x11\x01\xff\xc4\x00\x14\x00\x01\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x08\xff\xc4\x00\x14\x10\x01\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\xff\xda\x00\x0c\x03\x01\x00\x02\x11\x03\x11\x00\x3f\x00\xaa\xff\xd9"

        upload_response = client.post(
            "/api/images",
            data={"image": (BytesIO(image_data), "test.jpg")},
            content_type="multipart/form-data"
        )
        file_path = upload_response.get_json()["file_path"]

        # When - Retrieve the image
        response = client.get(f"/api/images/{file_path}")

        # Then
        assert response.status_code == 200
        assert response.content_type == "image/jpeg"
        assert response.data == image_data

    def test_get_image_not_found(self, client: FlaskClient) -> None:
        """Test image retrieval with non-existent file."""
        # When
        response = client.get("/api/images/nonexistent/file.jpg")

        # Then
        assert response.status_code == 404
        assert "Image file not found" in response.get_json()["msg"]

    def test_get_image_path_traversal_attempt(self, client: FlaskClient) -> None:
        """Test image retrieval with path traversal attempt."""
        # When
        response = client.get("/api/images/../../../etc/passwd")

        # Then
        assert response.status_code == 404
        assert "Invalid file path" in response.get_json()["msg"]


class TestImageDeletionEndpoint:
    """Test cases for DELETE /api/images/<path> endpoint."""

    def test_delete_image_success(self, client: FlaskClient) -> None:
        """Test successful image deletion."""
        # Given - Upload an image first
        image_data = b"\xff\xd8\xff\xe0\x00\x10JFIF\x00\x01\x01\x01\x00H\x00H\x00\x00\xff\xdb\x00C\x00\x08\x06\x06\x07\x06\x05\x08\x07\x07\x07\t\t\x08\n\x0c\x14\r\x0c\x0b\x0b\x0c\x19\x12\x13\x0f\x14\x1d\x1a\x1f\x1e\x1d\x1a\x1c\x1c $.' \",#\x1c\x1c(7),01444\x1f'9=82<.342\xff\xc0\x00\x11\x08\x00\x01\x00\x01\x01\x01\x11\x00\x02\x11\x01\x03\x11\x01\xff\xc4\x00\x14\x00\x01\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x08\xff\xc4\x00\x14\x10\x01\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\xff\xda\x00\x0c\x03\x01\x00\x02\x11\x03\x11\x00\x3f\x00\xaa\xff\xd9"

        upload_response = client.post(
            "/api/images",
            data={"image": (BytesIO(image_data), "test.jpg")},
            content_type="multipart/form-data"
        )
        file_path = upload_response.get_json()["file_path"]

        # When - Delete the image
        response = client.delete(f"/api/images/{file_path}")

        # Then
        assert response.status_code == 200
        assert "deleted successfully" in response.get_json()["message"]

        # Verify file is actually deleted
        get_response = client.get(f"/api/images/{file_path}")
        assert get_response.status_code == 404

    def test_delete_image_not_found(self, client: FlaskClient) -> None:
        """Test image deletion with non-existent file."""
        # When
        response = client.delete("/api/images/nonexistent/file.jpg")

        # Then
        assert response.status_code == 404
        assert "Image file not found" in response.get_json()["msg"]

    def test_delete_image_path_traversal_attempt(self, client: FlaskClient) -> None:
        """Test image deletion with path traversal attempt."""
        # When
        response = client.delete("/api/images/../../../etc/passwd")

        # Then
        assert response.status_code == 404
        assert "Invalid file path" in response.get_json()["msg"]


class TestImageEndpointIntegration:
    """Integration tests for complete image lifecycle."""

    def test_upload_retrieve_delete_lifecycle(self, client: FlaskClient) -> None:
        """Test complete lifecycle: upload -> retrieve -> delete."""
        # Given - Test image data
        image_data = b"\xff\xd8\xff\xe0\x00\x10JFIF\x00\x01\x01\x01\x00H\x00H\x00\x00\xff\xdb\x00C\x00\x08\x06\x06\x07\x06\x05\x08\x07\x07\x07\t\t\x08\n\x0c\x14\r\x0c\x0b\x0b\x0c\x19\x12\x13\x0f\x14\x1d\x1a\x1f\x1e\x1d\x1a\x1c\x1c $.' \",#\x1c\x1c(7),01444\x1f'9=82<.342\xff\xc0\x00\x11\x08\x00\x01\x00\x01\x01\x01\x11\x00\x02\x11\x01\x03\x11\x01\xff\xc4\x00\x14\x00\x01\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x08\xff\xc4\x00\x14\x10\x01\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\xff\xda\x00\x0c\x03\x01\x00\x02\x11\x03\x11\x00\x3f\x00\xaa\xff\xd9"

        # Step 1: Upload image
        upload_response = client.post(
            "/api/images",
            data={"image": (BytesIO(image_data), "lifecycle_test.jpg")},
            content_type="multipart/form-data"
        )
        assert upload_response.status_code == 201
        file_path = upload_response.get_json()["file_path"]

        # Step 2: Retrieve image
        get_response = client.get(f"/api/images/{file_path}")
        assert get_response.status_code == 200
        assert get_response.data == image_data

        # Step 3: Delete image
        delete_response = client.delete(f"/api/images/{file_path}")
        assert delete_response.status_code == 200

        # Step 4: Verify deletion
        final_get_response = client.get(f"/api/images/{file_path}")
        assert final_get_response.status_code == 404
