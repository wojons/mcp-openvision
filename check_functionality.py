"""
Simple test script to check if the server functionality works.
This bypasses the pytest framework that has issues with schema generation.
"""

import asyncio
import os
import sys
from pathlib import Path
from unittest.mock import MagicMock, patch

# Add the src directory to sys.path to import the package
src_dir = Path(__file__).parent / "src"
sys.path.append(str(src_dir))


# Mock Image class
class MockImage:
    def __init__(self, data=None, path=None, format=None):
        self.data = data or b"fake_image_data"
        self.path = path
        self._format = format or "jpeg"


# Apply patch for Image
with patch("fastmcp.Image", MockImage):
    from mcp_openvision.server import (
        AnalysisMode,
        VisionModel,
        analyze_image,
        compare_images,
        extract_text_from_image,
    )

# Create mock objects
mock_image = MockImage(data=b"fake_image_data")
mock_context = MagicMock()
mock_context.info = MagicMock()
mock_context.error = MagicMock()

# Create mock response
mock_response = MagicMock()
mock_response.status_code = 200
mock_response.json.return_value = {
    "choices": [{"message": {"content": "Test analysis result"}}]
}


async def test_analyze_image():
    """Test the analyze_image function."""
    with (
        patch.dict(os.environ, {"OPENROUTER_API_KEY": "test_key"}),
        patch(
            "mcp_openvision.server.encode_image_to_base64",
            return_value="base64_encoded",
        ),
        patch(
            "mcp_openvision.server.requests.post",
            return_value=mock_response,
        ),
    ):
        result = await analyze_image(
            image=mock_image,
            prompt="Test prompt",
            model=VisionModel.CLAUDE_3_SONNET,
            mode=AnalysisMode.GENERAL,
            ctx=mock_context,
        )

        print(f"analyze_image result: {result}")
        assert result == "Test analysis result"
        mock_context.info.assert_called()
        print("analyze_image test passed!")


async def test_extract_text_from_image():
    """Test the extract_text_from_image function."""
    with (
        patch.dict(os.environ, {"OPENROUTER_API_KEY": "test_key"}),
        patch(
            "mcp_openvision.server.analyze_image",
            return_value="Extracted text",
        ),
    ):
        result = await extract_text_from_image(
            image=mock_image,
            language="English",
            model=VisionModel.CLAUDE_3_SONNET,
            ctx=mock_context,
        )

        print(f"extract_text_from_image result: {result}")
        assert result == "Extracted text"
        mock_context.info.assert_called()
        print("extract_text_from_image test passed!")


async def test_compare_images():
    """Test the compare_images function."""
    with (
        patch.dict(os.environ, {"OPENROUTER_API_KEY": "test_key"}),
        patch(
            "mcp_openvision.server.encode_image_to_base64",
            return_value="base64_encoded",
        ),
        patch(
            "mcp_openvision.server.requests.post",
            return_value=mock_response,
        ),
    ):
        result = await compare_images(
            image1=mock_image,
            image2=mock_image,
            comparison_aspect="colors",
            model=VisionModel.CLAUDE_3_SONNET,
            ctx=mock_context,
        )

        print(f"compare_images result: {result}")
        assert result == "Test analysis result"
        mock_context.info.assert_called()
        print("compare_images test passed!")


async def run_tests():
    """Run all tests."""
    print("Starting functional tests...")
    await test_analyze_image()
    await test_extract_text_from_image()
    await test_compare_images()
    print("All tests passed!")


if __name__ == "__main__":
    asyncio.run(run_tests())
