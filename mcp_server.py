# mcp_server.py

import os
import json
from flask import Flask, request, jsonify
from mcp.server import Server
from mcp.types import Tool, TextContent
from tools import get_current_balance, add_purchase

# --- Server Setup ---
app = Flask(__name__)

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


# --- Flask Routes to expose MCP tools ---
@app.route('/mcp/list-tools', methods=['GET'])
def list_tools():
    """
    Exposes a route for Puch AI to discover the available tools.
    """
    return jsonify([tool.model_dump() for tool in tool_schemas])


@app.route('/mcp/call-tool', methods=['POST'])
def call_tool():
    """
    Exposes a route for Puch AI to call a specific tool.
    """
    data = request.json
    name = data.get('name')
    arguments = data.get('arguments', {})

    if name == "get_current_balance":
        balance = get_current_balance()
        return jsonify({"result": f"💰 Current Balance: ₹{balance:.2f}"})

    elif name == "add_purchase":
        result = add_purchase(
            item_name=arguments.get("item_name"),
            cost=arguments.get("cost"),
            category=arguments.get("category")
        )
        return jsonify({"result": result})

    return jsonify({"error": f"Unknown tool: {name}"}), 400


# --- Main Entry Point ---
if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port)