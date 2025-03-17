# MCP My Mac

A lightweight server that exposes Mac system information via a simple API, allowing AI assistants like Claude to access real-time system information about your Mac. This tool is primarily designed for Mac users who want to experiment with AI and Deep Learning on their machines.

> **Status: BETA** - This project is currently in beta. We're actively looking for feedback to improve functionality and user experience. Please share your thoughts and suggestions!

## Why Use It?

- Provides Claude Desktop or other MCP clients with access to your Mac's hardware specifications, system configuration, and resource usage
- Enables more targeted and accurate assistance for software optimization and troubleshooting
- Runs as a secure local API with minimal overhead
- Only executes safe, verified commands:
  - `system_profiler` - to gather system information
  - `conda` - to analyze Python environment configurations

## Installation

### Method 1: Using UV + Git Clone

#### Prerequisites
- Python 3.8 or higher
- UV package manager installed

#### Steps

1. Clone the repository:   ```bash
   git clone git@github.com:zhongmingyuan/mcp-my-mac.git   ```

2. Configure for your AI client:

   **[Claude Desktop]** Add the following to your MCP server config file:
   ```json
   "mcpServers": {
       "mcp-my-mac": {
           "command": "uv",
           "args": [
               "--directory",
               "/YOUR_PATH_TO/mcp-my-mac",
               "run",
               "-m",
               "mcp_server_my_mac"
           ]
       }
   }
   ```
   > Note: Replace `/YOUR_PATH_TO` with the actual path where you cloned the repository.

   **[Cursor]** Add tool by selecting "command" in UI:
   ```bash
   uv run --directory /YOUR_PATH_TO/mcp-my-mac mcp_server_my_mac
   ```

## Usage

After installation, Claude Desktop will automatically connect to this API when running on your Mac, allowing it to access system information when needed for answering your questions or providing assistance.
