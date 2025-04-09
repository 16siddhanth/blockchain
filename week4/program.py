from Crypto.Cipher import AES
from Crypto.Util.Padding import pad, unpad
from Crypto.Random import get_random_bytes
from Crypto.Util import Counter
import hashlib
import time

class Block:
    def __init__(self, index, data, previous_hash):
        self.index = index
        self.timestamp = time.time()
        self.data = data  # encrypted data
        self.previous_hash = previous_hash
        self.hash = self.calculate_hash()

    def calculate_hash(self):
        block_string = f"{self.index}{self.timestamp}{self.data.hex()}{self.previous_hash}"
        return hashlib.sha256(block_string.encode()).hexdigest()

class Blockchain:
    def __init__(self):
        self.chain = [self.create_genesis_block()]

    def create_genesis_block(self):
        return Block(0, b'Genesis Block', '0')

    def add_block(self, data):
        prev_hash = self.chain[-1].hash
        new_block = Block(len(self.chain), data, prev_hash)
        self.chain.append(new_block)

    def print_chain(self):
        for block in self.chain:
            print(f"Index: {block.index}")
            print(f"Timestamp: {time.ctime(block.timestamp)}")
            print(f"Encrypted Data: {block.data.hex()}")
            print(f"Hash: {block.hash}")
            print(f"Previous Hash: {block.previous_hash}\n")

# ---------------------- AES MODES -------------------------

def encrypt_cbc(data, key):
    iv = get_random_bytes(16)
    cipher = AES.new(key, AES.MODE_CBC, iv)
    ct = cipher.encrypt(pad(data.encode(), AES.block_size))
    return iv + ct

def decrypt_cbc(data, key):
    iv = data[:16]
    ct = data[16:]
    cipher = AES.new(key, AES.MODE_CBC, iv)
    pt = unpad(cipher.decrypt(ct), AES.block_size)
    return pt.decode()

def encrypt_ctr(data, key):
    nonce = get_random_bytes(8)
    ctr = Counter.new(64, prefix=nonce)
    cipher = AES.new(key, AES.MODE_CTR, counter=ctr)
    ct = cipher.encrypt(data.encode())
    return nonce + ct

def decrypt_ctr(data, key):
    nonce = data[:8]
    ct = data[8:]
    ctr = Counter.new(64, prefix=nonce)
    cipher = AES.new(key, AES.MODE_CTR, counter=ctr)
    return cipher.decrypt(ct).decode()

def encrypt_ecb(data, key):
    cipher = AES.new(key, AES.MODE_ECB)
    ct = cipher.encrypt(pad(data.encode(), AES.block_size))
    return ct

def decrypt_ecb(data, key):
    cipher = AES.new(key, AES.MODE_ECB)
    pt = unpad(cipher.decrypt(data), AES.block_size)
    return pt.decode()

# ---------------------- DEMO -------------------------

if __name__ == "__main__":
    key = get_random_bytes(16)  # 128-bit AES key
    bc = Blockchain()

    # CBC mode transaction
    tx1 = "Alice pays Bob 5 BTC"
    enc1 = encrypt_cbc(tx1, key)
    bc.add_block(enc1)

    # CTR mode transaction
    tx2 = "Bob pays Charlie 10 BTC"
    enc2 = encrypt_ctr(tx2, key)
    bc.add_block(enc2)

    # ECB mode transaction
    tx3 = "Charlie pays Alice 15 BTC"
    enc3 = encrypt_ecb(tx3, key)
    bc.add_block(enc3)

    # Print full blockchain
    print("=== Blockchain with Encrypted Transactions ===\n")
    bc.print_chain()

    # Decrypting each block's data
    print("=== Decrypted Transactions ===\n")
    print("Block 1 (CBC):", decrypt_cbc(bc.chain[1].data, key))
    print("Block 2 (CTR):", decrypt_ctr(bc.chain[2].data, key))
    print("Block 3 (ECB):", decrypt_ecb(bc.chain[3].data, key))
