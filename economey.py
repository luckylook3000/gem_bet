import json
import os
import random
import discord

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
    return balances.get(str(user_id), 1000) # Default 1000 coins

def update_balance(user_id, amount):
    balances = load_balances()
    user_id = str(user_id)
    balances[user_id] = balances.get(user_id, 1000) + amount
    save_balances(balances)
    return balances[user_id]

# Promo Codes
PROMO_CODES = {"GEMBET100": 100, "KING": 500, "WINNER": 200}
USED_CODES = set() 
