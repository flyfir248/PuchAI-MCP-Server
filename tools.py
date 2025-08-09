import os
import sys
from dotenv import load_dotenv
from supabase import create_client, Client

# Supabase configuration
load_dotenv()
SUPABASE_URL = os.environ.get('SUPABASE_URL', '')
SUPABASE_KEY = os.environ.get('SUPABASE_KEY', '')
POOCH_BEARER_TOKEN = os.environ.get('POOCH_BEARER_TOKEN', '')

# Add a check to ensure the variables are loaded
if not SUPABASE_URL or not SUPABASE_KEY or not POOCH_BEARER_TOKEN:
    print("Error: Supabase or bearer token credentials not found in environment variables.")
    sys.exit(1)

supabase: Client = create_client(SUPABASE_URL, SUPABASE_KEY)

# --- New Validation Tool ---
def validate_user(bearer_token: str) -> str | None:
    """Authenticates the user with a bearer token and returns their phone number."""
    # For hackathon purposes, we check the token against an environment variable.
    if bearer_token == POOCH_BEARER_TOKEN:
        # The documentation specifies the format: {country_code}{number}
        return "9909241865" # Example phone number for India
    return None

# --- Tool Functions ---
def get_current_balance() -> float:
    """Gets the user's current financial balance from the database."""
    try:
        balance_result = supabase.table('balance_updates').select('amount').execute()
        total_added = sum(row['amount'] for row in balance_result.data) if balance_result.data else 0

        purchases_result = supabase.table('purchases').select('amount').execute()
        total_spent = sum(row['amount'] for row in purchases_result.data) if purchases_result.data else 0

        balance = total_added - total_spent
        return float(balance)
    except Exception as e:
        print(f"Error getting balance: {e}")
        return 0.0

def add_purchase(item_name: str, cost: float, category: str) -> str:
    """Adds a new purchase to the user's financial record in the database."""
    try:
        purchase_data = {'item_name': item_name, 'amount': cost, 'category': category}
        supabase.table('purchases').insert(purchase_data).execute()
        return f"Purchase of {item_name} for ₹{cost} in the {category} category added successfully."
    except Exception as e:
        print(f"Error adding purchase: {e}")
        return "An error occurred while adding the purchase."