# Implementation Plan for Simplified OpenVision MCP Server

## Overview

This plan outlines the specific technical changes needed to simplify the MCP OpenVision server and focus it on a single customizable image_analysis tool.

## 1. Server Simplification

### 1.1 Remove Unused Tools

- Delete the following tools from `server.py`:
  - `extract_text_from_image`
  - `compare_images`
  - `detect_objects`
- Remove the `image_analysis_prompt` as it won't be needed

### 1.2 Update Enum Classes

- Keep the `VisionModel` enum for model selection
- Consider removing or simplifying the `AnalysisMode` enum if no longer needed

### 1.3 Update Server Initialization

- Update the server description to reflect the simplified focus
- Remove any references to removed tools from the documentation

## 2. Enhance the `image_analysis` Tool

### 2.1 Restructure Parameters

```python
@mcp.tool()
async def image_analysis(
    image: types.BinaryData,
    prompt: Optional[str] = None,
    messages: Optional[List[dict]] = None,
    model: Optional[VisionModel] = None,
    max_tokens: int = 4000,
    temperature: float = 0.7,
    # Add other relevant OpenRouter parameters
    ctx: types.Context = None,
) -> str:
```

### 2.2 Implement Message Handling

- Add logic to handle both `prompt` and `messages` parameters:

```python
# Handle messages vs. prompt
if messages is None:
    # Create default messages from prompt
    default_prompt = prompt or "Analyze this image in detail"
    messages = [
        {
            "role": "user",
            "content": [
                {"type": "text", "text": default_prompt},
                {
                    "type": "image_url",
                    "image_url": {"url": f"data:image/jpeg;base64,{base64_image}"},
                },
            ],
        }
    ]
else:
    # Ensure the image is included in the messages
    # Insert image at appropriate position if not already present
```

### 2.3 Add Parameter Validation

- Validate incoming parameters
- Handle edge cases (e.g., both prompt and messages provided)
- Ensure reasonable defaults

## 3. Improve Configuration Management

### 3.1 Create a Configuration Module

- Create a new file `src/mcp_openvision/config.py` to centralize configuration:

```python
import os
from enum import Enum
from typing import Optional

class VisionModel(str, Enum):
    """Available vision models from OpenRouter."""
    # Keep existing models

def get_api_key() -> str:
    """Get API key with better error handling"""

def get_default_model() -> VisionModel:
    """Get default model with better error handling"""

# Add other configuration functions as needed
```

### 3.2 Update Environment Variable Handling

- Add support for loading from `.env` files (optional)
- Document all supported environment variables
- Implement validation for configuration values

## 4. Improve Error Handling

### 4.1 Create Error Classes

- Create a new file `src/mcp_openvision/exceptions.py`:

```python
class OpenVisionError(Exception):
    """Base exception for OpenVision MCP server."""

class ConfigurationError(OpenVisionError):
    """Error in server configuration."""

class OpenRouterError(OpenVisionError):
    """Error from the OpenRouter API."""

# Add other exception classes as needed
```

### 4.2 Implement Error Handling in the Tool

- Use try/except blocks to catch and handle errors
- Return informative error messages
- Log detailed error information when context is available

## 5. Update Documentation

### 5.1 Update README

- Update with simplified tool description
- Add examples of using the simplified tool
- Document all configuration options

### 5.2 Add Example Usage

- Create an examples directory with sample code
- Include examples for different use cases

## 6. Testing

### 6.1 Test Plan

- Test the simplified tool with various parameters
- Test error handling
- Test configuration management

### 6.2 Manual Testing Checklist

- Verify MCP compliance
- Test with different image types
- Test with different OpenRouter models

## Timeline

- Simplification Phase: 1 day
- Enhancement Phase: 1 day
- Configuration & Error Handling: 1 day
- Documentation & Testing: 1 day

## Dependencies

- MCP Python SDK
- Requests library for API calls
