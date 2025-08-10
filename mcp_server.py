# mcp_server.py
import os
from flask import Flask, request, jsonify
from mcp.types import Tool
from tools import get_current_balance, add_purchase
from dotenv import load_dotenv

load_dotenv()

AUTH_TOKEN = os.environ.get("AUTH_TOKEN", "")
MY_NUMBER = os.environ.get("MY_NUMBER", "")

app = Flask(__name__)

# --------------------
# Root Health Check
# --------------------
@app.route('/', methods=['GET', 'HEAD'])
def health():
    return jsonify({"status": "MCP server running"}), 200

# --------------------
# MCP Tool Definitions
# --------------------
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
                "item_name": {"type": "string", "description": "Name of the item purchased."},
                "cost": {"type": "number", "description": "Cost of the item."},
                "category": {"type": "string", "description": "Category of the purchase."}
            },
            "required": ["item_name", "cost", "category"],
        }
    ),
    Tool(
        name="validate",
        description="Validates the MCP server connection and returns the owner's phone number.",
        inputSchema={
            "type": "object",
            "properties": {
                "bearer_token": {"type": "string", "description": "The bearer token for authentication."}
            },
            "required": ["bearer_token"],
        }
    ),
]

# --------------------
# List Tools Endpoint
# --------------------
@app.route('/mcp/list-tools', methods=['GET'])
def list_tools():
    return jsonify([tool.model_dump() for tool in tool_schemas])

# --------------------
# Tool Caller Endpoint
# --------------------
@app.route('/mcp/call-tool', methods=['POST'])
def call_tool():
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
        bearer_token = arguments.get("bearer_token")
        if bearer_token == AUTH_TOKEN:
            return MY_NUMBER
        else:
            return jsonify({"error": "Invalid bearer token"}), 401

    return jsonify({"error": f"Unknown tool: {name}"}), 400

# --------------------
# Server Entry Point
# --------------------

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port)