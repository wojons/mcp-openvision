#!/usr/bin/env python
"""
Test script for OpenRouter vision API using direct HTTP requests.
This bypasses our MCP server and tests the API directly.
"""

import os
import base64
import requests
import json
from pathlib import Path

def encode_image_to_base64(image_path):
    """Encode image file to base64."""
    with open(image_path, "rb") as image_file:
        return base64.b64encode(image_file.read()).decode("utf-8")

def test_openrouter_vision_api():
    """Test the OpenRouter vision API with direct HTTP requests."""
    print("Testing OpenRouter Vision API directly...")
    
    # Get API key from environment or use the one from mcp.json
    api_key = os.environ.get("OPENROUTER_API_KEY")
    model = "qwen/qwen2.5-vl-32b-instruct:free"
    
    # Get current working directory
    cwd = os.getcwd()
    print(f"Current working directory: {cwd}")
    
    # Find test image
    test_image_path = Path(cwd) / "examples" / "test_image.png"
    if not test_image_path.exists():
        # Try sample image as fallback
        test_image_path = Path(cwd) / "sample_image.jpg"
        if not test_image_path.exists():
            print("No test images found. Please add an image to examples/test_image.png or sample_image.jpg")
            return
    
    print(f"Using image: {test_image_path}")
    
    # Determine MIME type based on file extension
    if test_image_path.suffix.lower() == '.png':
        mime_type = 'image/png'
    elif test_image_path.suffix.lower() in ['.jpg', '.jpeg']:
        mime_type = 'image/jpeg'
    elif test_image_path.suffix.lower() == '.webp':
        mime_type = 'image/webp'
    else:
        mime_type = 'image/jpeg'  # Default
    
    print(f"Detected MIME type: {mime_type}")
    
    try:
        # Encode image to base64
        base64_image = encode_image_to_base64(test_image_path)
        print(f"Successfully encoded image to base64")
        
        # Prepare OpenRouter request
        headers = {
            "Authorization": f"Bearer {api_key}",
            "Content-Type": "application/json",
            "HTTP-Referer": "https://github.com/modelcontextprotocol/mcp-openvision",
            "X-Title": "MCP OpenVision Test",
        }
        
        messages = [
            {"role": "system", "content": "You are an expert vision analyzer."},
            {
                "role": "user",
                "content": [
                    {"type": "text", "text": "What do you see in this image? Describe it in detail."},
                    {
                        "type": "image_url",
                        "image_url": {"url": f"data:{mime_type};base64,{base64_image}"},
                    },
                ],
            },
        ]
        
        payload = {
            "model": model,
            "messages": messages,
            "max_tokens": 1000,
            "temperature": 0.7,
        }
        
        print("Sending request to OpenRouter...")
        
        # Make the API call
        response = requests.post(
            "https://openrouter.ai/api/v1/chat/completions",
            headers=headers,
            json=payload,
        )
        
        # Check for errors
        if response.status_code != 200:
            print(f"Error from OpenRouter: {response.status_code} - {response.text}")
            return
        
        # Parse and print the response
        result = response.json()
        print("\nAPI Response:")
        print(json.dumps(result, indent=2))
        
        # Extract just the content
        analysis = result["choices"][0]["message"]["content"]
        print("\nImage Analysis Result:")
        print(analysis)
        
        print("\nTest completed successfully!")
        
    except Exception as e:
        print(f"Error: {str(e)}")

if __name__ == "__main__":
    test_openrouter_vision_api()
 