# mcp_server.py - Minimal working version
import os
from flask import Flask, request, jsonify
from tools import get_current_balance, add_purchase
from dotenv import load_dotenv

load_dotenv()

AUTH_TOKEN = os.environ.get("AUTH_TOKEN", "")
MY_NUMBER = os.environ.get("MY_NUMBER", "")

app = Flask(__name__)


@app.after_request
def after_request(response):
    response.headers.add('Access-Control-Allow-Origin', '*')
    response.headers.add('Access-Control-Allow-Headers', 'Content-Type,Authorization')
    response.headers.add('Access-Control-Allow-Methods', 'GET,PUT,POST,DELETE,OPTIONS')
    return response


@app.route('/', methods=['GET', 'HEAD', 'POST', 'OPTIONS'])
def root():
    if request.method == 'OPTIONS':
        return '', 200

    if request.method == 'POST':
        try:
            data = request.json or {}

            # Handle MCP validation request
            if data.get('name') == 'validate' or 'validate' in str(data):
                bearer_token = data.get('arguments', {}).get('bearer_token') or data.get('bearer_token')
                if bearer_token == AUTH_TOKEN:
                    # Return phone number as plain text
                    return MY_NUMBER, 200, {'Content-Type': 'text/plain'}
                else:
                    return jsonify({"error": "Invalid token"}), 401

            # Handle other tool calls
            name = data.get('name', '')
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

        except Exception as e:
            return jsonify({"error": str(e)}), 500

    return jsonify({"status": "MCP server running", "version": "1.0"}), 200


@app.route('/mcp/list-tools', methods=['GET'])
def list_tools():
    tools = [
        {
            "name": "get_current_balance",
            "description": "Gets the user's current financial balance.",
            "inputSchema": {"type": "object", "properties": {}}
        },
        {
            "name": "add_purchase",
            "description": "Adds a new purchase to the user's financial record.",
            "inputSchema": {
                "type": "object",
                "properties": {
                    "item_name": {"type": "string", "description": "Name of the item purchased."},
                    "cost": {"type": "number", "description": "Cost of the item."},
                    "category": {"type": "string", "description": "Category of the purchase."}
                },
                "required": ["item_name", "cost", "category"]
            }
        },
        {
            "name": "validate",
            "description": "Validates the MCP server connection and returns the owner's phone number.",
            "inputSchema": {
                "type": "object",
                "properties": {
                    "bearer_token": {"type": "string", "description": "The bearer token for authentication."}
                },
                "required": ["bearer_token"]
            }
        }
    ]
    return jsonify({"tools": tools})


@app.route('/mcp/call-tool', methods=['POST'])
def call_tool():
    return root()  # Delegate to root handler


@app.route('/validate', methods=['POST'])
def validate_endpoint():
    data = request.json or {}
    bearer_token = data.get('bearer_token') or data.get('arguments', {}).get('bearer_token')

    if bearer_token == AUTH_TOKEN:
        return MY_NUMBER, 200, {'Content-Type': 'text/plain'}
    else:
        return jsonify({"error": "Invalid bearer token"}), 401


if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    print(f"Starting MCP server on port {port}")
    print(f"Auth token configured: {'Yes' if AUTH_TOKEN else 'No'}")
    print(f"Phone number configured: {'Yes' if MY_NUMBER else 'No'}")
    app.run(host="0.0.0.0", port=port, debug=True)