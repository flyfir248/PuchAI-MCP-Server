# mcp_server.py - Fixed for Puch AI compatibility
import os
from flask import Flask, request, jsonify
from mcp.types import Tool
from tools import get_current_balance, add_purchase
from dotenv import load_dotenv

load_dotenv()

# Get auth token and phone number from .env
AUTH_TOKEN = os.environ.get("AUTH_TOKEN", "")
MY_NUMBER = os.environ.get("MY_NUMBER", "")

# Flask application setup
app = Flask(__name__)


# Enable CORS for MCP
@app.after_request
def after_request(response):
    response.headers.add('Access-Control-Allow-Origin', '*')
    response.headers.add('Access-Control-Allow-Headers', 'Content-Type,Authorization')
    response.headers.add('Access-Control-Allow-Methods', 'GET,PUT,POST,DELETE,OPTIONS')
    return response


# --------------------
# Root Health Check
# --------------------
@app.route('/', methods=['GET', 'HEAD', 'POST'])
def health():
    if request.method == 'POST':
        # Handle POST requests that might be MCP calls
        return handle_mcp_request()
    return jsonify({"status": "MCP server running", "version": "1.0"}), 200


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
# MCP Request Handler
# --------------------
def handle_mcp_request():
    try:
        data = request.json
        if not data:
            return jsonify({"error": "No JSON data provided"}), 400

        # Handle different MCP request types
        if 'method' in data:
            method = data.get('method')
            if method == 'tools/list':
                return jsonify({
                    "jsonrpc": "2.0",
                    "id": data.get('id'),
                    "result": {"tools": [tool.model_dump() for tool in tool_schemas]}
                })
            elif method == 'tools/call':
                params = data.get('params', {})
                return handle_tool_call(params, data.get('id'))

        # Fallback to direct tool calling
        return call_tool()
    except Exception as e:
        return jsonify({"error": str(e)}), 500


def handle_tool_call(params, request_id):
    name = params.get('name')
    arguments = params.get('arguments', {})

    try:
        if name == "validate":
            bearer_token = arguments.get("bearer_token")
            if bearer_token == AUTH_TOKEN:
                return jsonify({
                    "jsonrpc": "2.0",
                    "id": request_id,
                    "result": {"content": [{"type": "text", "text": MY_NUMBER}]}
                })
            else:
                return jsonify({
                    "jsonrpc": "2.0",
                    "id": request_id,
                    "error": {"code": -32602, "message": "Invalid bearer token"}
                }), 401

        elif name == "get_current_balance":
            balance = get_current_balance()
            return jsonify({
                "jsonrpc": "2.0",
                "id": request_id,
                "result": {"content": [{"type": "text", "text": f"💰 Current Balance: ₹{balance:.2f}"}]}
            })

        elif name == "add_purchase":
            result = add_purchase(
                item_name=arguments.get("item_name"),
                cost=arguments.get("cost"),
                category=arguments.get("category")
            )
            return jsonify({
                "jsonrpc": "2.0",
                "id": request_id,
                "result": {"content": [{"type": "text", "text": result}]}
            })

        return jsonify({
            "jsonrpc": "2.0",
            "id": request_id,
            "error": {"code": -32601, "message": f"Unknown tool: {name}"}
        }), 400

    except Exception as e:
        return jsonify({
            "jsonrpc": "2.0",
            "id": request_id,
            "error": {"code": -32603, "message": str(e)}
        }), 500


# --------------------
# List Tools Endpoint
# --------------------
@app.route('/mcp/list-tools', methods=['GET'])
def list_tools():
    return jsonify({"tools": [tool.model_dump() for tool in tool_schemas]})


# --------------------
# Tool Caller Endpoint (Legacy support)
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
            # Return just the phone number as plain text for Puch AI
            return MY_NUMBER, 200, {'Content-Type': 'text/plain'}
        else:
            return jsonify({"error": "Invalid bearer token"}), 401

    return jsonify({"error": f"Unknown tool: {name}"}), 400


# --------------------
# Server Entry Point
# --------------------
if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port, debug=True)