"""
OpenVision MCP Server

A simple MCP server that provides image analysis capabilities using OpenRouter.
"""

import base64
import io
import json
import os
from enum import Enum
from typing import Annotated, List, Literal, Optional, Union

import requests
from fastmcp import Context, FastMCP, Image

# Initialize FastMCP with dependencies
mcp = FastMCP(
    "OpenVision",
    description="Vision analysis tool for images using OpenRouter",
    dependencies=["openai", "pillow", "requests"],
)


class AnalysisMode(str, Enum):
    """Predefined analysis modes for specific use cases."""

    GENERAL = "general"
    DETAILED = "detailed"
    TEXT_EXTRACTION = "text_extraction"
    TECHNICAL = "technical"
    SOCIAL_MEDIA = "social_media"


class VisionModel(str, Enum):
    """Available vision models from OpenRouter."""

    CLAUDE_3_5_SONNET = "anthropic/claude-3-5-sonnet"
    CLAUDE_3_OPUS = "anthropic/claude-3-opus"
    CLAUDE_3_SONNET = "anthropic/claude-3-sonnet"
    GPT_4O = "openai/gpt-4o"
    QWEN_QWQ_32B = "qwen/qwq-32b:free"


def get_default_model() -> VisionModel:
    """Get the default vision model from environment variables or use Qwen QWQ-32B as fallback."""
    default_model = os.environ.get("OPENROUTER_DEFAULT_MODEL")
    if default_model:
        # Try to match the environment variable to a VisionModel enum value
        for model in VisionModel:
            if model.value == default_model:
                return model
        # If provided value doesn't match any enum, add a custom model
        try:
            # Add the custom model to the enum dynamically
            VisionModel(default_model)  # This will raise ValueError if not valid
            return VisionModel(default_model)
        except ValueError:
            print(
                f"Warning: OPENROUTER_DEFAULT_MODEL '{default_model}' is not recognized. Using qwen/qwq-32b:free as default."
            )

    # Return qwen/qwq-32b:free as the default model if no env var or not valid
    # First check if it's in existing enum values
    for model in VisionModel:
        if model.value == "qwen/qwq-32b:free":
            return model

    # If not in enum, add it dynamically
    try:
        VisionModel("qwen/qwq-32b:free")
        return VisionModel("qwen/qwq-32b:free")
    except ValueError:
        # Fallback to Claude 3 Sonnet if something goes wrong
        print(
            "Warning: Could not set qwen/qwq-32b:free as default. Using Claude 3 Sonnet instead."
        )
        return VisionModel.CLAUDE_3_SONNET


def get_openrouter_api_key() -> str:
    """Get the OpenRouter API key from environment variables."""
    api_key = os.environ.get("OPENROUTER_API_KEY")
    if not api_key:
        raise ValueError(
            "OPENROUTER_API_KEY environment variable not set. "
            "Please set it to your OpenRouter API key."
        )
    return api_key


def encode_image_to_base64(image_data: bytes) -> str:
    """Encode image data to base64."""
    return base64.b64encode(image_data).decode("utf-8")


@mcp.tool()
async def analyze_image(
    image: Image,
    prompt: str = "Analyze this image in detail",
    model: VisionModel = None,  # Changed to None default, will use get_default_model() below
    mode: AnalysisMode = AnalysisMode.GENERAL,
    max_tokens: int = 1000,  # Removed Field, using simple type annotation
    temperature: float = 0.7,  # Removed Field, using simple type annotation
    ctx: Context = None,
) -> str:
    """
    Analyze an image using OpenRouter's vision capabilities.

    Args:
        image: The image to analyze (local file or URL)
        prompt: The analysis prompt to use
        model: The vision model to use (defaults to OPENROUTER_DEFAULT_MODEL env var or Claude 3 Sonnet)
        mode: Predefined analysis mode for specific use cases
        max_tokens: Maximum number of tokens in the response (100-4000)
        temperature: Temperature parameter for generation (0.0-1.0)
        ctx: MCP context

    Returns:
        The analysis result as text
    """
    # Validate parameter constraints manually
    if max_tokens < 100 or max_tokens > 4000:
        raise ValueError("max_tokens must be between 100 and 4000")
    
    if temperature < 0.0 or temperature > 1.0:
        raise ValueError("temperature must be between 0.0 and 1.0")
        
    # If no model specified, use the default model from environment or fallback
    if model is None:
        model = get_default_model()

    # If using a predefined mode, adjust the prompt
    if mode == AnalysisMode.DETAILED:
        prompt = f"Provide an extremely detailed description of this image. {prompt}"
    elif mode == AnalysisMode.TEXT_EXTRACTION:
        prompt = f"Extract and transcribe all text from this image. {prompt}"
    elif mode == AnalysisMode.TECHNICAL:
        prompt = f"Provide a technical analysis of this image, focusing on technical aspects, measurements, specifications, and any technical data visible. {prompt}"
    elif mode == AnalysisMode.SOCIAL_MEDIA:
        prompt = f"Analyze this image as if it were a social media post. What platform might it be from? What type of content is it? Is it likely to be popular? {prompt}"

    # Get API key
    api_key = get_openrouter_api_key()

    if ctx:
        ctx.info(f"Processing image with model: {model.value}")
        ctx.info(f"Analysis mode: {mode}")

    # Encode image to base64
    base64_image = encode_image_to_base64(image.data)

    # Prepare OpenRouter request
    headers = {
        "Authorization": f"Bearer {api_key}",
        "Content-Type": "application/json",
    }

    payload = {
        "model": model.value,
        "messages": [
            {
                "role": "user",
                "content": [
                    {"type": "text", "text": prompt},
                    {
                        "type": "image_url",
                        "image_url": {"url": f"data:image/jpeg;base64,{base64_image}"},
                    },
                ],
            }
        ],
        "max_tokens": max_tokens,
        "temperature": temperature,
    }

    if ctx:
        ctx.info("Sending request to OpenRouter...")

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
            ctx.error(error_msg)
        raise Exception(error_msg)

    # Parse the response
    result = response.json()
    analysis = result["choices"][0]["message"]["content"]

    if ctx:
        ctx.info("Analysis completed successfully")

    return analysis


@mcp.tool()
async def extract_text_from_image(
    image: Image,
    language: Optional[str] = None,
    model: VisionModel = None,  # Changed to None default
    ctx: Context = None,
) -> str:
    """
    Extract text from an image using OpenRouter's vision capabilities.

    Args:
        image: The image containing text to extract
        language: Optional language hint for better extraction
        model: The vision model to use (defaults to OPENROUTER_DEFAULT_MODEL env var or Claude 3 Sonnet)
        ctx: MCP context

    Returns:
        The extracted text
    """
    prompt = "Extract and transcribe all text visible in this image. Output only the text, formatted properly."

    if language:
        prompt += f" The text is in {language}."

    if ctx:
        ctx.info(
            f"Extracting text from image using model: {model.value if model else get_default_model().value}"
        )
        if language:
            ctx.info(f"Language hint: {language}")

    # Use the analyze_image tool with text extraction settings
    return await analyze_image(
        image=image,
        prompt=prompt,
        model=model,
        mode=AnalysisMode.TEXT_EXTRACTION,
        max_tokens=2000,
        temperature=0.3,
        ctx=ctx,
    )


@mcp.tool()
async def compare_images(
    image1: Image,
    image2: Image,
    comparison_aspect: Optional[str] = None,
    model: VisionModel = None,  # Changed to None default
    max_tokens: int = 1500,  # Removed Field, using simple type annotation
    ctx: Context = None,
) -> str:
    """
    Compare two images and analyze their differences or similarities.

    Args:
        image1: The first image to compare
        image2: The second image to compare
        comparison_aspect: Optional specific aspect to focus on (e.g., "colors", "objects", "composition")
        model: The vision model to use (defaults to OPENROUTER_DEFAULT_MODEL env var or Claude 3 Sonnet)
        max_tokens: Maximum number of tokens in the response (100-4000)
        ctx: MCP context

    Returns:
        Comparison analysis text
    """
    # Validate parameter constraints manually
    if max_tokens < 100 or max_tokens > 4000:
        raise ValueError("max_tokens must be between 100 and 4000")
        
    # If no model specified, use the default model from environment or fallback
    if model is None:
        model = get_default_model()

    # Build the prompt based on the comparison aspect
    prompt = "Compare these two images and describe the differences and similarities"
    if comparison_aspect:
        prompt += f", focusing specifically on the {comparison_aspect} aspect"
    prompt += "."

    # Get API key
    api_key = get_openrouter_api_key()

    if ctx:
        ctx.info(f"Comparing images with model: {model.value}")
        if comparison_aspect:
            ctx.info(f"Focusing on aspect: {comparison_aspect}")

    # Encode images to base64
    base64_image1 = encode_image_to_base64(image1.data)
    base64_image2 = encode_image_to_base64(image2.data)

    # Prepare OpenRouter request
    headers = {
        "Authorization": f"Bearer {api_key}",
        "Content-Type": "application/json",
    }

    payload = {
        "model": model.value,
        "messages": [
            {
                "role": "user",
                "content": [
                    {"type": "text", "text": prompt},
                    {
                        "type": "image_url",
                        "image_url": {"url": f"data:image/jpeg;base64,{base64_image1}"},
                    },
                    {
                        "type": "image_url",
                        "image_url": {"url": f"data:image/jpeg;base64,{base64_image2}"},
                    },
                ],
            }
        ],
        "max_tokens": max_tokens,
        "temperature": 0.7,  # Using a moderate temperature for comparison
    }

    if ctx:
        ctx.info("Sending request to OpenRouter...")

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
            ctx.error(error_msg)
        raise Exception(error_msg)

    # Parse the response
    result = response.json()
    comparison = result["choices"][0]["message"]["content"]

    if ctx:
        ctx.info("Comparison completed successfully")

    return comparison


@mcp.prompt()
def analyze_screenshot(task: str = "Analyze this screenshot") -> str:
    """
    Prompt for analyzing a screenshot with detailed context.

    Args:
        task: The specific task or question about the screenshot

    Returns:
        A prompt template for screenshot analysis
    """
    return f"""
    {task}
    
    Please provide a comprehensive analysis of this screenshot including:
    1. What type of application/website is shown
    2. The main elements and layout of the interface
    3. Any notable text content
    4. Key UI components (buttons, forms, navigation, etc.)
    5. What the user might be trying to accomplish
    
    Be as detailed as possible in your analysis.
    """


@mcp.prompt()
def extract_chart_data(chart_type: Optional[str] = None) -> str:
    """
    Prompt for extracting data from charts and visualizations.

    Args:
        chart_type: Optional hint about the chart type (pie, bar, line, etc.)

    Returns:
        A prompt template for chart data extraction
    """
    base_prompt = "Please analyze this chart and extract the data represented in it."

    if chart_type:
        return f"""
        {base_prompt}
        
        This appears to be a {chart_type} chart. Please:
        1. Identify the title and axis labels
        2. List all data points or series shown
        3. Explain what trends or patterns are visible
        4. Provide a numerical table representation of the data if possible
        5. Note any anomalies or outliers
        """
    else:
        return f"""
        {base_prompt}
        
        Please:
        1. Identify what type of chart or visualization this is
        2. Identify the title and axis labels
        3. List all data points or series shown
        4. Explain what trends or patterns are visible
        5. Provide a numerical table representation of the data if possible
        6. Note any anomalies or outliers
        """


def main():
    """Run the MCP server."""
    mcp.run()


# Run the server if executed directly
if __name__ == "__main__":
    main()
