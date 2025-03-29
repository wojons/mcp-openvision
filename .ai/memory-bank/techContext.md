# Technical Context

## Essential Technologies

- **Python 3.9+**: Primary programming language
- **Model Context Protocol (MCP)**: Framework for AI tool interfaces
- **OpenRouter API**: Gateway to vision-capable models
- **FastMCP**: MCP server implementation framework

## Core Dependencies

- **MCP**: `mcp>=0.1.0` - Core MCP Python SDK
- **Requests**: `requests>=2.28.0` - HTTP client for API calls
- **Standard Library**: Leveraging `re`, `os`, `pathlib`, `base64`, etc.

## Development Dependencies

- **pytest**: For testing
- **pytest-asyncio**: For testing async functions
- **black**: For code formatting
- **isort**: For import sorting
- **mypy**: For type checking

## Environment Setup

- **Environment Variables**:
  - `OPENROUTER_API_KEY`: Required API key for OpenRouter
  - `OPENROUTER_DEFAULT_MODEL`: Optional default model selection

## Infrastructure Requirements

- **Minimal**: Python 3.9+ runtime
- **Network**: Access to OpenRouter API

## API Integration

### OpenRouter API

- **Authentication**: API key based
- **Endpoint**: `https://openrouter.ai/api/v1/chat/completions`
- **Response Format**: JSON with model-generated text
- **Image Format**: Base64-encoded within the request payload

### Model Context Protocol

- **Protocol**: MCP server protocol
- **Tools**: Defined through decorators
- **Data Types**: Support for binary data (images)

## Image Processing

- **Input Formats**:
  - Base64-encoded strings
  - Image URLs (http/https)
  - Local file paths
- **Conversion**: Automatic detection and conversion to base64
- **Validation**: Checks for valid inputs before processing

## Security Considerations

- **API Keys**: Stored in environment variables
- **Image Data**: Processed in memory, not stored
- **URL Validation**: Implemented to prevent abuse

## Code Organization

```
src/mcp_openvision/
├── __init__.py   # Package initialization
├── __main__.py   # Entry point
├── server.py     # MCP server implementation with image processing
├── config.py     # Configuration management
└── exceptions.py # Error handling
```

## Testing Approach

- **Unit Tests**: For individual functions
- **Mock Tests**: Using predefined API responses
- **Fixtures**: For consistent test environments
- **Test Coverage**: Comprehensive tests for all functionality

## MCP Compliance Requirements

- **Tool Definitions**: Properly defined with correct decorators
- **Async Support**: Using async/await consistently
- **Type Annotations**: Following MCP type definitions
- **Error Handling**: Returning appropriate error responses
- **Documentation**: Clear docstrings for all tools
