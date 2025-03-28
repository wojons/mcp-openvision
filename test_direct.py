"""
Direct test of the OpenVision functions, bypassing the MCP tools.

This avoids the JSON schema generation issue by importing the module code
and calling the functions directly without the fastmcp tool decorators.
"""

import asyncio
import importlib.util
import inspect
import os
import sys
from pathlib import Path
from unittest.mock import AsyncMock, MagicMock, patch

# Add the src directory to sys.path to import the package
src_dir = Path(__file__).parent / "src"
sys.path.append(str(src_dir))

# Mock Image class
class MockImage:
    def __init__(self, data=None, path=None, format=None):
        self.data = data or b"fake_image_data"
        self.path = path
        self._format = format or "jpeg"

# Load the server.py file without executing the decorators
spec = importlib.util.spec_from_file_location(
    "server_source", Path(__file__).parent / "src" / "mcp_openvision" / "server.py"
)
server_source = importlib.util.module_from_spec(spec)

# Keep reference to original decorator
original_decorator = None

# Mock the decorator to avoid schema generation
def mock_tool_decorator():
    def decorator(fn):
        return fn
    return decorator

# Mock the FastMCP class
class MockFastMCP:
    def __init__(self, *args, **kwargs):
        pass
    
    def tool(self):
        return mock_tool_decorator()
    
    def prompt(self):
        return mock_tool_decorator()
    
    def run(self):
        pass

# Patch key imports before loading the module
with patch("fastmcp.FastMCP", MockFastMCP), patch("fastmcp.Image", MockImage), patch("fastmcp.Context", MagicMock):
    spec.loader.exec_module(server_source)

# Now extract the functions we need
analyze_image = server_source.analyze_image
extract_text_from_image = server_source.extract_text_from_image
compare_images = server_source.compare_images
AnalysisMode = server_source.AnalysisMode
VisionModel = server_source.VisionModel

# Create test objects
mock_image = MockImage(data=b"fake_image_data")
mock_context = MagicMock()
mock_context.info = MagicMock()
mock_context.error = MagicMock()
mock_response = MagicMock()
mock_response.status_code = 200
mock_response.json.return_value = {
    "choices": [{"message": {"content": "Test analysis result"}}]
}


async def test_analyze_image():
    """Test the analyze_image function directly."""
    with (
        patch.dict(os.environ, {"OPENROUTER_API_KEY": "test_key"}),
        patch(
            "requests.post",
            return_value=mock_response,
        ),
    ):
        # Mock encode_image_to_base64 directly in the server_source module
        server_source.encode_image_to_base64 = lambda data: "base64_encoded"
        
        result = await analyze_image(
            image=mock_image,
            prompt="Test prompt",
            model=VisionModel.CLAUDE_3_SONNET,
            mode=AnalysisMode.GENERAL,
            ctx=mock_context,
        )

        print(f"analyze_image result: {result}")
        assert result == "Test analysis result"
        print("analyze_image test passed!")


async def test_extract_text_from_image():
    """Test the extract_text_from_image function directly."""
    # Temporarily replace analyze_image with a simple mock in the module
    original_analyze = server_source.analyze_image
    server_source.analyze_image = AsyncMock(return_value="Extracted text")
    
    try:
        result = await extract_text_from_image(
            image=mock_image,
            language="English",
            model=VisionModel.CLAUDE_3_SONNET,
            ctx=mock_context,
        )

        print(f"extract_text_from_image result: {result}")
        assert result == "Extracted text"
        print("extract_text_from_image test passed!")
    finally:
        # Restore the original function
        server_source.analyze_image = original_analyze


async def test_compare_images():
    """Test the compare_images function directly."""
    with (
        patch.dict(os.environ, {"OPENROUTER_API_KEY": "test_key"}),
        patch(
            "requests.post",
            return_value=mock_response,
        ),
    ):
        # Mock encode_image_to_base64 directly in the server_source module
        server_source.encode_image_to_base64 = lambda data: "base64_encoded"
        
        result = await compare_images(
            image1=mock_image,
            image2=mock_image,
            comparison_aspect="colors",
            model=VisionModel.CLAUDE_3_SONNET,
            ctx=mock_context,
        )

        print(f"compare_images result: {result}")
        assert result == "Test analysis result"
        print("compare_images test passed!")


async def run_tests():
    """Run all tests."""
    print("\nStarting direct function tests...\n")
    await test_analyze_image()
    await test_extract_text_from_image()
    await test_compare_images()
    print("\nAll tests passed!")


if __name__ == "__main__":
    asyncio.run(run_tests()) 