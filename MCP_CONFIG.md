# MCP OpenVision Configuration Guide

This guide describes how to configure MCP OpenVision in your Claude Desktop or other MCP client setups.

## Configuration Options

MCP OpenVision can be configured in three different ways:

### 1. Local Development Configuration

This configuration is useful when you're actively developing the MCP server and want to run it directly from your local repository.

```json
"openvision-dev": {
  "command": "uv",
  "args": [
    "--directory",
    "C:/path/to/mcp-openvision",
    "run",
    "python",
    "-m",
    "src.mcp_openvision.server"
  ],
  "env": {
    "OPENROUTER_API_KEY": "your_openrouter_api_key_here",
    "OPENROUTER_DEFAULT_MODEL": "anthropic/claude-3-sonnet"
  }
}
```

**Note:** Replace `C:/path/to/mcp-openvision` with the actual path to your MCP OpenVision repository.

### 2. Published Package Configuration (Python)

If you've published the package to PyPI (or installed it locally with pip), you can use this simpler configuration:

```json
"openvision": {
  "command": "uvx",
  "args": ["mcp-openvision"],
  "env": {
    "OPENROUTER_API_KEY": "your_openrouter_api_key_here",
    "OPENROUTER_DEFAULT_MODEL": "anthropic/claude-3-sonnet"
  }
}
```

### 3. NPM Package Configuration

If the package is published as an npm package, you can use this configuration:

```json
"openvision-npm": {
  "command": "npx",
  "args": ["@mcpservers/openvision"],
  "env": {
    "OPENROUTER_API_KEY": "your_openrouter_api_key_here",
    "OPENROUTER_DEFAULT_MODEL": "anthropic/claude-3-sonnet"
  }
}
```

## Environment Variables

MCP OpenVision supports these environment variables:

- **OPENROUTER_API_KEY** (required): Your OpenRouter API key
- **OPENROUTER_DEFAULT_MODEL** (optional): The default vision model to use. If not specified, defaults to "anthropic/claude-3-sonnet"

Valid model options include:

- "anthropic/claude-3-5-sonnet"
- "anthropic/claude-3-opus"
- "anthropic/claude-3-sonnet"
- "openai/gpt-4o"
- Any other valid OpenRouter model ID that supports vision

## Adding to your mcp.json

To use any of these configurations, add them to your `mcp.json` file under the `mcpServers` section:

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
    },
    "other-server": {
      // Your other servers configuration...
    }
  }
}
```

The mcp.json file is typically located at:

- Windows: `%USERPROFILE%\.cursor\mcp.json`
- macOS: `~/.cursor/mcp.json`
- Linux: `~/.cursor/mcp.json`
