# MCP OpenVision

[![CI](https://github.com/Nazruden/mcp-openvision/actions/workflows/ci.yml/badge.svg)](https://github.com/Nazruden/mcp-openvision/actions/workflows/ci.yml)
[![PyPI version](https://img.shields.io/pypi/v/mcp-openvision.svg)](https://pypi.org/project/mcp-openvision/)
[![Python Versions](https://img.shields.io/pypi/pyversions/mcp-openvision.svg)](https://pypi.org/project/mcp-openvision/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)

A simple MCP server for image analysis using OpenRouter. This MCP server allows clients (like Claude Desktop and Cursor) to analyze images with state-of-the-art vision models.

## Features

- **Analyze images** from local or remote sources using Claude, GPT-4o, or other models
- **Extract text** from images with language hints
- **Compare images** and identify differences
- **Multiple analysis modes** (general, detailed, text extraction, technical, social media)
- **Configurable** through environment variables

## Installation

### Option 1: Install from PyPI (Recommended)

The simplest way to install MCP OpenVision is directly from PyPI:

```bash
pip install mcp-openvision
```

This method allows you to use the server with `uvx` in your mcp.json configuration.

### Option 2: Install from source

```bash
# Clone the repository
git clone https://github.com/Nazruden/mcp-openvision.git
cd mcp-openvision

# Install the package
pip install -e .
```

## Quick Setup

### 1. Get an OpenRouter API Key

Sign up at [openrouter.ai](https://openrouter.ai) to get your API key.

### 2. Configure in mcp.json

Add the following to your mcp.json file (typically located at `~/.cursor/mcp.json` or equivalent):

```json
{
  "mcpServers": {
    "openvision": {
      "command": "uvx",
      "args": ["mcp-openvision"],
      "env": {
        "OPENROUTER_API_KEY": "your_openrouter_api_key_here",
        "OPENROUTER_DEFAULT_MODEL": "qwen/qwq-32b:free"
      }
    }
  }
}
```

For detailed configuration options, see [MCP_CONFIG.md](MCP_CONFIG.md).

## Using MCP OpenVision

Once installed and configured, you can use MCP OpenVision with any MCP client like Claude Desktop or Cursor.

### Available Tools

- **analyze_image**: General purpose image analysis with various modes
- **extract_text_from_image**: Specialized tool for extracting text from images
- **compare_images**: Tool for comparing two images and describing differences

### Example Prompts

- "Analyze this screenshot and tell me what's happening on the webpage"
- "Extract all text from this image"
- "Describe this photo in detail"
- "Is there a dog in this picture?"
- "What kind of chart is this and what data is it showing?"

## Environment Variables

Configure MCP OpenVision using these environment variables in your mcp.json:

- **OPENROUTER_API_KEY** (required): Your OpenRouter API key
- **OPENROUTER_DEFAULT_MODEL** (optional): The default vision model to use

## Development

### Running Tests

```bash
pip install -e ".[dev]"
pytest tests/
```

## License

MIT
