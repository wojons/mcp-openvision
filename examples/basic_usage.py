#!/usr/bin/env python
"""
Basic example of using the OpenVision MCP server.

This example shows how to:
1. Connect to the server
2. List available tools
3. Call the image_analysis tool with a simple prompt
"""

import asyncio
import os
from pathlib import Path

from mcp import ClientSession, StdioServerParameters
from mcp.client.stdio import stdio_client


async def main():
    # Set up the server parameters
    server_params = StdioServerParameters(
        command="python",
        args=["-m", "mcp_openvision"],
        env={
            # You can set environment variables here
            "OPENROUTER_API_KEY": os.environ.get("OPENROUTER_API_KEY"),
            "OPENROUTER_DEFAULT_MODEL": "qwen/qwq-32b:free",  # Optional: set default model
        }
    )
    
    print("Connecting to OpenVision MCP server...")
    
    # Connect to the server
    async with stdio_client(server_params) as (read_stream, write_stream):
        async with ClientSession(read_stream, write_stream) as session:
            # Initialize the connection
            await session.initialize()
            
            # List available tools
            tools_response = await session.list_tools()
            print(f"Available tools: {[tool.name for tool in tools_response.tools]}")
            
            # Read an image file
            image_path = Path(__file__).parent / "sample_image.jpg"
            
            if not image_path.exists():
                print(f"Error: Sample image not found at {image_path}")
                print("Please add a sample image named 'sample_image.jpg' to the examples directory.")
                return
            
            with open(image_path, "rb") as f:
                image_data = f.read()
            
            print("\nAnalyzing image with basic prompt...")
            
            # Call the image_analysis tool with a simple prompt
            result = await session.call_tool(
                "image_analysis", 
                {
                    "image": {"data": image_data},
                    "prompt": "What's in this image?"
                }
            )
            
            print(f"\nResult:\n{result.content}")
            
            # Example with custom messages
            print("\nAnalyzing image with custom messages...")
            
            result = await session.call_tool(
                "image_analysis", 
                {
                    "image": {"data": image_data},
                    "messages": [
                        {"role": "system", "content": "You are a helpful assistant focused on analyzing images."},
                        {
                            "role": "user", 
                            "content": [
                                {"type": "text", "text": "Identify all colors present in this image"},
                                {"type": "image_url", "image_url": {"url": "WILL_BE_REPLACED_WITH_IMAGE"}}
                            ]
                        }
                    ]
                }
            )
            
            print(f"\nResult with custom messages:\n{result.content}")
            
            # Example with relative path and project_root
            print("\nAnalyzing image using a relative path with project_root...")
            
            # Get the current working directory to use as a project_root example
            project_root = os.getcwd()
            
            # Call the image_analysis tool with a relative path and project_root
            try:
                result = await session.call_tool(
                    "image_analysis", 
                    {
                        "image": "examples/test_image.png",  # Relative path from project root
                        "project_root": project_root,  # Set the project root directory
                        "prompt": "What can you see in this image?"
                    }
                )
                print(f"\nResult with relative path and project_root:\n{result.content}")
            except Exception as e:
                print(f"\nError using relative path: {str(e)}")
                print("Make sure you have a file at 'examples/test_image.png' relative to the current directory.")
                
            print("\nDone!")


if __name__ == "__main__":
    # Run the async main function
    asyncio.run(main()) 