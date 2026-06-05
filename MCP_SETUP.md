# MCP Integration Setup

This directory contains an MCP (Model Context Protocol) integration with a FastAPI server for managing school activities. The MCP server exposes the FastAPI endpoints as tools that Copilot can use.

## Project Structure

```
.
├── src/
│   ├── app.py              # FastAPI application with activity endpoints
│   ├── mcp_server.py       # MCP server that wraps the FastAPI endpoints
│   └── static/             # Static files (HTML, CSS, JS)
├── .vscode/
│   └── mcp.json            # MCP server configuration
└── requirements.txt        # Python dependencies
```

## Setup Instructions

### 1. Install Dependencies

```bash
pip install -r requirements.txt
```

This installs:
- **fastapi** - Web framework
- **uvicorn** - ASGI server
- **mcp** - Model Context Protocol SDK
- **httpx** - Async HTTP client for MCP server

### 2. Start the FastAPI Server

In one terminal:

```bash
uvicorn src.app:app --reload
```

This starts the FastAPI server on `http://localhost:8000`.

### 3. MCP Server Configuration

The `.vscode/mcp.json` file configures the MCP server:

```json
{
  "servers": {
    "activities": {
      "type": "stdio",
      "command": "python",
      "args": ["-m", "src.mcp_server"],
      "cwd": "/workspaces/skills-integrate-mcp-with-copilot1"
    }
  }
}
```

When Copilot needs to use the MCP tools, it will automatically start the MCP server process via stdio.

## Available Tools

The MCP server exposes three tools that Copilot can use:

### 1. `get_activities`
Lists all available activities at Mergington High School with their details.

**Parameters:** None

**Returns:** List of activities with descriptions, schedules, and enrollment info

**Example Usage:**
```
Get all activities at the school
```

### 2. `signup_for_activity`
Sign up a student for an activity.

**Parameters:**
- `activity_name` (string): Name of the activity (e.g., "Chess Club", "Programming Class")
- `email` (string): Student's email address (e.g., "student@mergington.edu")

**Returns:** Confirmation message

**Example Usage:**
```
Sign up john.doe@mergington.edu for Chess Club
```

### 3. `unregister_from_activity`
Unregister a student from an activity.

**Parameters:**
- `activity_name` (string): Name of the activity
- `email` (string): Student's email address

**Returns:** Confirmation message

**Example Usage:**
```
Unregister jane.smith@mergington.edu from Soccer Team
```

## How MCP Integration Works

1. **Copilot Chat** makes a request to use tools
2. **VS Code** reads the MCP configuration from `.vscode/mcp.json`
3. **VS Code** spawns the MCP server process: `python -m src.mcp_server`
4. **MCP Server** starts and registers the available tools with Copilot
5. **Copilot** can now call any of the exposed tools
6. **MCP Server** translates tool calls to HTTP requests to the FastAPI backend
7. **FastAPI** processes the request and returns the result
8. **MCP Server** formats the response and returns it to Copilot

## Development

To test the MCP server directly:

```bash
# Start the FastAPI server first
uvicorn src.app:app --reload

# In another terminal, test the API
curl http://localhost:8000/activities
```

## Troubleshooting

**Port 8000 already in use:**
```bash
# Use a different port
uvicorn src.app:app --port 8001 --reload
# Note: Update API_BASE_URL in mcp_server.py if you change the port
```

**MCP Server not starting:**
- Ensure FastAPI server is running on http://localhost:8000
- Check that dependencies are installed: `pip install -r requirements.txt`
- Review stderr logs for connection errors

**Tools not available in Copilot:**
- Verify `.vscode/mcp.json` exists and is valid JSON
- Ensure the path in mcp.json matches your workspace location
- Reload VS Code window (Cmd+R on Mac, Ctrl+R on Linux/Windows)
