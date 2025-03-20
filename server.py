from hashlib import sha256
import json
import time
import os
from flask import Flask, request, jsonify

# Define a Block class that holds transactions and metadata.
class Block:
    def __init__(self, index, transactions, timestamp, previous_hash, nonce=0):
        self.index = index
        self.transactions = transactions
        self.timestamp = timestamp
        self.previous_hash = previous_hash
        self.nonce = nonce

    def compute_hash(self):
        # Create a SHA-256 hash of the block's content.
        block_string = json.dumps(self.__dict__, sort_keys=True)
        return sha256(block_string.encode()).hexdigest()

# Define the Blockchain class that manages chain and mining.
class Blockchain:
    difficulty = 2  # mining difficulty (leading zeros)
    blockchain_file = "blockchain.json"  # File where blockchain is stored

    def __init__(self):
        self.unconfirmed_transactions = []  # Transactions waiting to be mined
        self.chain = []  # The actual blockchain
        self.load_chain()

    def load_chain(self):
        # Load the blockchain from a file, or create a new one if it doesn't exist.
        if os.path.exists(self.blockchain_file):
            with open(self.blockchain_file, 'r') as file:
                blockchain_data = json.load(file)
                for block_data in blockchain_data:
                    block = Block(**block_data)
                    self.chain.append(block)
        else:
            self.create_genesis_block()

    def create_genesis_block(self):
        # Create the first block with no transactions.
        genesis_block = Block(0, [], time.time(), "0")
        genesis_block.hash = genesis_block.compute_hash()
        self.chain.append(genesis_block)
        self.save_chain()

    def save_chain(self):
        # Save the blockchain to the file.
        with open(self.blockchain_file, 'w') as file:
            json.dump([block.__dict__ for block in self.chain], file, indent=4)

    @property
    def last_block(self):
        # Return the last block in the blockchain.
        return self.chain[-1]

    def proof_of_work(self, block):
        # Perform a simple proof-of-work algorithm.
        block.nonce = 0
        computed_hash = block.compute_hash()
        while not computed_hash.startswith('0' * Blockchain.difficulty):
            block.nonce += 1
            computed_hash = block.compute_hash()
        return computed_hash

    def add_block(self, block, proof):
        # Validate the block's previous hash and the proof-of-work.
        previous_hash = self.last_block.compute_hash()
        if previous_hash != block.previous_hash:
            return False
        if not proof.startswith('0' * Blockchain.difficulty) or proof != block.compute_hash():
            return False
        self.chain.append(block)
        self.save_chain()  # Save the blockchain after adding a new block
        return True

    def add_new_transaction(self, transaction):
        # Add a new transaction to the unconfirmed transactions list.
        self.unconfirmed_transactions.append(transaction)

    def mine(self):
        # Mine unconfirmed transactions if available.
        if not self.unconfirmed_transactions:
            return False
        last_block = self.last_block
        new_block = Block(
            index=last_block.index + 1,
            transactions=self.unconfirmed_transactions,
            timestamp=time.time(),
            previous_hash=last_block.compute_hash()
        )
        proof = self.proof_of_work(new_block)
        self.add_block(new_block, proof)
        self.unconfirmed_transactions = []  # Reset the transaction pool
        return new_block.index

# Initialize the Flask application and our Blockchain instance.
app = Flask(__name__)
blockchain = Blockchain()

# Endpoint to add a new transaction.
@app.route('/new_transaction', methods=['POST'])
def new_transaction():
    tx_data = request.get_json()
    required_fields = ["sender", "receiver", "amount"]
    if not all(field in tx_data for field in required_fields):
        return "Invalid transaction data", 400
    blockchain.add_new_transaction(tx_data)
    return "Transaction added", 201

# Endpoint to mine a block (i.e. add unconfirmed transactions to the blockchain).
@app.route('/mine', methods=['GET'])
def mine_unconfirmed_transactions():
    result = blockchain.mine()
    if not result:
        return "No transactions to mine", 200
    return f"Block #{result} is mined.", 200

# Endpoint to return the entire blockchain ledger.
@app.route('/chain', methods=['GET'])
def get_chain():
    chain_data = []
    for block in blockchain.chain:
        # Convert block objects to dict for JSON serialization.
        chain_data.append(block.__dict__)
    return jsonify(chain_data), 200

# Start the Flask app and listen on port 5000
if __name__ == '__main__':
    app.run(port=5000)
