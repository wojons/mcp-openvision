"""
Configuration management for the OpenVision MCP server.
"""

import os
from enum import Enum
from typing import Optional

from .exceptions import ConfigurationError


class VisionModel(str, Enum):
    """Available vision models from OpenRouter."""

    CLAUDE_3_5_SONNET = "anthropic/claude-3-5-sonnet"
    CLAUDE_3_OPUS = "anthropic/claude-3-opus"
    CLAUDE_3_SONNET = "anthropic/claude-3-sonnet"
    GPT_4O = "openai/gpt-4o"
    QWEN_QWQ_32B = "qwen/qwq-32b:free"
    QWEN_2_5_VL = "qwen/qwen2.5-vl-32b-instruct:free"


def get_api_key() -> str:
    """
    Get the OpenRouter API key from environment variables.

    Returns:
        The API key as a string

    Raises:
        ConfigurationError: If the API key is not set
    """
    api_key = os.environ.get("OPENROUTER_API_KEY")
    if not api_key:
        raise ConfigurationError(
            "OPENROUTER_API_KEY environment variable not set. "
            "Please set it to your OpenRouter API key."
        )
    return api_key


def get_default_model() -> VisionModel:
    """
    Get the default vision model from environment variables or use Qwen 2.5 VL as fallback.

    Returns:
        The default VisionModel to use
    """
    default_model = os.environ.get("OPENROUTER_DEFAULT_MODEL")
    if default_model:
        # Try to match the environment variable to a VisionModel enum value
        for model in VisionModel:
            if model.value == default_model:
                return model

        # If we didn't find a match, log a warning and use the fallback
        print(
            f"Warning: OPENROUTER_DEFAULT_MODEL '{default_model}' is not recognized. "
            f"Using qwen/qwen2.5-vl-32b-instruct:free as default."
        )

    # Return the fallback model (QWEN_2_5_VL)
    return VisionModel.QWEN_2_5_VL
