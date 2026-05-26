import json
import os

DATA_FILE = "balances.json"

def load_balances():
    if not os.path.exists(DATA_FILE):
        return {}
    with open(DATA_FILE, "r") as f:
        return json.load(f)

def save_balances(balances):
    with open(DATA_FILE, "w") as f:
        json.dump(balances, f, indent=4)

def get_balance(user_id):
    balances = load_balances()
    return balances.get(str(user_id), 1000) # Start with 1000

def update_balance(user_id, amount):
    balances = load_balances()
    user_id = str(user_id)
    balances[user_id] = balances.get(user_id, 1000) + amount
    save_balances(balances)
    return balances[user_id]
