"""Tests for the MCP server implementation."""

import json
import os
import requests
import pytest
import tempfile
from pathlib import Path
from unittest.mock import patch, MagicMock

from mcp_openvision.server import (
    image_analysis,
    mcp,
    is_url,
    is_base64,
    process_image_input,
    load_image_from_url,
    load_image_from_path,
)
from mcp_openvision.exceptions import OpenRouterError


@pytest.fixture
def mock_api_key():
    """Set a mock API key for testing."""
    original_key = os.environ.get("OPENROUTER_API_KEY")
    os.environ["OPENROUTER_API_KEY"] = "test_api_key"
    yield
    if original_key:
        os.environ["OPENROUTER_API_KEY"] = original_key
    else:
        del os.environ["OPENROUTER_API_KEY"]


@pytest.fixture
def sample_image_file():
    """Create a temporary image file for testing."""
    with tempfile.NamedTemporaryFile(suffix=".jpg", delete=False) as tmp:
        # Write some dummy image content
        tmp.write(b"dummy image content")
        tmp.flush()
        yield tmp.name
    # Clean up the file after the test
    try:
        os.unlink(tmp.name)
    except Exception:
        pass


def test_is_url():
    """Test the is_url function."""
    assert is_url("http://example.com/image.jpg") is True
    assert is_url("https://example.com/image.jpg") is True
    assert is_url("ftp://example.com/image.jpg") is True
    assert is_url("example.com") is False
    assert is_url("/path/to/image.jpg") is False
    assert is_url("image.jpg") is False
    assert is_url("data:image/jpeg;base64,abc123") is False


def test_is_base64():
    """Test the is_base64 function."""
    # Valid base64
    valid_base64 = "SGVsbG8gV29ybGQ="  # "Hello World" in base64
    assert is_base64(valid_base64) is True

    # Base64 with data URL prefix
    data_url = "data:image/jpeg;base64,SGVsbG8gV29ybGQ="
    assert is_base64(data_url) is True

    # Invalid base64
    assert is_base64("not base64!") is False
    assert is_base64("http://example.com") is False
    assert is_base64("/path/to/image.jpg") is False


@patch("mcp_openvision.server.requests.get")
def test_load_image_from_url(mock_get):
    """Test loading an image from a URL."""
    # Mock the response
    mock_response = MagicMock()
    mock_response.status_code = 200
    mock_response.content = b"dummy image content"
    mock_get.return_value = mock_response

    # Test successful URL loading
    base64_result = load_image_from_url("http://example.com/image.jpg")
    assert isinstance(base64_result, str)

    # Test URL loading error
    mock_response.status_code = 404
    with pytest.raises(Exception):
        load_image_from_url("http://example.com/not-found.jpg")


def test_load_image_from_path(sample_image_file):
    """Test loading an image from a file path."""
    # Test with a valid file
    base64_result = load_image_from_path(sample_image_file)
    assert isinstance(base64_result, str)

    # Test with a non-existent file
    with pytest.raises(FileNotFoundError):
        load_image_from_path("/path/to/nonexistent/image.jpg")

    # Create a test directory structure for project_root testing
    with tempfile.TemporaryDirectory() as temp_dir:
        # Create a test file within a subdirectory
        test_subdir = Path(temp_dir) / "subdir"
        test_subdir.mkdir()
        test_file = test_subdir / "test_image.jpg"
        with open(test_file, "wb") as f:
            f.write(b"test image content")

        # Test with project_root and relative path
        base64_result = load_image_from_path(
            "subdir/test_image.jpg", project_root=temp_dir
        )
        assert isinstance(base64_result, str)

        # Test with project_root but invalid path
        with pytest.raises(FileNotFoundError) as excinfo:
            load_image_from_path("non_existent.jpg", project_root=temp_dir)
        assert "tried directly and under project root" in str(excinfo.value)

        # Test with relative path but no project_root
        with pytest.raises(FileNotFoundError) as excinfo:
            load_image_from_path("some/relative/path.jpg")
        assert "relative path used without specifying project_root" in str(
            excinfo.value
        )


@patch("mcp_openvision.server.load_image_from_url")
@patch("mcp_openvision.server.load_image_from_path")
def test_process_image_input(mock_load_path, mock_load_url):
    """Test the process_image_input function."""
    # Setup mocks
    mock_load_url.return_value = "base64_from_url"
    mock_load_path.return_value = "base64_from_path"

    # Test with base64 input
    base64_input = "SGVsbG8gV29ybGQ="  # Valid base64
    result = process_image_input(base64_input)
    assert result == base64_input

    # Test with URL input
    url_input = "http://example.com/image.jpg"
    result = process_image_input(url_input)
    assert result == "base64_from_url"
    mock_load_url.assert_called_once_with(url_input)

    # Test with path input (no project_root)
    path_input = "/path/to/image.jpg"
    result = process_image_input(path_input)
    assert result == "base64_from_path"
    mock_load_path.assert_called_once_with(path_input, None)

    # Reset mocks for next test
    mock_load_path.reset_mock()

    # Test with path input and project_root
    path_input = "relative/path/to/image.jpg"
    project_root = "/app/root"
    result = process_image_input(path_input, project_root)
    assert result == "base64_from_path"
    mock_load_path.assert_called_once_with(path_input, project_root)

    # Test with invalid input
    mock_load_path.side_effect = FileNotFoundError("File not found")
    with pytest.raises(ValueError):
        process_image_input("invalid_input")


@pytest.mark.asyncio
@patch("mcp_openvision.server.process_image_input")
@patch("requests.post")
async def test_image_analysis_with_file_path(mock_post, mock_process, mock_api_key):
    """Test image analysis with a file path."""
    # Set up mocks
    mock_process.return_value = "base64_encoded_image"

    mock_response = MagicMock()
    mock_response.status_code = 200
    mock_response.json.return_value = {
        "choices": [{"message": {"content": "This is a test image analysis result."}}]
    }
    mock_post.return_value = mock_response

    # Call the function with a file path
    result = await image_analysis(image="/path/to/image.jpg", query="Test prompt")

    # Verify the result
    assert result == "This is a test image analysis result."

    # Verify the image was processed
    mock_process.assert_called_once_with("/path/to/image.jpg", None)

    # Verify the API was called correctly
    mock_post.assert_called_once()


@pytest.mark.asyncio
@patch("mcp_openvision.server.process_image_input")
@patch("requests.post")
async def test_image_analysis_with_project_root(mock_post, mock_process, mock_api_key):
    """Test image analysis with a file path and project root."""
    # Set up mocks
    mock_process.return_value = "base64_encoded_image"

    mock_response = MagicMock()
    mock_response.status_code = 200
    mock_response.json.return_value = {
        "choices": [{"message": {"content": "This is a test image analysis result."}}]
    }
    mock_post.return_value = mock_response

    # Call the function with a file path and project root
    result = await image_analysis(
        image="examples/test_image.png",
        project_root="/path/to/project",
        query="Test prompt",
    )

    # Verify the result
    assert result == "This is a test image analysis result."

    # Verify the image was processed with project_root
    mock_process.assert_called_once_with("examples/test_image.png", "/path/to/project")

    # Verify the API was called correctly
    mock_post.assert_called_once()


@pytest.mark.asyncio
@patch("mcp_openvision.server.process_image_input")
@patch("requests.post")
async def test_image_analysis_with_url(mock_post, mock_process, mock_api_key):
    """Test image analysis with a URL."""
    # Set up mocks
    mock_process.return_value = "base64_encoded_image"

    mock_response = MagicMock()
    mock_response.status_code = 200
    mock_response.json.return_value = {
        "choices": [{"message": {"content": "This is a test image analysis result."}}]
    }
    mock_post.return_value = mock_response

    # Call the function with a URL
    result = await image_analysis(
        image="http://example.com/image.jpg", query="Test prompt"
    )

    # Verify the result
    assert result == "This is a test image analysis result."

    # Verify the image was processed
    mock_process.assert_called_once_with("http://example.com/image.jpg", None)

    # Verify the API was called correctly
    mock_post.assert_called_once()


@pytest.mark.asyncio
@patch("mcp_openvision.server.process_image_input")
@patch("requests.post")
async def test_image_analysis_with_base64(mock_post, mock_process, mock_api_key):
    """Test image analysis with base64 data."""
    # Set up mocks
    base64_image = "SGVsbG8gV29ybGQ="  # Valid base64
    mock_process.return_value = base64_image

    mock_response = MagicMock()
    mock_response.status_code = 200
    mock_response.json.return_value = {
        "choices": [{"message": {"content": "This is a test image analysis result."}}]
    }
    mock_post.return_value = mock_response

    # Call the function with base64 data
    result = await image_analysis(image=base64_image, query="Test prompt")

    # Verify the result
    assert result == "This is a test image analysis result."

    # Verify the image was processed
    mock_process.assert_called_once_with(base64_image, None)

    # Verify the API was called correctly
    mock_post.assert_called_once()


@pytest.mark.asyncio
@patch("mcp_openvision.server.process_image_input")
@patch("requests.post")
async def test_image_analysis_processing_error(mock_post, mock_process, mock_api_key):
    """Test error handling when image processing fails."""
    # Set up mock to raise an exception
    mock_process.side_effect = ValueError("Invalid image")

    # Call the function and verify it raises a ValueError
    with pytest.raises(ValueError) as excinfo:
        await image_analysis(image="invalid_input", query="Test prompt")

    # Verify error details
    assert "Failed to process image" in str(excinfo.value)

    # Verify the API was not called
    mock_post.assert_not_called()


@pytest.mark.asyncio
@patch("requests.post")
async def test_image_analysis_api_error(mock_post, mock_api_key):
    """Test API error handling."""
    # Set up the mock response
    mock_response = MagicMock()
    mock_response.status_code = 401
    mock_response.text = "Unauthorized"
    mock_post.return_value = mock_response

    # Call the function and verify it raises an OpenRouterError
    with pytest.raises(OpenRouterError) as excinfo:
        await image_analysis(
            image="SGVsbG8gV29ybGQ=", query="Test prompt"  # Valid base64
        )

    # Verify error details
    assert excinfo.value.status_code == 401
    assert "Unauthorized" in str(excinfo.value)


@pytest.mark.asyncio
@patch("requests.post")
async def test_image_analysis_network_error(mock_post, mock_api_key):
    """Test network error handling."""
    # Set up the mock to raise a requests.RequestException
    mock_post.side_effect = requests.RequestException("Connection error")

    # Call the function and verify it raises an OpenRouterError
    with pytest.raises(OpenRouterError) as excinfo:
        await image_analysis(
            image="SGVsbG8gV29ybGQ=", query="Test prompt"  # Valid base64
        )

    # Verify error details
    assert excinfo.value.status_code == 0
    assert "Connection error" in str(excinfo.value)
