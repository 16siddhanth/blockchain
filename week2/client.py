import requests

# The server address (adjust if needed)
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
    if response.status_code == 200:
        chain = response.json()
        print("Current Blockchain Ledger:")
        for block in chain:
            print(f"Block #{block['index']} - Hash: {block['previous_hash']} - Nonce: {block['nonce']}")
    else:
        print("Error fetching blockchain:", response.text)

if __name__ == "__main__":
    # Example usage: create a transaction, mine it, and then display the ledger.
    print("Creating transaction...")
    create_transaction("Alice", "Bob", 10)  # Example transaction
    print("Mining block...")
    mine_block()  # Mine the transaction
    print("Fetching blockchain...")
    get_blockchain()  # Display the blockchain
