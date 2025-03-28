"""
Tests for the MCP OpenVision server.
"""

import os
import sys
from pathlib import Path
from unittest.mock import AsyncMock, MagicMock, patch

import pytest

# Add the src directory to sys.path to import the package
src_dir = Path(__file__).parent.parent / "src"
sys.path.append(str(src_dir))

from mcp_openvision.server import (
    AnalysisMode,
    VisionModel,
    analyze_image,
    compare_images,
    extract_text_from_image,
    get_openrouter_api_key,
)


# Fixtures
@pytest.fixture
def mock_image():
    """Create a mock Image object."""
    mock = MagicMock()
    mock.data = b"fake_image_data"
    return mock


@pytest.fixture
def mock_context():
    """Create a mock Context object."""
    mock = MagicMock()
    mock.info = MagicMock()
    mock.error = MagicMock()
    return mock


@pytest.fixture
def mock_response():
    """Create a mock response object."""
    mock = MagicMock()
    mock.status_code = 200
    mock.json.return_value = {
        "choices": [{"message": {"content": "Test analysis result"}}]
    }
    return mock


# Tests
def test_get_openrouter_api_key():
    """Test the get_openrouter_api_key function."""
    with patch.dict(os.environ, {"OPENROUTER_API_KEY": "test_key"}):
        assert get_openrouter_api_key() == "test_key"

    with patch.dict(os.environ, {}, clear=True):
        with pytest.raises(ValueError):
            get_openrouter_api_key()


@pytest.mark.asyncio
async def test_analyze_image(mock_image, mock_context, mock_response):
    """Test the analyze_image function."""
    with patch("mcp_openvision.server.get_openrouter_api_key", return_value="test_key"), patch(
        "mcp_openvision.server.encode_image_to_base64", return_value="base64_encoded"
    ), patch("mcp_openvision.server.requests.post", return_value=mock_response):
        result = await analyze_image(
            image=mock_image,
            prompt="Test prompt",
            model=VisionModel.CLAUDE_3_SONNET,
            mode=AnalysisMode.GENERAL,
            ctx=mock_context,
        )
        
        assert result == "Test analysis result"
        mock_context.info.assert_called()


@pytest.mark.asyncio
async def test_extract_text_from_image(mock_image, mock_context):
    """Test the extract_text_from_image function."""
    with patch("mcp_openvision.server.analyze_image", AsyncMock(return_value="Extracted text")):
        result = await extract_text_from_image(
            image=mock_image,
            language="English",
            model=VisionModel.CLAUDE_3_SONNET,
            ctx=mock_context,
        )
        
        assert result == "Extracted text"
        mock_context.info.assert_called()


@pytest.mark.asyncio
async def test_compare_images(mock_image, mock_context, mock_response):
    """Test the compare_images function."""
    with patch("mcp_openvision.server.get_openrouter_api_key", return_value="test_key"), patch(
        "mcp_openvision.server.encode_image_to_base64", return_value="base64_encoded"
    ), patch("mcp_openvision.server.requests.post", return_value=mock_response):
        result = await compare_images(
            image1=mock_image,
            image2=mock_image,
            comparison_aspect="colors",
            model=VisionModel.CLAUDE_3_SONNET,
            ctx=mock_context,
        )
        
        assert result == "Test analysis result"
        mock_context.info.assert_called() 