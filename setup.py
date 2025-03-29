"""Setup script for MCP OpenVision."""

from setuptools import setup, find_packages

# Read the content of the README file
with open("README.md", encoding="utf-8") as f:
    long_description = f.read()

# Read version from the package
from src.mcp_openvision import __version__

setup(
    name="mcp-openvision",
    version=__version__,
    description="MCP server for image analysis using OpenRouter",
    long_description=long_description,
    long_description_content_type="text/markdown",
    author="MCP OpenVision Team",
    author_email="your.email@example.com",
    url="https://github.com/yourusername/mcp-openvision",
    packages=find_packages(where="src"),
    package_dir={"": "src"},
    classifiers=[
        "Development Status :: 4 - Beta",
        "Intended Audience :: Developers",
        "License :: OSI Approved :: MIT License",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
    ],
    python_requires=">=3.9",
    install_requires=[
        "mcp>=0.1.0",
        "requests>=2.28.0",
    ],
    extras_require={
        "dev": [
            "pytest>=7.0.0",
            "black>=23.0.0",
            "isort>=5.12.0",
            "mypy>=1.0.0",
        ],
    },
    entry_points={
        "console_scripts": [
            "mcp-openvision=mcp_openvision.server:main",
        ],
    },
) 