# MCP OpenVision

[![CI](https://github.com/Nazruden/mcp-openvision/actions/workflows/ci.yml/badge.svg)](https://github.com/Nazruden/mcp-openvision/actions/workflows/ci.yml)
[![PyPI version](https://img.shields.io/pypi/v/mcp-openvision.svg)](https://pypi.org/project/mcp-openvision/)
[![Python Versions](https://img.shields.io/pypi/pyversions/mcp-openvision.svg)](https://pypi.org/project/mcp-openvision/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)

A simple MCP server for image analysis using OpenRouter. This MCP server allows clients (like Claude Desktop) to analyze images with state-of-the-art vision models.

## Features

- **Analyze images** from local or remote sources using Claude, GPT-4o, or other models
- **Extract text** from images with language hints
- **Compare images** and identify differences
- **Multiple analysis modes** (general, detailed, text extraction, technical, social media)
- **Configurable** through environment variables

## Installation

### Option 1: Install from PyPI

```bash
pip install mcp-openvision
```

### Option 2: Install from source

```bash
# Clone the repository
git clone https://github.com/Nazruden/mcp-openvision.git
cd mcp-openvision

# Install the package
pip install -e .
```

### Option 3: Install with FastMCP

```bash
# Install directly for use with Claude
fastmcp install src/mcp_openvision/server.py --name "OpenVision" -e OPENROUTER_API_KEY=your_api_key_here
```

## Requirements

- Python 3.10 or higher
- An OpenRouter API key (get one at [openrouter.ai](https://openrouter.ai))
- Claude Desktop or another MCP client

## Configuration

MCP OpenVision can be configured using environment variables:

- **OPENROUTER_API_KEY** (required): Your OpenRouter API key
- **OPENROUTER_DEFAULT_MODEL** (optional): The default vision model to use (defaults to "anthropic/claude-3-sonnet")

### Adding to your mcp.json

To use OpenVision with Claude Desktop or other MCP clients, add this to your `mcp.json` file:

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

For more detailed configuration options, see [MCP_CONFIG.md](MCP_CONFIG.md).

## Example Prompts

- "Analyze this screenshot and tell me what's happening on the webpage"
- "Extract all text from this image"
- "Describe this photo in detail"
- "Is there a dog in this picture?"
- "What kind of chart is this and what data is it showing?"

## Development

### Running in Development Mode

For development and testing, run the server in development mode:

```bash
fastmcp dev src/mcp_openvision/server.py -e OPENROUTER_API_KEY=your_api_key_here
```

### Running Tests

```bash
pip install pytest pytest-asyncio
pytest tests/
```

## Available Tools

The MCP server provides these tools:

- **analyze_image**: General purpose image analysis with various modes
- **extract_text_from_image**: Specialized tool for extracting text from images
- **compare_images**: Tool for comparing two images and describing differences

## License

MIT
