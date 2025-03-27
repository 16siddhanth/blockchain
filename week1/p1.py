import hashlib
import time

# Define the Block class
class Block:
    def __init__(self, block_data, block_number, previous_hash=''):
        self.block_number = block_number  # Block number (index in the chain)
        self.header = f"Block #{self.block_number}"  # Block header now shows the block number
        self.previous_hash = previous_hash  # Previous block's hash
        self.timestamp = time.time()  # Unix timestamp
        self.nonce = 0  # Nonce for mining (Proof of Work)
        self.block_data = block_data  # List of transactions or data
        self.hash = self.calculate_hash()  # Hash of the current block (calculated)
        self.next_block = None  # Link to the next block in the chain (initially None)

    # Method to calculate hash of the block using sha256 from hashlib
    def calculate_hash(self):
        try:
            # Manually concatenate the block's data into a single string
            block_content = (str(self.block_number) + 
                             str(self.header) + 
                             str(self.previous_hash) + 
                             str(self.timestamp) + 
                             str(self.nonce) + 
                             str(self.block_data))
            # Return the SHA-256 hash of the concatenated string
            return hashlib.sha256(block_content.encode()).hexdigest()
        except Exception as e:
            raise RuntimeError("Error calculating hash") from e

    # Proof of Work to find a valid hash (with leading zeros)
    def mine_block(self, difficulty):
        target = '0' * difficulty  # Target hash should start with 'difficulty' number of 0s
        while not self.hash.startswith(target):
            self.nonce += 1  # Increment nonce to try and change the hash
            self.hash = self.calculate_hash()  # Recalculate hash with the new nonce

    def __str__(self):
        return (f"{self.header}\n"
                f"Previous Hash: {self.previous_hash}\n"
                f"Timestamp: {self.timestamp}\n"
                f"Nonce: {self.nonce}\n"
                f"Hash: {self.hash}\n"
                f"Block Data: {self.block_data}\n")


# Define the Blockchain class
class Blockchain:
    def __init__(self, difficulty=2):
        self.head = None  # Initially, no blocks are present
        self.tail = None  # Initially, no blocks are present
        self.difficulty = difficulty  # Difficulty level for mining (Proof of Work)
        self.block_number = 0  # Start with block number 0

    # Add a block to the blockchain
    def add_block(self, block_data):
        self.block_number += 1  # Increment block number for each new block
        if self.head is None:
            # First block (genesis block)
            new_block = Block(block_data, self.block_number)
            new_block.mine_block(self.difficulty)  # Mine the block to find a valid hash
            self.head = new_block
            self.tail = new_block
        else:
            # Add new block to the chain
            new_block = Block(block_data, self.block_number, self.tail.hash)
            new_block.mine_block(self.difficulty)  # Mine the block to find a valid hash
            self.tail.next_block = new_block  # Link the previous block to the new one
            self.tail = new_block  # Update the tail to the new block

    # Display the entire blockchain
    def display_chain(self):
        current_block = self.head
        while current_block:
            print(current_block)
            current_block = current_block.next_block


# Example usage
blockchain = Blockchain(difficulty=2)

# Adding blocks with some transaction data (could be any data, here using strings as placeholders)
blockchain.add_block(["Transaction 1: Alice -> Bob: 10 BTC", "Transaction 2: Bob -> Charlie: 5 BTC"])
blockchain.add_block(["Transaction 3: Charlie -> Alice: 2 BTC"])
blockchain.add_block(["Transaction 4: Bob -> Alice: 3 BTC"])

# Display the entire blockchain
blockchain.display_chain()
