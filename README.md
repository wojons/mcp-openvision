# MCP OpenVision

[![CI](https://github.com/Nazruden/mcp-openvision/actions/workflows/ci.yml/badge.svg)](https://github.com/Nazruden/mcp-openvision/actions/workflows/ci.yml)
[![PyPI version](https://img.shields.io/pypi/v/mcp-openvision.svg)](https://pypi.org/project/mcp-openvision/)
[![Python Versions](https://img.shields.io/pypi/pyversions/mcp-openvision.svg)](https://pypi.org/project/mcp-openvision/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)

## Overview

MCP OpenVision is a Model Context Protocol (MCP) server that provides image analysis capabilities powered by OpenRouter vision models. It enables AI assistants to analyze images via a simple interface within the MCP ecosystem.

## Installation

### Using pip

```bash
pip install mcp-openvision
```

### Using UV (recommended)

```bash
uv pip install mcp-openvision
```

## Configuration

MCP OpenVision requires an OpenRouter API key and can be configured through environment variables:

- **OPENROUTER_API_KEY** (required): Your OpenRouter API key
- **OPENROUTER_DEFAULT_MODEL** (optional): The default vision model to use

### Supported Models

- `qwen/qwq-32b:free` (default)
- `anthropic/claude-3-5-sonnet`
- `anthropic/claude-3-opus`
- `anthropic/claude-3-sonnet`
- `openai/gpt-4o`

## Usage

### Testing with MCP Inspector

The easiest way to test MCP OpenVision is with the MCP Inspector tool:

```bash
npx @modelcontextprotocol/inspector uvx mcp-openvision
```

### Integration with Claude Desktop or Cursor

1. Edit your MCP configuration file:

   - Windows: `%USERPROFILE%\.cursor\mcp.json`
   - macOS: `~/.cursor/mcp.json` or `~/Library/Application Support/Claude/claude_desktop_config.json`

2. Add the following configuration:

```json
{
  "mcpServers": {
    "openvision": {
      "command": "uvx",
      "args": ["mcp-openvision"],
      "env": {
        "OPENROUTER_API_KEY": "your_openrouter_api_key_here",
        "OPENROUTER_DEFAULT_MODEL": "anthropic/claude-3-sonnet"
      }
    }
  }
}
```

### Running Locally for Development

```bash
# Set the required API key
export OPENROUTER_API_KEY="your_api_key"

# Run the server module directly
python -m mcp_openvision
```

## Features

MCP OpenVision provides the following core tool:

- **image_analysis**: Analyze images with vision models, supporting various parameters:
  - `image`: Can be provided as:
    - Base64-encoded image data
    - Image URL (http/https)
    - Local file path
  - `prompt`: Analysis instruction
  - `model`: Vision model to use
  - `temperature`: Controls randomness (0.0-1.0)
  - `max_tokens`: Maximum response length

### Example Usage

```python
# Analyze an image from a URL
result = await image_analysis(
    image="https://example.com/image.jpg",
    prompt="Describe this image in detail"
)

# Analyze an image from a local file
result = await image_analysis(
    image="path/to/local/image.jpg",
    prompt="What objects are in this image?"
)

# Analyze with a base64-encoded image
result = await image_analysis(
    image="SGVsbG8gV29ybGQ=...",  # base64 data
    prompt="Analyze this image"
)
```

## Development

### Setup Development Environment

```bash
# Clone the repository
git clone https://github.com/modelcontextprotocol/mcp-openvision.git
cd mcp-openvision

# Install development dependencies
pip install -e ".[dev]"
```

### Run Tests

```bash
pytest
```

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.
