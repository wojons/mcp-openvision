# System Patterns

## Simplified Architecture

MCP OpenVision follows a straightforward architecture:

```mermaid
flowchart TD
    Client[Client Applications]
    MCP[MCP Server Layer]
    OpenRouter[OpenRouter API]

    Client --> MCP
    MCP --> OpenRouter

    subgraph "MCP OpenVision"
        MCP
    end
```

## Core Components

### MCP Server Module

- **Purpose**: Provide MCP-compliant tools for image analysis
- **Pattern**: Follows standard MCP tool definitions
- **Key File**: `server.py`

### Essential Utilities

- **Error Handling**: Simple exception hierarchy
- **Configuration**: Basic environment variable support
- **Image Processing**: Minimal preprocessing helpers

## Data Flow

The system follows a simple request-response flow:

```mermaid
sequenceDiagram
    Client->>MCP Server: Image Analysis Request
    MCP Server->>OpenRouter: Vision API Request
    OpenRouter->>MCP Server: Analysis Results
    MCP Server->>Client: Formatted Results
```

## Error Handling Approach

Basic error handling pattern:

```mermaid
flowchart TD
    Error[Error Occurs] --> Handled{Can be handled?}
    Handled -->|Yes| RetryOrContinue[Retry or Continue]
    Handled -->|No| TransformError[Transform to User-Friendly Error]
    TransformError --> ReturnError[Return Error to Client]
```

## Configuration

Simple configuration from environment variables:

```mermaid
flowchart TD
    Config[Configuration]
    Param[Function Parameters]
    Env[Environment Variables]
    Default[Default Values]

    Config --> Param
    Param -->|Not Set| Env
    Env -->|Not Set| Default
```

## Testing Strategy

Focus on core functionality testing:

```mermaid
flowchart TD
    Unit[Unit Tests]
    Mock[Mocked API Tests]

    Unit --> Mock
```

## MCP Compliance

The project strictly adheres to MCP patterns:

1. **Tool Definitions**: Using `@mcp.tool()` decorators
2. **Type Annotations**: Following MCP type definitions
3. **Async Patterns**: Using proper async/await patterns
4. **Error Handling**: Returning informative errors
