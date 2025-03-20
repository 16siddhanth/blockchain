import requests
import json

# Change the server_address (and port) as needed.
server_address = "http://127.0.0.1:5000"

def create_transaction(sender, receiver, amount):
    tx_data = {
        "sender": sender,
        "receiver": receiver,
        "amount": amount
    }
    response = requests.post(f"{server_address}/new_transaction", json=tx_data)
    print("Transaction response:", response.text)

def mine_block():
    response = requests.get(f"{server_address}/mine")
    print("Mining response:", response.text)

def get_blockchain():
    response = requests.get(f"{server_address}/chain")
    chain = response.json()
    print("Current Blockchain Ledger:")
    print(json.dumps(chain, indent=4))

if __name__ == "__main__":
    # Example usage: create a transaction, mine it, and then display the ledger.
    create_transaction("Alice", "Bob", 10)
    mine_block()
    get_blockchain()
