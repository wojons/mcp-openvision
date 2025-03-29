"""Tests for the configuration module."""

import os
import pytest
from mcp_openvision.config import get_api_key, get_default_model, VisionModel
from mcp_openvision.exceptions import ConfigurationError


@pytest.fixture
def clear_env_vars():
    """Remove environment variables before tests and restore after."""
    # Save original values
    original_api_key = os.environ.get("OPENROUTER_API_KEY")
    original_model = os.environ.get("OPENROUTER_DEFAULT_MODEL")

    # Clear environment variables
    if "OPENROUTER_API_KEY" in os.environ:
        del os.environ["OPENROUTER_API_KEY"]
    if "OPENROUTER_DEFAULT_MODEL" in os.environ:
        del os.environ["OPENROUTER_DEFAULT_MODEL"]

    yield

    # Restore original values
    if original_api_key:
        os.environ["OPENROUTER_API_KEY"] = original_api_key
    elif "OPENROUTER_API_KEY" in os.environ:
        del os.environ["OPENROUTER_API_KEY"]

    if original_model:
        os.environ["OPENROUTER_DEFAULT_MODEL"] = original_model
    elif "OPENROUTER_DEFAULT_MODEL" in os.environ:
        del os.environ["OPENROUTER_DEFAULT_MODEL"]


def test_get_api_key_from_env():
    """Test retrieving API key from environment variable."""
    # Set environment variable
    os.environ["OPENROUTER_API_KEY"] = "test_api_key"

    # Get the API key
    api_key = get_api_key()

    # Check the result
    assert api_key == "test_api_key"


def test_get_api_key_missing(clear_env_vars):
    """Test behavior when API key is missing."""
    # Ensure environment variable is not set
    assert "OPENROUTER_API_KEY" not in os.environ

    # Attempt to get the API key, should raise ConfigurationError
    with pytest.raises(ConfigurationError) as excinfo:
        get_api_key()

    # Check the error message
    assert "OPENROUTER_API_KEY environment variable not set" in str(excinfo.value)


def test_get_default_model_from_env():
    """Test retrieving default model from environment variable."""
    # Set environment variable to a valid model value
    valid_model = VisionModel.CLAUDE_3_SONNET.value
    os.environ["OPENROUTER_DEFAULT_MODEL"] = valid_model

    # Get the default model
    model = get_default_model()

    # Check the result
    assert model == VisionModel.CLAUDE_3_SONNET


def test_get_default_model_invalid():
    """Test behavior with an invalid model name."""
    # Set environment variable to an invalid model
    original_value = os.environ.get("OPENROUTER_DEFAULT_MODEL")
    os.environ["OPENROUTER_DEFAULT_MODEL"] = "invalid/model-name"

    # Get the default model, should use fallback
    model = get_default_model()

    # Check that it returns the fallback model
    assert model == VisionModel.QWEN_QWQ_32B

    # Restore original value if it existed
    if original_value:
        os.environ["OPENROUTER_DEFAULT_MODEL"] = original_value
    else:
        del os.environ["OPENROUTER_DEFAULT_MODEL"]


def test_get_default_model_fallback(clear_env_vars):
    """Test fallback to default model when not set in environment."""
    # Ensure environment variable is not set
    assert "OPENROUTER_DEFAULT_MODEL" not in os.environ

    # Get the default model
    model = get_default_model()

    # Check that it returns the fallback value
    assert model == VisionModel.QWEN_QWQ_32B
