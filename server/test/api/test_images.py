"""Tests for image API endpoints."""
from __future__ import annotations

import tempfile
from io import BytesIO
from pathlib import Path
from typing import TYPE_CHECKING
from unittest.mock import patch

from werkzeug.datastructures import FileStorage

from src.models import Image, db

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
        assert "image_id" in data
        assert data["original_filename"] == "test.jpg"
        assert data["content_type"] == "image/jpeg"
        assert data["file_size"] == len(image_data)

        # Verify database record was created
        image_id = data["image_id"]
        image = db.session.get(Image, image_id)
        assert image is not None
        assert image.original_filename == "test.jpg"
        assert image.content_type == "image/jpeg"
        assert image.file_size == len(image_data)

        # Verify file was saved
        file_path = Path(image.file_path)
        assert file_path.exists()
        assert file_path.stat().st_size == len(image_data)

    def test_upload_image_success_png(self, client: FlaskClient) -> None:
        """Test successful image upload with PNG file."""
        # Given - Create a minimal PNG image (1x1 pixel)
        png_data = b"\x89PNG\r\n\x1a\n\x00\x00\x00\rIHDR\x00\x00\x00\x01\x00\x00\x00\x01\x08\x02\x00\x00\x00\x90wS\xde\x00\x00\x00\tpHYs\x00\x00\x0b\x13\x00\x00\x0b\x13\x01\x00\x9a\x9c\x18\x00\x00\x00\nIDATx\x9cc\xf8\x00\x00\x00\x01\x00\x01\x01\x00\x00\x00\x00IEND\xaeB`\x82"

        # When
        response = client.post(
            "/api/images",
            data={"image": (BytesIO(png_data), "test.png")},
            content_type="multipart/form-data"
        )

        # Then
        assert response.status_code == 201
        data = response.get_json()
        assert data["original_filename"] == "test.png"
        assert data["content_type"] == "image/png"
        assert data["file_size"] == len(png_data)

    def test_upload_image_no_file_field(self, client: FlaskClient) -> None:
        """Test error when no image field is provided."""
        # When
        response = client.post("/api/images", data={}, content_type="multipart/form-data")

        # Then
        assert response.status_code == 400
        data = response.get_json()
        assert "No 'image' field" in data["msg"]

    def test_upload_image_empty_file(self, client: FlaskClient) -> None:
        """Test error when empty file is uploaded."""
        # When
        response = client.post(
            "/api/images",
            data={"image": (BytesIO(b""), "empty.jpg")},
            content_type="multipart/form-data"
        )

        # Then
        assert response.status_code == 400
        data = response.get_json()
        assert "File is empty" in data["msg"]

    def test_upload_image_no_filename(self, client: FlaskClient) -> None:
        """Test error when file has no filename."""
        # When
        response = client.post(
            "/api/images",
            data={"image": (BytesIO(b"test"), "")},
            content_type="multipart/form-data"
        )

        # Then
        assert response.status_code == 400
        data = response.get_json()
        assert "No file provided" in data["msg"]

    def test_upload_image_invalid_extension(self, client: FlaskClient) -> None:
        """Test error when file has invalid extension."""
        # When
        response = client.post(
            "/api/images",
            data={"image": (BytesIO(b"test content"), "test.txt")},
            content_type="multipart/form-data"
        )

        # Then
        assert response.status_code == 415
        data = response.get_json()
        assert "File type '.txt' not allowed" in data["msg"]

    def test_upload_image_invalid_content_type(self, client: FlaskClient) -> None:
        """Test error when file has invalid content type."""
        # Given - File with image extension but wrong content type
        file_storage = FileStorage(
            stream=BytesIO(b"test content"),
            filename="test.jpg",
            content_type="text/plain"
        )

        # When
        response = client.post(
            "/api/images",
            data={"image": file_storage},
            content_type="multipart/form-data"
        )

        # Then
        assert response.status_code == 415
        data = response.get_json()
        assert "Content type 'text/plain' not allowed" in data["msg"]

    def test_upload_image_file_too_large(self, client: FlaskClient) -> None:
        """Test error when file exceeds size limit."""
        # Given - File larger than 10MB
        large_data = b"x" * (11 * 1024 * 1024)  # 11MB

        # When
        response = client.post(
            "/api/images",
            data={"image": (BytesIO(large_data), "large.jpg")},
            content_type="multipart/form-data"
        )

        # Then
        assert response.status_code == 400
        data = response.get_json()
        assert "exceeds maximum allowed size" in data["msg"]

    def test_upload_image_creates_storage_directory(self, client: FlaskClient) -> None:
        """Test that storage directory is created if it doesn't exist."""
        # Given - Configure a temporary storage path that doesn't exist
        with tempfile.TemporaryDirectory() as temp_dir:
            storage_path = Path(temp_dir) / "nonexistent" / "images"

            with patch.dict(client.application.config, {"IMAGE_STORAGE_PATH": str(storage_path)}):
                image_data = b"\x89PNG\r\n\x1a\n\x00\x00\x00\rIHDR\x00\x00\x00\x01\x00\x00\x00\x01\x08\x02\x00\x00\x00\x90wS\xde\x00\x00\x00\nIDATx\x9cc\xf8\x00\x00\x00\x01\x00\x01\x01\x00\x00\x00\x00IEND\xaeB`\x82"

                # When
                response = client.post(
                    "/api/images",
                    data={"image": (BytesIO(image_data), "test.png")},
                    content_type="multipart/form-data"
                )

                # Then
                assert response.status_code == 201
                assert storage_path.exists()
                assert storage_path.is_dir()

    def test_upload_image_rollback_on_database_error(self, client: FlaskClient) -> None:
        """Test that file is cleaned up if database save fails."""
        # Given
        image_data = b"\x89PNG\r\n\x1a\n\x00\x00\x00\rIHDR\x00\x00\x00\x01\x00\x00\x00\x01\x08\x02\x00\x00\x00\x90wS\xde\x00\x00\x00\nIDATx\x9cc\xf8\x00\x00\x00\x01\x00\x01\x01\x00\x00\x00\x00IEND\xaeB`\x82"

        with patch("src.api.images.db.session.commit", side_effect=Exception("Database error")):
            # When
            response = client.post(
                "/api/images",
                data={"image": (BytesIO(image_data), "test.png")},
                content_type="multipart/form-data"
            )

            # Then
            assert response.status_code == 400
            data = response.get_json()
            assert "Failed to save image metadata" in data["msg"]

    def test_upload_image_unique_ids(self, client: FlaskClient) -> None:
        """Test that multiple uploads get unique IDs."""
        # Given
        image_data = b"\x89PNG\r\n\x1a\n\x00\x00\x00\rIHDR\x00\x00\x00\x01\x00\x00\x00\x01\x08\x02\x00\x00\x00\x90wS\xde\x00\x00\x00\nIDATx\x9cc\xf8\x00\x00\x00\x01\x00\x01\x01\x00\x00\x00\x00IEND\xaeB`\x82"

        # When - Upload same image twice
        response1 = client.post(
            "/api/images",
            data={"image": (BytesIO(image_data), "test1.png")},
            content_type="multipart/form-data"
        )
        response2 = client.post(
            "/api/images",
            data={"image": (BytesIO(image_data), "test2.png")},
            content_type="multipart/form-data"
        )

        # Then
        assert response1.status_code == 201
        assert response2.status_code == 201

        data1 = response1.get_json()
        data2 = response2.get_json()

        assert data1["image_id"] != data2["image_id"]
        assert data1["original_filename"] == "test1.png"
        assert data2["original_filename"] == "test2.png"


class TestImageRetrievalEndpoint:
    """Test cases for GET /api/images/{image_id} endpoint."""

    def test_get_image_success(self, client: FlaskClient) -> None:
        """Test successful image retrieval."""
        # Given - Upload an image first
        image_data = b"\x89PNG\r\n\x1a\n\x00\x00\x00\rIHDR\x00\x00\x00\x01\x00\x00\x00\x01\x08\x02\x00\x00\x00\x90wS\xde\x00\x00\x00\nIDATx\x9cc\xf8\x00\x00\x00\x01\x00\x01\x01\x00\x00\x00\x00IEND\xaeB`\x82"

        upload_response = client.post(
            "/api/images",
            data={"image": (BytesIO(image_data), "test.png")},
            content_type="multipart/form-data"
        )
        image_id = upload_response.get_json()["image_id"]

        # When
        response = client.get(f"/api/images/{image_id}")

        # Then
        assert response.status_code == 200
        assert response.content_type == "image/png"
        assert response.data == image_data

    def test_get_image_not_found(self, client: FlaskClient) -> None:
        """Test retrieval of non-existent image."""
        # When
        response = client.get("/api/images/nonexistent-id")

        # Then
        assert response.status_code == 404
        data = response.get_json()
        assert "Image with ID 'nonexistent-id' not found" in data["msg"]

    def test_get_image_file_missing_on_disk(self, client: FlaskClient) -> None:
        """Test retrieval when database record exists but file is missing."""
        # Given - Create database record with non-existent file path
        image = Image(
            id="test-id",
            original_filename="missing.png",
            content_type="image/png",
            file_size=100,
            file_path="/nonexistent/path/missing.png"
        )
        db.session.add(image)
        db.session.commit()

        # When
        response = client.get("/api/images/test-id")

        # Then
        assert response.status_code == 404
        data = response.get_json()
        assert "Image file not found on disk" in data["msg"]


class TestImageMetadataEndpoint:
    """Test cases for GET /api/images/{image_id}/metadata endpoint."""

    def test_get_image_metadata_success(self, client: FlaskClient) -> None:
        """Test successful image metadata retrieval."""
        # Given - Upload an image first
        image_data = b"\x89PNG\r\n\x1a\n\x00\x00\x00\rIHDR\x00\x00\x00\x01\x00\x00\x00\x01\x08\x02\x00\x00\x00\x90wS\xde\x00\x00\x00\nIDATx\x9cc\xf8\x00\x00\x00\x01\x00\x01\x01\x00\x00\x00\x00IEND\xaeB`\x82"

        upload_response = client.post(
            "/api/images",
            data={"image": (BytesIO(image_data), "test.png")},
            content_type="multipart/form-data"
        )
        upload_data = upload_response.get_json()
        image_id = upload_data["image_id"]

        # When
        response = client.get(f"/api/images/{image_id}/metadata")

        # Then
        assert response.status_code == 200
        data = response.get_json()
        assert data["image_id"] == image_id
        assert data["original_filename"] == "test.png"
        assert data["content_type"] == "image/png"
        assert data["file_size"] == len(image_data)
        assert "created_at" in data
        assert "updated_at" in data

    def test_get_image_metadata_not_found(self, client: FlaskClient) -> None:
        """Test metadata retrieval for non-existent image."""
        # When
        response = client.get("/api/images/nonexistent-id/metadata")

        # Then
        assert response.status_code == 404
        data = response.get_json()
        assert "Image with ID 'nonexistent-id' not found" in data["msg"]


class TestImageDeleteEndpoint:
    """Test cases for DELETE /api/images/{image_id} endpoint."""

    def test_delete_image_success(self, client: FlaskClient) -> None:
        """Test successful image deletion."""
        # Given - Upload an image first
        image_data = b"\x89PNG\r\n\x1a\n\x00\x00\x00\rIHDR\x00\x00\x00\x01\x00\x00\x00\x01\x08\x02\x00\x00\x00\x90wS\xde\x00\x00\x00\nIDATx\x9cc\xf8\x00\x00\x00\x01\x00\x01\x01\x00\x00\x00\x00IEND\xaeB`\x82"

        upload_response = client.post(
            "/api/images",
            data={"image": (BytesIO(image_data), "test.png")},
            content_type="multipart/form-data"
        )
        image_id = upload_response.get_json()["image_id"]

        # Verify file exists
        image = db.session.get(Image, image_id)
        file_path = Path(image.file_path)
        assert file_path.exists()

        # When
        response = client.delete(f"/api/images/{image_id}")

        # Then
        assert response.status_code == 200
        data = response.get_json()
        assert f"Image '{image_id}' deleted successfully" in data["message"]

        # Verify database record is deleted
        assert db.session.get(Image, image_id) is None

        # Verify file is deleted
        assert not file_path.exists()

    def test_delete_image_not_found(self, client: FlaskClient) -> None:
        """Test deletion of non-existent image."""
        # When
        response = client.delete("/api/images/nonexistent-id")

        # Then
        assert response.status_code == 404
        data = response.get_json()
        assert "Image with ID 'nonexistent-id' not found" in data["msg"]

    def test_delete_image_file_missing_continues(self, client: FlaskClient) -> None:
        """Test that deletion continues even if file is missing on disk."""
        # Given - Create database record with non-existent file path
        image = Image(
            id="test-id",
            original_filename="missing.png",
            content_type="image/png",
            file_size=100,
            file_path="/nonexistent/path/missing.png"
        )
        db.session.add(image)
        db.session.commit()

        # When
        response = client.delete("/api/images/test-id")

        # Then - Should succeed despite missing file
        assert response.status_code == 200
        data = response.get_json()
        assert "Image 'test-id' deleted successfully" in data["message"]

        # Verify database record is deleted
        assert db.session.get(Image, "test-id") is None


class TestImageAPIIntegration:
    """Integration tests for the complete image API workflow."""

    def test_complete_image_lifecycle(self, client: FlaskClient) -> None:
        """Test complete workflow: upload -> retrieve -> metadata -> delete."""
        # Given
        image_data = b"\xff\xd8\xff\xe0\x00\x10JFIF\x00\x01\x01\x01\x00H\x00H\x00\x00\xff\xdb\x00C\x00\x08\x06\x06\x07\x06\x05\x08\x07\x07\x07\t\t\x08\n\x0c\x14\r\x0c\x0b\x0b\x0c\x19\x12\x13\x0f\x14\x1d\x1a\x1f\x1e\x1d\x1a\x1c\x1c $.' \",#\x1c\x1c(7),01444\x1f'9=82<.342\xff\xc0\x00\x11\x08\x00\x01\x00\x01\x01\x01\x11\x00\x02\x11\x01\x03\x11\x01\xff\xc4\x00\x14\x00\x01\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x08\xff\xc4\x00\x14\x10\x01\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\xff\xda\x00\x0c\x03\x01\x00\x02\x11\x03\x11\x00\x3f\x00\xaa\xff\xd9"

        # Step 1: Upload image
        upload_response = client.post(
            "/api/images",
            data={"image": (BytesIO(image_data), "cover.jpg")},
            content_type="multipart/form-data"
        )
        assert upload_response.status_code == 201

        upload_data = upload_response.get_json()
        image_id = upload_data["image_id"]
        assert upload_data["original_filename"] == "cover.jpg"
        assert upload_data["content_type"] == "image/jpeg"

        # Step 2: Retrieve image
        retrieve_response = client.get(f"/api/images/{image_id}")
        assert retrieve_response.status_code == 200
        assert retrieve_response.content_type == "image/jpeg"
        assert retrieve_response.data == image_data

        # Step 3: Get metadata
        metadata_response = client.get(f"/api/images/{image_id}/metadata")
        assert metadata_response.status_code == 200

        metadata = metadata_response.get_json()
        assert metadata["image_id"] == image_id
        assert metadata["original_filename"] == "cover.jpg"
        assert metadata["content_type"] == "image/jpeg"
        assert metadata["file_size"] == len(image_data)

        # Step 4: Delete image
        delete_response = client.delete(f"/api/images/{image_id}")
        assert delete_response.status_code == 200

        # Step 5: Verify deletion
        verify_response = client.get(f"/api/images/{image_id}")
        assert verify_response.status_code == 404

    def test_multiple_images_independent(self, client: FlaskClient) -> None:
        """Test that multiple images can be managed independently."""
        # Given - Two different images
        image1_data = b"\x89PNG\r\n\x1a\n\x00\x00\x00\rIHDR\x00\x00\x00\x01\x00\x00\x00\x01\x08\x02\x00\x00\x00\x90wS\xde\x00\x00\x00\nIDATx\x9cc\xf8\x00\x00\x00\x01\x00\x01\x01\x00\x00\x00\x00IEND\xaeB`\x82"
        image2_data = b"\xff\xd8\xff\xe0\x00\x10JFIF\x00\x01\x01\x01\x00H\x00H\x00\x00\xff\xdb\x00C\x00\x08\x06\x06\x07\x06\x05\x08\x07\x07\x07\t\t\x08\n\x0c\x14\r\x0c\x0b\x0b\x0c\x19\x12\x13\x0f\x14\x1d\x1a\x1f\x1e\x1d\x1a\x1c\x1c $.' \",#\x1c\x1c(7),01444\x1f'9=82<.342\xff\xc0\x00\x11\x08\x00\x01\x00\x01\x01\x01\x11\x00\x02\x11\x01\x03\x11\x01\xff\xc4\x00\x14\x00\x01\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x08\xff\xc4\x00\x14\x10\x01\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\xff\xda\x00\x0c\x03\x01\x00\x02\x11\x03\x11\x00\x3f\x00\xaa\xff\xd9"

        # When - Upload both images
        response1 = client.post(
            "/api/images",
            data={"image": (BytesIO(image1_data), "flag1.png")},
            content_type="multipart/form-data"
        )
        response2 = client.post(
            "/api/images",
            data={"image": (BytesIO(image2_data), "flag2.jpg")},
            content_type="multipart/form-data"
        )

        # Then
        assert response1.status_code == 201
        assert response2.status_code == 201

        image1_id = response1.get_json()["image_id"]
        image2_id = response2.get_json()["image_id"]

        # Verify both images can be retrieved independently
        get1_response = client.get(f"/api/images/{image1_id}")
        get2_response = client.get(f"/api/images/{image2_id}")

        assert get1_response.status_code == 200
        assert get1_response.data == image1_data
        assert get1_response.content_type == "image/png"

        assert get2_response.status_code == 200
        assert get2_response.data == image2_data
        assert get2_response.content_type == "image/jpeg"

        # Delete one image shouldn't affect the other
        delete_response = client.delete(f"/api/images/{image1_id}")
        assert delete_response.status_code == 200

        # Image 1 should be gone
        assert client.get(f"/api/images/{image1_id}").status_code == 404

        # Image 2 should still exist
        assert client.get(f"/api/images/{image2_id}").status_code == 200
