# Simplified OpenVision MCP Server Stories

## Background

The current OpenVision MCP server implements several tools for image analysis using OpenRouter. We need to simplify it to focus on just one tool (`image_analysis`) and make it more customizable for AI agents.

## User Stories

### Story 1: Simplify MCP Server to One Tool

**As a** developer  
**I want** the MCP server to be simplified to just one core tool  
**So that** it's easier to maintain and use

**Acceptance Criteria:**

- Remove unnecessary tools (extract_text_from_image, compare_images, detect_objects)
- Keep only the core image_analysis functionality
- Update documentation to reflect the simplified approach
- Ensure the server is still MCP-compliant

### Story 2: Allow AI Agent to Customize Chat Completion Request

**As an** AI agent  
**I want** to customize OpenRouter chat completion requests  
**So that** I can provide more specific instructions for image analysis

**Acceptance Criteria:**

- Allow customization of relevant parameters in the chat completion request
- Ensure the model field is determined by environment variables or configuration
- Make the messages field optional but automatically fill them when needed
- Keep the API simple and easy to understand

### Story 3: Improve Configuration Management

**As a** server administrator  
**I want** simple configuration options for the server  
**So that** I can easily set up and customize it

**Acceptance Criteria:**

- Support environment variables for configuration
- Allow overriding defaults through configuration files
- Document all configuration options clearly
- Implement reasonable defaults

### Story 4: Improve Error Handling and User Experience

**As a** user of the MCP server  
**I want** clear error messages and good documentation  
**So that** I can troubleshoot issues easily

**Acceptance Criteria:**

- Implement proper error handling for OpenRouter API errors
- Return user-friendly error messages
- Add example usage in documentation
- Include troubleshooting tips

## Implementation Plan

1. **Simplification Phase:**

   - Remove unused tools from server.py
   - Consolidate functionality into one core tool
   - Update initialization and documentation

2. **Customization Phase:**

   - Extend the image_analysis tool to accept customization parameters
   - Implement automatic filling of required fields
   - Add validation for parameters

3. **Configuration Phase:**

   - Add support for reading configuration from environment variables
   - Implement sane defaults
   - Document configuration options

4. **Testing & Documentation Phase:**
   - Test the simplified implementation
   - Update README and documentation
   - Add examples of usage
