# MCP OpenVision Quick Start Guide

This guide will help you get started with the MCP OpenVision server quickly.

## Prerequisites

- Python 3.10 or higher
- An OpenRouter API key (get one at [openrouter.ai](https://openrouter.ai))
- Claude Desktop or another MCP client

## Installation

### Option 1: Install directly from source

```bash
# Clone the repository
git clone https://github.com/yourusername/mcp-openvision.git
cd mcp-openvision

# Install the package
pip install -e .
```

### Option 2: Install using FastMCP

```bash
# Install directly for use with Claude
fastmcp install src/mcp_openvision/server.py --name "OpenVision" -e OPENROUTER_API_KEY=your_api_key_here
```

### Option 3: Install as a published package (if available)

```bash
# Install with pip/uv
pip install mcp-openvision

# Or install with npm (if published to npm)
npm install -g @mcpservers/openvision
```

## Setting Up Your API Key

The MCP server requires an OpenRouter API key to function. You can set it up in one of these ways:

1. **Environment variable**:

   ```bash
   export OPENROUTER_API_KEY="your_api_key_here"
   ```

2. **When installing with FastMCP**:

   ```bash
   fastmcp install src/mcp_openvision/server.py -e OPENROUTER_API_KEY=your_api_key_here
   ```

3. **In your mcp.json configuration**:
   ```json
   "openvision": {
     "command": "uvx",
     "args": ["mcp-openvision"],
     "env": {
       "OPENROUTER_API_KEY": "your_api_key_here",
       "OPENROUTER_DEFAULT_MODEL": "anthropic/claude-3-sonnet"
     }
   }
   ```

## Setting the Default Model

You can specify which vision model to use by default:

1. **Environment variable**:

   ```bash
   export OPENROUTER_DEFAULT_MODEL="anthropic/claude-3-opus"
   ```

2. **In your mcp.json configuration**:
   ```json
   "env": {
     "OPENROUTER_API_KEY": "your_api_key_here",
     "OPENROUTER_DEFAULT_MODEL": "anthropic/claude-3-opus"
   }
   ```

Available models include:

- "anthropic/claude-3-5-sonnet"
- "anthropic/claude-3-opus"
- "anthropic/claude-3-sonnet" (default)
- "openai/gpt-4o"

## Manual Configuration in mcp.json

For more detailed instructions on configuring the server in your mcp.json file, see [MCP_CONFIG.md](MCP_CONFIG.md).

## Using with Claude Desktop

Once installed with `fastmcp install` or configured in your mcp.json, the OpenVision server will be available in Claude Desktop. Simply:

1. Open Claude Desktop
2. Click on the "Tools" menu
3. Select "OpenVision" from the list of available MCP servers
4. Use Claude to analyze images

## Example Prompts

Here are some example prompts you can use with Claude:

- "Analyze this screenshot of a website and tell me what it's about"
- "Extract all the text from this image"
- "Compare these two images and tell me the differences"
- "Is there a chart in this image? If so, analyze it and extract the data"
- "What objects can you see in this photo?"
- "Describe this technical diagram in detail"

## Running in Development Mode

For development and testing, you can run the server in development mode:

```bash
fastmcp dev src/mcp_openvision/server.py -e OPENROUTER_API_KEY=your_api_key_here
```

This will launch the MCP Inspector, which allows you to:

- Test your tools interactively
- View detailed logs
- Debug any issues

## Available Tools

The OpenVision MCP server provides the following tools:

- **analyze_image**: General purpose image analysis with various modes
- **extract_text_from_image**: Specialized tool for extracting text from images
- **compare_images**: Tool for comparing two images and describing differences

Each tool has parameters you can adjust for your specific needs.
