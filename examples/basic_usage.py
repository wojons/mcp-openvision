"""
Example showing basic usage of the MCP OpenVision server.

This script demonstrates how to use the MCP OpenVision server from Python.
"""

import os
import sys
from pathlib import Path

# Add the src directory to sys.path to import the package
src_dir = Path(__file__).parent.parent / "src"
sys.path.append(str(src_dir))

from mcp_openvision.server import (
    analyze_image,
    compare_images,
    extract_text_from_image,
    AnalysisMode,
    VisionModel,
)
from fastmcp import Image

# Set your OpenRouter API key
os.environ["OPENROUTER_API_KEY"] = "your_api_key_here"  # Replace with your actual key


async def main():
    """Run example usage of the MCP server."""
    print("MCP OpenVision Example")
    print("======================")
    
    # Example 1: Basic image analysis
    image_path = "./examples/test_image.jpg"  # Replace with your test image
    
    print("\nExample 1: Basic Image Analysis")
    print("---------------------------------")
    try:
        result = await analyze_image(
            image=Image(path=image_path),
            prompt="What's in this image?",
            model=VisionModel.CLAUDE_3_SONNET,
        )
        print(result)
    except Exception as e:
        print(f"Error: {e}")
    
    # Example 2: Text extraction
    print("\nExample 2: Text Extraction")
    print("---------------------------")
    try:
        result = await extract_text_from_image(
            image=Image(path=image_path),
            language="English",  # Optional
        )
        print(result)
    except Exception as e:
        print(f"Error: {e}")
    
    # Example 3: Image comparison
    print("\nExample 3: Image Comparison")
    print("----------------------------")
    try:
        image_path2 = "./examples/test_image2.jpg"  # Replace with your second test image
        result = await compare_images(
            image1=Image(path=image_path),
            image2=Image(path=image_path2),
            comparison_aspect="colors and objects",
        )
        print(result)
    except Exception as e:
        print(f"Error: {e}")


if __name__ == "__main__":
    import asyncio
    asyncio.run(main()) 