import asyncio
import logging
import sys
import os
from mcp.server import Server
from mcp.server.stdio import stdio_server
from mcp.server.models import InitializationOptions
from mcp.server import NotificationOptions
from mcp.types import Tool, TextContent

# Add the parent directory to the path to import tools correctly
sys.path.append(os.path.dirname(os.path.abspath(__file__)))
from tools import get_current_balance, add_purchase

# --- Server Setup ---
server = Server(name="budget-buddy-mcp")
logger = logging.getLogger("money-tracker-mcp")

# --- Tool Schemas for Puch AI ---
tool_schemas = [
    Tool(
        name="get_current_balance",
        description="Gets the user's current financial balance.",
        inputSchema={"type": "object", "properties": {}},
    ),
    Tool(
        name="add_purchase",
        description="Adds a new purchase to the user's financial record.",
        inputSchema={
            "type": "object",
            "properties": {
                "item_name": {"type": "string", "description": "The name of the item purchased."},
                "cost": {"type": "number", "description": "The cost of the item."},
                "category": {"type": "string", "description": "The category of the purchase."}
            },
            "required": ["item_name", "cost", "category"],
        }
    ),
]

# --- MCP Server Decorators ---
@server.list_tools()
async def list_tools() -> list[Tool]:
    return tool_schemas

@server.call_tool()
async def call_tool(name: str, arguments: dict) -> list[TextContent]:
    logger.info(f"Received call for tool: {name}")

    if name == "get_current_balance":
        balance = get_current_balance()
        return [TextContent(type="text", text=f"💰 Current Balance: ₹{balance:.2f}")]
    elif name == "add_purchase":
        result = add_purchase(item_name=arguments.get("item_name"),
                              cost=arguments.get("cost"),
                              category=arguments.get("category"))
        return [TextContent(type="text", text=result)]

    return [TextContent(type="text", text=f"Unknown tool: {name}")]

# --- Main Entry Point ---
async def main():
    print("🚀 Starting MoneyTracker MCP Server...")
    async with stdio_server() as (read_stream, write_stream):
        await server.run(
            read_stream,
            write_stream,
            InitializationOptions(
                server_name="moneytracker-tools",
                server_version="1.0.0",
                capabilities=server.get_capabilities(
                    notification_options=NotificationOptions(),
                    experimental_capabilities={},
                ),
            ),
        )

if __name__ == "__main__":
    asyncio.run(main())