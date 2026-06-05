"""
MCP Server for High School Activities Management

This server exposes the FastAPI endpoints as MCP tools that can be used
by Copilot to interact with the school activities system.
"""

import asyncio
import sys
import logging
from mcp.server import Server
from mcp.types import Tool, TextContent
import httpx

# Configure logging
logging.basicConfig(level=logging.INFO, stream=sys.stderr)
logger = logging.getLogger(__name__)

# Server configuration
API_BASE_URL = "http://localhost:8000"

# Create server instance
server = Server("activities-mcp")


@server.call_tool()
async def handle_call_tool(name: str, arguments: dict):
    """Handle tool calls from Copilot"""
    logger.info(f"Tool called: {name} with arguments: {arguments}")
    
    async with httpx.AsyncClient(timeout=10.0) as client:
        try:
            if name == "get_activities":
                # List all activities
                response = await client.get(f"{API_BASE_URL}/activities")
                response.raise_for_status()
                activities = response.json()
                
                # Format the response nicely
                activities_text = "**Available Activities:**\n\n"
                for activity_name, details in activities.items():
                    activities_text += f"**{activity_name}**\n"
                    activities_text += f"- Description: {details['description']}\n"
                    activities_text += f"- Schedule: {details['schedule']}\n"
                    activities_text += f"- Participants: {len(details['participants'])}/{details['max_participants']}\n"
                    activities_text += f"- Current members: {', '.join(details['participants']) if details['participants'] else 'None'}\n\n"
                
                return [TextContent(type="text", text=activities_text)]
            
            elif name == "signup_for_activity":
                # Sign up for an activity
                activity_name = arguments.get("activity_name")
                email = arguments.get("email")
                
                if not activity_name or not email:
                    return [TextContent(type="text", text="Error: Missing required parameters: activity_name and email")]
                
                response = await client.post(
                    f"{API_BASE_URL}/activities/{activity_name}/signup",
                    params={"email": email}
                )
                
                if response.status_code == 200:
                    result = response.json()
                    return [TextContent(type="text", text=result["message"])]
                else:
                    error = response.json()
                    return [TextContent(type="text", text=f"Error: {error.get('detail', 'Unknown error')}")]
            
            elif name == "unregister_from_activity":
                # Unregister from an activity
                activity_name = arguments.get("activity_name")
                email = arguments.get("email")
                
                if not activity_name or not email:
                    return [TextContent(type="text", text="Error: Missing required parameters: activity_name and email")]
                
                response = await client.delete(
                    f"{API_BASE_URL}/activities/{activity_name}/unregister",
                    params={"email": email}
                )
                
                if response.status_code == 200:
                    result = response.json()
                    return [TextContent(type="text", text=result["message"])]
                else:
                    error = response.json()
                    return [TextContent(type="text", text=f"Error: {error.get('detail', 'Unknown error')}")]
            
            else:
                return [TextContent(type="text", text=f"Error: Unknown tool: {name}")]
        
        except Exception as e:
            logger.error(f"Error calling {name}: {str(e)}", exc_info=True)
            return [TextContent(type="text", text=f"Error calling {name}: {str(e)}")]


@server.list_tools()
async def handle_list_tools():
    """Return list of available tools"""
    return [
        Tool(
            name="get_activities",
            description="Get a list of all available activities at Mergington High School, including their descriptions, schedules, and current enrollment",
            inputSchema={
                "type": "object",
                "properties": {},
                "required": []
            }
        ),
        Tool(
            name="signup_for_activity",
            description="Sign up a student for an activity. The student must provide their email address.",
            inputSchema={
                "type": "object",
                "properties": {
                    "activity_name": {
                        "type": "string",
                        "description": "The name of the activity to sign up for (e.g., 'Chess Club', 'Programming Class')"
                    },
                    "email": {
                        "type": "string",
                        "description": "The student's email address (e.g., student@mergington.edu)"
                    }
                },
                "required": ["activity_name", "email"]
            }
        ),
        Tool(
            name="unregister_from_activity",
            description="Unregister a student from an activity they are currently enrolled in",
            inputSchema={
                "type": "object",
                "properties": {
                    "activity_name": {
                        "type": "string",
                        "description": "The name of the activity to unregister from"
                    },
                    "email": {
                        "type": "string",
                        "description": "The student's email address"
                    }
                },
                "required": ["activity_name", "email"]
            }
        )
    ]


async def main():
    """Run the MCP server"""
    logger.info("Starting Activities MCP Server...")
    async with server:
        logger.info("Activities MCP Server running and waiting for connections...")
        await server.wait_for_shutdown()


if __name__ == "__main__":
    asyncio.run(main())
