# mcp_server.py

import os
import json
from flask import Flask, request, jsonify
from mcp.server import Server
from mcp.types import Tool
from tools import get_current_balance, add_purchase
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

POOCH_BEARER_TOKEN = os.environ.get("POOCH_BEARER_TOKEN", "")

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
    Tool(
        name="validate",
        description="Validates the MCP server connection and returns the phone number in {country_code}{number} format.",
        inputSchema={"type": "object", "properties": {}}
    ),
]

# --- Flask Routes to expose MCP tools ---
@app.route('/mcp/list-tools', methods=['GET'])
def list_tools():
    """Exposes a route for Puch AI to discover the available tools."""
    return jsonify([tool.model_dump() for tool in tool_schemas])


@app.route('/mcp/call-tool', methods=['POST'])
def call_tool():
    """Exposes a route for Puch AI to call a specific tool."""
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

    elif name == "validate":
        bearer_token = request.headers.get("Authorization", "").replace("Bearer ", "")
        if bearer_token == POOCH_BEARER_TOKEN:
            return jsonify({"result": "+49491786525454"})  # ✅ correct format with "+"
        else:
            return jsonify({"error": "Invalid bearer token"}), 401

    return jsonify({"error": f"Unknown tool: {name}"}), 400


if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port)
