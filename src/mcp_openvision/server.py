"""
OpenVision MCP Server

A simple MCP server that provides image analysis capabilities using OpenRouter.
"""

import base64
import json
import sys
import asyncio
import os
from pathlib import Path
import re
from typing import Dict, List, Optional, Any, Union
from urllib.parse import urlparse

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


def is_url(string: str) -> bool:
    """
    Check if the provided string is a URL.

    Args:
        string: The string to check

    Returns:
        True if the string is a URL, False otherwise
    """
    try:
        result = urlparse(string)
        return all([result.scheme, result.netloc])
    except ValueError:
        return False


def is_base64(string: str) -> bool:
    """
    Check if the provided string is base64-encoded.

    Args:
        string: The string to check

    Returns:
        True if the string appears to be base64-encoded, False otherwise
    """
    # Remove base64 URL prefix if present
    if string.startswith("data:image"):
        # Extract the actual base64 content
        pattern = r"base64,(.*)"
        match = re.search(pattern, string)
        if match:
            string = match.group(1)

    # Check if string is base64
    try:
        # Check if the string matches base64 pattern
        if not isinstance(string, str):
            return False

        # Check if the string follows base64 format (may have padding)
        # This regex allows for the standard base64 character set and optional padding
        if not re.match(r"^[A-Za-z0-9+/]*={0,2}$", string):
            return False

        # If it's too short, it's probably not base64
        if len(string) < 4:  # Minimum meaningful base64 is 4 chars
            return False

        # Try decoding - this will raise an exception if not valid base64
        decoded = base64.b64decode(string)
        # If we can decode it, it's likely base64
        return True
    except Exception:
        # If any exception occurs during decoding, it's not valid base64
        return False


def load_image_from_url(url: str) -> str:
    """
    Download an image from a URL and convert it to base64.

    Args:
        url: The URL of the image

    Returns:
        The image data as a base64-encoded string

    Raises:
        Exception: If the image cannot be downloaded
    """
    response = requests.get(url, stream=True)
    if response.status_code != 200:
        raise Exception(
            f"Failed to download image from URL: {url}, status code: {response.status_code}"
        )

    return encode_image_to_base64(response.content)


def load_image_from_path(path: str, project_root: Optional[str] = None) -> str:
    """
    Load an image from a local file path and convert it to base64.

    Args:
        path: The path to the image file
        project_root: Optional root directory to resolve relative paths against

    Returns:
        The image data as a base64-encoded string

    Raises:
        FileNotFoundError: If the image file does not exist
    """
    # Create a Path object from the input path
    file_path = Path(path)

    # If the path is absolute, use it directly
    if file_path.is_absolute():
        if not file_path.exists():
            raise FileNotFoundError(f"Image file not found at absolute path: {path}")
        with open(file_path, "rb") as f:
            return encode_image_to_base64(f.read())

    # For relative paths, we need to handle differently
    paths_to_try = [file_path]  # Always try the direct path first

    # If project_root is provided, try resolving against it
    if project_root:
        root_path = Path(project_root)
        if root_path.exists() and root_path.is_dir():
            paths_to_try.append(root_path / path)

    # Try each path
    for p in paths_to_try:
        if p.exists():
            with open(p, "rb") as f:
                return encode_image_to_base64(f.read())

    # If we get here, the file wasn't found
    if project_root:
        raise FileNotFoundError(
            f"Image file not found: {path} (tried directly and under project root: {project_root})"
        )
    else:
        raise FileNotFoundError(
            f"Image file not found: {path} (relative path used without specifying project_root)"
        )


def process_image_input(image: str, project_root: Optional[str] = None) -> str:
    """
    Process the image input, which can be a URL, file path, or base64-encoded data.

    Args:
        image: The image input as a URL, file path, or base64-encoded data
        project_root: Optional root directory to resolve relative paths against

    Returns:
        The image data as a base64-encoded string

    Raises:
        ValueError: If the image cannot be processed
    """
    # Check if the image is already base64-encoded
    if is_base64(image):
        return image

    # Check if the image is a URL
    if is_url(image):
        return load_image_from_url(image)

    # Check if the image is a file path
    try:
        return load_image_from_path(image, project_root)
    except FileNotFoundError as e:
        raise ValueError(
            f"Invalid image input: {str(e)}. "
            f"Image must be a base64-encoded string, a URL, or a valid file path."
        )


@mcp.tool()
async def image_analysis(
    image: str,
    query: str = "Describe this image in detail",
    system_prompt: str = "You are an expert vision analyzer with exceptional attention to detail. Your purpose is to provide accurate, comprehensive descriptions of images that help AI agents understand visual content they cannot directly perceive. Focus on describing all relevant elements in the image - objects, people, text, colors, spatial relationships, actions, and context. Be precise but concise, organizing information from most to least important. Avoid making assumptions beyond what's visible and clearly indicate any uncertainty. When text appears in images, transcribe it verbatim within quotes. Respond only with factual descriptions without subjective judgments or creative embellishments. Your descriptions should enable an agent to make informed decisions based solely on your analysis.",
    messages: Optional[List[Dict[str, Any]]] = None,
    model: Optional[str] = None,
    max_tokens: int = 4000,
    temperature: float = 0.7,
    top_p: Optional[float] = None,
    presence_penalty: Optional[float] = None,
    frequency_penalty: Optional[float] = None,
    project_root: Optional[str] = None,
) -> str:
    """
    Analyze an image using OpenRouter's vision capabilities.

    This tool allows you to send an image to OpenRouter's vision models for analysis.
    You can either provide a simple prompt or customize the full messages array for
    more control over the interaction.

    Args:
        image: The image as a base64-encoded string, URL, or local file path
        query: Text prompt to guide the image analysis (as user message)
        system_prompt: Instructions for the model defining its role and behavior
        messages: Optional custom messages array for the OpenRouter chat completions API
        model: The vision model to use (defaults to the value set by OPENROUTER_DEFAULT_MODEL)
        max_tokens: Maximum number of tokens in the response (100-4000)
        temperature: Temperature parameter for generation (0.0-1.0)
        top_p: Optional nucleus sampling parameter (0.0-1.0)
        presence_penalty: Optional penalty for new tokens based on presence in text so far (0.0-2.0)
        frequency_penalty: Optional penalty for new tokens based on frequency in text so far (0.0-2.0)
        project_root: Optional root directory to resolve relative image paths against

    Returns:
        The analysis result as text

    Examples:
        Basic usage with just a prompt and file path:
            image_analysis(image="path/to/image.jpg", query="Describe this image in detail")

        Basic usage with an image URL:
            image_analysis(image="https://example.com/image.jpg", query="Describe this image in detail")

        Basic usage with a relative path and project root:
            image_analysis(image="examples/image.jpg", project_root="/path/to/project", query="Describe this image in detail")

        Advanced usage with custom messages:
            image_analysis(
                image="path/to/image.jpg",
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

    if presence_penalty is not None and (
        presence_penalty < 0.0 or presence_penalty > 2.0
    ):
        raise ValueError("presence_penalty must be between 0.0 and 2.0")

    if frequency_penalty is not None and (
        frequency_penalty < 0.0 or frequency_penalty > 2.0
    ):
        raise ValueError("frequency_penalty must be between 0.0 and 2.0")

    # Process the image input (URL, file path, or base64)
    try:
        base64_image = process_image_input(image, project_root)
    except Exception as e:
        # Provide more helpful error message with examples
        error_msg = f"Failed to process image: {str(e)}\n\n"
        error_msg += "Make sure your image is specified correctly:\n"
        error_msg += "- For file paths, try providing the full absolute path\n"
        error_msg += "- For relative paths, specify the project_root parameter\n"
        error_msg += "- For URLs, ensure they are publicly accessible\n"
        error_msg += "- For base64, ensure the encoding is correct\n\n"
        error_msg += "Examples:\n"
        error_msg += 'image_analysis(image="/full/path/to/image.jpg", query="Describe this image")\n'
        error_msg += 'image_analysis(image="relative/path/image.jpg", project_root="/root/dir", query="What\'s in this image?")\n'
        error_msg += 'image_analysis(image="https://example.com/image.jpg", query="Analyze this image")'
        raise ValueError(error_msg)

    # If no model specified, use the default model from environment or fallback
    if model is None:
        selected_model = get_default_model()
        if isinstance(selected_model, VisionModel):
            model_value = selected_model.value
        else:
            # Handle custom model string
            model_value = selected_model
    else:
        # Allow any custom model string directly from the parameter
        model_value = model

    # Get API key
    try:
        api_key = get_api_key()
    except ConfigurationError as e:
        raise

    print(f"Processing image with model: {model_value}")

    # Prepare messages for the OpenRouter request
    if messages is None:
        # Create default messages with system and user role
        messages = [
            {"role": "system", "content": system_prompt},
            {
                "role": "user",
                "content": [
                    {"type": "text", "text": query},
                    {
                        "type": "image_url",
                        "image_url": {"url": f"data:image/jpeg;base64,{base64_image}"},
                    },
                ],
            },
        ]
    else:
        # Messages were provided - ensure the image is included
        image_added = False

        # Check if system message exists, add if not
        has_system_message = any(
            message.get("role") == "system" for message in messages
        )
        if not has_system_message:
            messages.insert(0, {"role": "system", "content": system_prompt})

        # Process each message
        for message in messages:
            if message.get("role") == "user":
                # Check if this message already has image content
                has_image = False
                if "content" in message and isinstance(message["content"], list):
                    for content_item in message["content"]:
                        if content_item.get("type") == "image_url":
                            # Replace any placeholder URLs with the actual image
                            if (
                                content_item.get("image_url", {}).get("url")
                                == "WILL_BE_REPLACED_WITH_IMAGE"
                            ):
                                content_item["image_url"][
                                    "url"
                                ] = f"data:image/jpeg;base64,{base64_image}"
                            has_image = True
                            image_added = True

                # If no image found, add it to the first user message
                if (
                    not has_image
                    and "content" in message
                    and isinstance(message["content"], list)
                ):
                    message["content"].append(
                        {
                            "type": "image_url",
                            "image_url": {
                                "url": f"data:image/jpeg;base64,{base64_image}"
                            },
                        }
                    )
                    image_added = True
                    break

        # If no user message with content list was found, add a new one with the image
        if not image_added:
            messages.append(
                {
                    "role": "user",
                    "content": [
                        {"type": "text", "text": query},
                        {
                            "type": "image_url",
                            "image_url": {
                                "url": f"data:image/jpeg;base64,{base64_image}"
                            },
                        },
                    ],
                }
            )

    # Prepare OpenRouter request
    headers = {
        "Authorization": f"Bearer {api_key}",
        "Content-Type": "application/json",
        "HTTP-Referer": "https://github.com/modelcontextprotocol/mcp-openvision",
        "X-Title": "MCP OpenVision",
    }

    # Start with required parameters
    payload = {
        "model": model_value,
        "messages": messages,
        "max_tokens": max_tokens,
        "temperature": temperature,
    }

    # Add optional parameters if provided
    if top_p is not None:
        payload["top_p"] = top_p

    if presence_penalty is not None:
        payload["presence_penalty"] = presence_penalty

    if frequency_penalty is not None:
        payload["frequency_penalty"] = frequency_penalty

    print("Sending request to OpenRouter...")

    try:
        # Make the API call
        response = requests.post(
            "https://openrouter.ai/api/v1/chat/completions",
            headers=headers,
            json=payload,
        )

        # Check for errors
        if response.status_code != 200:
            error_msg = (
                f"Error from OpenRouter: {response.status_code} - {response.text}"
            )
            print(error_msg)
            raise OpenRouterError(response.status_code, response.text)

        # Parse the response
        result = response.json()
        analysis = result["choices"][0]["message"]["content"]

        print("Analysis completed successfully")

        return analysis

    except requests.RequestException as e:
        error_msg = f"Network error when connecting to OpenRouter: {str(e)}"
        print(error_msg)
        raise OpenRouterError(0, error_msg)
    except json.JSONDecodeError as e:
        error_msg = f"Error parsing OpenRouter response: {str(e)}"
        print(error_msg)
        raise OpenRouterError(0, error_msg)


def main():
    """Run the MCP server."""
    if sys.platform == "win32":
        asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())

    mcp.run()
