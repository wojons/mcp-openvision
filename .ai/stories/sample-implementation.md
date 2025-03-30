# Sample Implementation of Simplified OpenVision MCP Server

This file shows a sample implementation of the simplified MCP OpenVision server with just the image_analysis tool.

## Configuration Module (`config.py`)

```python
"""
Configuration management for the OpenVision MCP server.
"""

import os
from enum import Enum
from typing import Optional

class VisionModel(str, Enum):
    """Available vision models from OpenRouter."""
    CLAUDE_3_5_SONNET = "anthropic/claude-3-5-sonnet"
    CLAUDE_3_OPUS = "anthropic/claude-3-opus"
    CLAUDE_3_SONNET = "anthropic/claude-3-sonnet"
    GPT_4O = "openai/gpt-4o"
    QWEN_QWQ_32B = "qwen/qwq-32b:free"

class ConfigurationError(Exception):
    """Error in server configuration."""
    pass

def get_api_key() -> str:
    """Get the OpenRouter API key from environment variables."""
    api_key = os.environ.get("OPENROUTER_API_KEY")
    if not api_key:
        raise ConfigurationError(
            "OPENROUTER_API_KEY environment variable not set. "
            "Please set it to your OpenRouter API key."
        )
    return api_key

def get_default_model() -> VisionModel:
    """Get the default vision model from environment variables or use Qwen QWQ-32B as fallback."""
    default_model = os.environ.get("OPENROUTER_DEFAULT_MODEL")
    if default_model:
        # Try to match the environment variable to a VisionModel enum value
        for model in VisionModel:
            if model.value == default_model:
                return model

        # If we didn't find a match, log a warning and use the fallback
        print(
            f"Warning: OPENROUTER_DEFAULT_MODEL '{default_model}' is not recognized. "
            f"Using qwen/qwq-32b:free as default."
        )

    # Return the fallback model (QWEN_QWQ_32B)
    return VisionModel.QWEN_QWQ_32B
```

## Exceptions Module (`exceptions.py`)

```python
"""
Exception classes for the OpenVision MCP server.
"""

class OpenVisionError(Exception):
    """Base exception for OpenVision MCP server."""
    pass

class ConfigurationError(OpenVisionError):
    """Error in server configuration."""
    pass

class OpenRouterError(OpenVisionError):
    """Error from the OpenRouter API."""

    def __init__(self, status_code: int, message: str):
        self.status_code = status_code
        self.message = message
        super().__init__(f"OpenRouter API error (status {status_code}): {message}")
```

## Simplified Server Module (`server.py`)

```python
"""
OpenVision MCP Server

A simple MCP server that provides image analysis capabilities using OpenRouter.
"""

import base64
import json
from typing import Annotated, Dict, List, Optional, Union

import requests
from mcp.server.fastmcp import FastMCP
from mcp import types

from .config import VisionModel, get_api_key, get_default_model
from .exceptions import OpenRouterError, ConfigurationError

# Initialize FastMCP with dependencies
mcp = FastMCP(
    "OpenVision",
    description="Vision analysis tool for images using OpenRouter",
)

def encode_image_to_base64(image_data: bytes) -> str:
    """Encode image data to base64."""
    return base64.b64encode(image_data).decode("utf-8")

@mcp.tool()
async def image_analysis(
    image: types.BinaryData,
    query: Optional[str] = None,
    system_prompt: str = "You are an expert vision analyzer with exceptional attention to detail. Your purpose is to provide accurate, comprehensive descriptions of images that help AI agents understand visual content they cannot directly perceive. Focus on describing all relevant elements in the image - objects, people, text, colors, spatial relationships, actions, and context. Be precise but concise, organizing information from most to least important. Avoid making assumptions beyond what's visible and clearly indicate any uncertainty. When text appears in images, transcribe it verbatim within quotes. Respond only with factual descriptions without subjective judgments or creative embellishments. Your descriptions should enable an agent to make informed decisions based solely on your analysis.",
    messages: Optional[List[Dict]] = None,
    model: Optional[VisionModel] = None,
    max_tokens: int = 4000,
    temperature: float = 0.7,
    top_p: Optional[float] = None,
    ctx: types.Context = None,
) -> str:
    """
    Analyze an image using OpenRouter's vision capabilities.

    This tool allows you to send an image to OpenRouter's vision models for analysis.
    You can either provide a simple prompt or customize the full messages array for
    more control over the interaction.

    Args:
        image: The image to analyze (binary data)
        query: A simple text prompt for the analysis (ignored if messages is provided)
        system_prompt: Instructions for the model defining its role and behavior
        messages: Optional custom messages array for the OpenRouter chat completions API
        model: The vision model to use (defaults to the value set by OPENROUTER_DEFAULT_MODEL)
        max_tokens: Maximum number of tokens in the response (100-4000)
        temperature: Temperature parameter for generation (0.0-1.0)
        top_p: Optional nucleus sampling parameter (0.0-1.0)
        ctx: MCP context

    Returns:
        The analysis result as text

    Examples:
        Basic usage with just a prompt:
            image_analysis(image=my_image, query="Describe this image in detail")

        Advanced usage with custom messages:
            image_analysis(
                image=my_image,
                messages=[
                    {
                        "role": "user",
                        "content": [
                            {"type": "text", "text": "What objects can you see in this image?"},
                            {"type": "image_url", "image_url": {"url": "WILL_BE_REPLACED_WITH_IMAGE"}}
                        ]
                    }
                ]
            )
    """
    # Validate parameter constraints
    if max_tokens < 100 or max_tokens > 4000:
        raise ValueError("max_tokens must be between 100 and 4000")

    if temperature < 0.0 or temperature > 1.0:
        raise ValueError("temperature must be between 0.0 and 1.0")

    if top_p is not None and (top_p < 0.0 or top_p > 1.0):
        raise ValueError("top_p must be between 0.0 and 1.0")

    # If no model specified, use the default model from environment or fallback
    if model is None:
        model = get_default_model()

    # Get API key
    try:
        api_key = get_api_key()
    except ConfigurationError as e:
        if ctx:
            ctx.log_error(str(e))
        raise

    if ctx:
        ctx.log_info(f"Processing image with model: {model.value}")

    # Encode image to base64
    base64_image = encode_image_to_base64(image.data)

    # Prepare messages for the OpenRouter request
    if messages is None:
        # Create default messages from prompt
        default_query = query or "Analyze this image in detail"
        messages = [
            {
                "role": "system",
                "content": system_prompt
            },
            {
                "role": "user",
                "content": [
                    {"type": "text", "text": default_query},
                    {
                        "type": "image_url",
                        "image_url": {"url": f"data:image/jpeg;base64,{base64_image}"},
                    },
                ],
            }
        ]
    else:
        # Messages were provided - ensure the image is included
        # This is a simplified version - production code would need more robust handling
        # Find the first user message
        for message in messages:
            if message.get("role") == "user":
                # Check if this message already has image content
                has_image = False
                if "content" in message and isinstance(message["content"], list):
                    for content_item in message["content"]:
                        if content_item.get("type") == "image_url":
                            # Replace any placeholder URLs with the actual image
                            if content_item.get("image_url", {}).get("url") == "WILL_BE_REPLACED_WITH_IMAGE":
                                content_item["image_url"]["url"] = f"data:image/jpeg;base64,{base64_image}"
                            has_image = True

                # If no image found, add it to the first user message
                if not has_image and "content" in message and isinstance(message["content"], list):
                    message["content"].append({
                        "type": "image_url",
                        "image_url": {"url": f"data:image/jpeg;base64,{base64_image}"},
                    })
                break

    # Prepare OpenRouter request
    headers = {
        "Authorization": f"Bearer {api_key}",
        "Content-Type": "application/json",
    }

    payload = {
        "model": model.value,
        "messages": messages,
        "max_tokens": max_tokens,
        "temperature": temperature,
    }

    # Add optional parameters if provided
    if top_p is not None:
        payload["top_p"] = top_p

    if ctx:
        ctx.log_info("Sending request to OpenRouter...")

    try:
        # Make the API call
        response = requests.post(
            "https://openrouter.ai/api/v1/chat/completions",
            headers=headers,
            json=payload,
        )

        # Check for errors
        if response.status_code != 200:
            error_msg = f"Error from OpenRouter: {response.status_code} - {response.text}"
            if ctx:
                ctx.log_error(error_msg)
            raise OpenRouterError(response.status_code, response.text)

        # Parse the response
        result = response.json()
        analysis = result["choices"][0]["message"]["content"]

        if ctx:
            ctx.log_info("Analysis completed successfully")

        return analysis

    except requests.RequestException as e:
        error_msg = f"Network error when connecting to OpenRouter: {str(e)}"
        if ctx:
            ctx.log_error(error_msg)
        raise OpenRouterError(0, error_msg)
    except json.JSONDecodeError as e:
        error_msg = f"Error parsing OpenRouter response: {str(e)}"
        if ctx:
            ctx.log_error(error_msg)
        raise OpenRouterError(0, error_msg)


def main():
    """Run the MCP server."""
    import sys
    import asyncio
    from mcp.server.stdio import stdio_server

    async def run_server():
        async with stdio_server() as (read, write):
            await mcp.run(read, write)

    if sys.platform == "win32":
        asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())

    asyncio.run(run_server())


if __name__ == "__main__":
    main()
```

## Example Usage

```python
# Example MCP client usage

from mcp import ClientSession, StdioServerParameters
from mcp.client.stdio import stdio_client
import asyncio

async def main():
    # Connect to the MCP server
    server_params = StdioServerParameters(
        command="python",
        args=["-m", "mcp_openvision"],
        env={"OPENROUTER_API_KEY": "your_api_key_here"}
    )

    async with stdio_client(server_params) as (read_stream, write_stream):
        async with ClientSession(read_stream, write_stream) as session:
            # Initialize the connection
            await session.initialize()

            # List available tools
            tools = await session.list_tools()
            print(f"Available tools: {[tool.name for tool in tools.tools]}")

            # Call the image_analysis tool
            with open("example.jpg", "rb") as f:
                image_data = f.read()

            result = await session.call_tool(
                "image_analysis",
                {
                    "image": {"data": image_data},
                    "query": "What objects can you see in this image?"
                }
            )

            print(f"Result: {result.content}")

if __name__ == "__main__":
    asyncio.run(main())
```
