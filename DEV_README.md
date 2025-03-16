# Developer Guide for mcp-my-mac

This document provides guidance for developers working on the `mcp-my-mac` project.

## Project Overview

`mcp-my-mac` is a MCP Server for managing Mac configuration and information. It provides an API for querying and managing Mac-specific settings and retrieving system information.

## Development Setup

### Prerequisites

- Python 3.10+
- pip
- git

### Installation

1. Clone the repository:
   ```bash
   git clone git@github.com:zhongmingyuan/mcp-my-mac.gi
   cd mcp-my-mac
   ```

2. Create and activate a virtual environment:
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows, use `venv\Scripts\activate`
   ```

3. Install the package in development mode with dev dependencies:
   ```bash
   pip install -e ".[dev]"
   ```
4. pre commit format and lint the code
   ```bash
   pre-commit run --all-files
   ```
