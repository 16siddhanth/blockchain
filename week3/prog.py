import socket
import threading
import time
import json
import hashlib
import os

# =============================================================================
# Blockchain Components
# =============================================================================

class Block:
    def __init__(self, index, timestamp, data, previous_hash, node_id, hash=None):
        self.index = index
        self.timestamp = timestamp
        self.data = data
        self.previous_hash = previous_hash
        self.node_id = node_id
        self.hash = hash if hash is not None else self.calculate_hash()

    def calculate_hash(self):
        block_string = f"{self.index}{self.previous_hash}{self.timestamp}{json.dumps(self.data, sort_keys=True)}{self.node_id}".encode()
        return hashlib.sha256(block_string).hexdigest()

class Blockchain:
    def __init__(self):
        self.chain = []
        self.load_chain_from_file()  # Load existing chain from file or create genesis block

    def create_genesis_block(self):
        return Block(0, time.time(), {"action": "patient_visit", "message": "Genesis block: New patient visit at hospital"}, "0", "hospital_node")

    def load_chain_from_file(self):
        if os.path.exists("blockchain_ledger.json"):
            with open("blockchain_ledger.json", "r") as f:
                blocks_data = json.load(f)
                self.chain = [Block(**block) for block in blocks_data]
        else:
            # If the file does not exist, create the genesis block
            genesis_block = self.create_genesis_block()
            self.chain.append(genesis_block)
            self.save_chain_to_file()  # Save the genesis block to file

    def get_last_block(self):
        return self.chain[-1]

    def add_block(self, data, node_id):
        last_block = self.get_last_block()
        new_block = Block(last_block.index + 1, time.time(), data, last_block.hash, node_id)
        self.chain.append(new_block)
        self.save_chain_to_file()  # Save the updated chain to a file
        return new_block

    def save_chain_to_file(self):
        with open("blockchain_ledger.json", "w") as f:
            json.dump([block.__dict__ for block in self.chain], f, indent=4)

    def get_full_chain(self):
        return {
            "status": "success",
            "chain": [block.__dict__ for block in self.chain]
        }

# Global user data
users = {
    "doctor": {"password": "doc123", "balance": 0},
    "diagnostic": {"password": "diag123", "balance": 0},
    "pharmacy": {"password": "pharm123", "balance": 0},
    "hospital": {"password": "hosp123"},
    "patient1": {"patient_id": "patient1", "password": "pat123"},  # Example patient
}

# Lock for accessing and modifying the blockchain and user data
blockchain_lock = threading.Lock()
user_data_lock = threading.Lock()

# =============================================================================
# Node Server to Handle Logins, Blockchain Operations, and Incentives
# =============================================================================

class NodeServer(threading.Thread):
    def __init__(self, host, port, node_id):
        threading.Thread.__init__(self)
        self.host = host
        self.port = port
        self.node_id = node_id
        self.blockchain = Blockchain()
        self.server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.server_socket.bind((host, port))
        self.server_socket.listen(5)
        print(f"{self.node_id} Node Server running on {host}:{port}")

    def run(self):
        while True:
            client, address = self.server_socket.accept()
            threading.Thread(target=self.handle_client, args=(client, address)).start()

    def handle_client(self, client, address):
        try:
            data = client.recv(4096).decode()
            if not data:
                client.close()
                return

            request = json.loads(data)
            response = {}

            if request["action"] == "login":
                username = request["username"]
                password = request["password"]

                # Check if the user is a patient
                if username.startswith("patient"):
                    if username in users and users[username]["password"] == password:
                        response["status"] = "success"
                        response["message"] = f"{username} logged in successfully."
                    else:
                        response["status"] = "failure"
                        response["message"] = "Invalid patient ID or password."
                else:
                    # Existing login logic for doctors, diagnostics, and pharmacies
                    if username in users and users[username]["password"] == password:
                        response["status"] = "success"
                        response["message"] = f"{username} logged in successfully."
                    else:
                        response["status"] = "failure"
                        response["message"] = "Invalid credentials."

            elif request["action"] == "add_block":
                with blockchain_lock:
                    block_data = request["data"]
                    new_block = self.blockchain.add_block(block_data, self.node_id)

                    # Incentive updates
                    with user_data_lock:
                        if block_data.get("action") == "blood_test":
                            doctor = block_data.get("doctor")
                            if doctor in users:
                                users[doctor]["balance"] += 10
                        elif block_data.get("action") == "report":
                            diagnostic = block_data.get("diagnostic")
                            if diagnostic in users:
                                users[diagnostic]["balance"] += 5
                        elif block_data.get("action") == "prescription":
                            doctor = block_data.get("doctor")
                            if doctor in users:
                                users[doctor]["balance"] += 5
                        elif block_data.get("action") == "medicine_purchase":
                            pass

                    response["status"] = "success"
                    response["message"] = f"Block added by {self.node_id} with index {new_block.index}."

            elif request["action"] == "get_chain":
                with blockchain_lock:
                    response = self.blockchain.get_full_chain()

            elif request["action"] == "get_balance":
                user = request.get("user")
                with user_data_lock:
                    if user in users and "balance" in users[user]:
                        response["status"] = "success"
                        response["balance"] = users[user]["balance"]
                    else:
                        response["status"] = "failure"
                        response["message"] = "User not found or no balance attribute."

            client.send(json.dumps(response).encode())

        except Exception as e:
            error_response = {"status": "error", "message": str(e)}
            client.send(json.dumps(error_response).encode())
        finally:
            client.close()

    def get_user_role(self, username):
        if username in users:
            for role, data in users.items():
                if username == role:
                    return role
        return None

# =============================================================================
# Client Utility Function to Interact with the Node
# =============================================================================

def send_request(host, port, request):
    try:
        s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        s.connect((host, port))
        s.send(json.dumps(request).encode())
        response = s.recv(4096).decode()
        s.close()
        return json.loads(response)
    except ConnectionRefusedError:
        print(f"Error: Could not connect to the node at {host}:{port}. Make sure the server is running.")
        return {"status": "error", "message": "Connection refused"}
    except Exception as e:
        print(f"An error occurred during the request: {e}")
        return {"status": "error", "message": str(e)}

# =============================================================================
# Workflow Simulation with Interactive Login for All Parties (Simulating Different Nodes)
# =============================================================================

def main():
    central_node_host = "127.0.0.1"
    central_node_port = 5000

    # Start the distributed node servers
    nodes = {
        "doctor": NodeServer(central_node_host, central_node_port + 1, "doctor_node"),
        "diagnostic": NodeServer(central_node_host, central_node_port + 2, "diagnostic_node"),
        "pharmacy": NodeServer(central_node_host, central_node_port + 3, "pharmacy_node"),
        "hospital": NodeServer(central_node_host, central_node_port + 4, "hospital_node"),
    }

    for node in nodes.values():
        node.daemon = True
        node.start()
        time.sleep(1)

    # Simulate patient visit and genesis block creation (handled by the hospital node on initial setup)
    print("\n--- System Start: Genesis Block Created on Patient Visit ---")
    print(json.dumps(nodes["hospital"].blockchain.chain[0].__dict__, indent=4))
    print("-" * 50)

    # -----------------------------------------------------------------------------
    # 1. Doctor logs in from their node.
    # -----------------------------------------------------------------------------
    print("\n--- Doctor Login ---")
    doctor_username = input("Enter doctor username: ")
    doctor_password = input("Enter doctor password: ")
    login_req_doctor = {
        "action": "login",
        "username": doctor_username,
        "password": doctor_password
    }
    doctor_login_response = send_request(central_node_host, central_node_port + 1, login_req_doctor)
    print("Doctor login response:", doctor_login_response)

    if doctor_login_response.get("status") == "success":
        # Doctor orders a blood test
        patient_id = input("Enter patient ID for the blood test: ")
        blood_test_req = {
            "action": "add_block",
            "data": {
                "action": "blood_test",
                "patient_id": patient_id,
                "doctor": doctor_username,
                "details": "Doctor ordered a blood test."
            }
        }
        print("Adding blood test order:", send_request(central_node_host, central_node_port + 1, blood_test_req))

    # -----------------------------------------------------------------------------
    # 2. Diagnostic center logs in from their node and adds the report.
    # -----------------------------------------------------------------------------
    print("\n--- Diagnostic Center Login ---")
    diag_username = input("Enter diagnostic center username: ")
    diag_password = input("Enter diagnostic center password: ")
    login_req_diag = {
        "action": "login",
        "username": diag_username,
        "password": diag_password
    }
    diag_login_response = send_request(central_node_host, central_node_port + 2, login_req_diag)
    print("Diagnostic center login response:", diag_login_response)

    if diag_login_response.get("status") == "success":
        patient_id = input("Enter patient ID for the report: ")
        blood_report_req = {
            "action": "add_block",
            "data": {
                "action": "report",
                "patient_id": patient_id,
                "diagnostic": diag_username,
                "report": "Blood test results are normal."
            }
        }
        print("Adding blood test report:", send_request(central_node_host, central_node_port + 2, blood_report_req))

    # -----------------------------------------------------------------------------
    # 3. Doctor logs in again (or is already logged in) and writes a prescription.
    # -----------------------------------------------------------------------------
    if doctor_login_response.get("status") == "success":
        print("\n--- Doctor Writes Prescription ---")
        patient_id = input("Enter patient ID for the prescription: ")
        prescription_req = {
            "action": "add_block",
            "data": {
                "action": "prescription",
                "patient_id": patient_id,
                "doctor": doctor_username,
                "prescription": "Patient prescribed vitamin supplements."
            }
        }
        print("Adding prescription:", send_request(central_node_host, central_node_port + 1, prescription_req))

    # -----------------------------------------------------------------------------
    # 4. Pharmacy logs in from their node and processes the medicine purchase.
    # -----------------------------------------------------------------------------
    print("\n--- Pharmacy Login ---")
    pharm_username = input("Enter pharmacy username: ")
    pharm_password = input("Enter pharmacy password: ")
    login_req_pharm = {
        "action": "login",
        "username": pharm_username,
        "password": pharm_password
    }
    pharm_login_response = send_request(central_node_host, central_node_port + 3, login_req_pharm)
    print("Pharmacy login response:", pharm_login_response)

    if pharm_login_response.get("status") == "success":
        patient_id = input("Enter patient ID for medicine purchase: ")
        medicine_purchase_req = {
            "action": "add_block",
            "data": {
                "action": "medicine_purchase",
                "patient_id": patient_id,
                "doctor": doctor_username,
                "pharmacy": pharm_username,
                "details": "Patient purchased prescribed medicines."
            }
        }
        print("Adding medicine purchase:", send_request(central_node_host, central_node_port + 3, medicine_purchase_req))

    # -----------------------------------------------------------------------------
    # 5. Patient logs in and checks their balance.
    # -----------------------------------------------------------------------------
    print("\n--- Patient Login ---")
    patient_id = input("Enter patient ID: ")
    patient_password = input("Enter patient password: ")
    login_req_patient = {
        "action": "login",
        "username": f"{patient_id}",  # Patient ID
        "password": patient_password     # Password
    }
    patient_login_response = send_request(central_node_host, central_node_port + 4, login_req_patient)
    print("Patient login response:", patient_login_response)

    if patient_login_response.get("status") == "success":
        print(f"Welcome, {patient_id}!")

    # -----------------------------------------------------------------------------
    # 6. Display the updated blockchain and incentive balances.
    # -----------------------------------------------------------------------------
    print("\n--- Current Blockchain Ledger ---")
    # Request the chain from the pharmacy node (port 5003) to see all blocks added in this simulation.
    get_chain_req = {"action": "get_chain"}
    chain_response = send_request(central_node_host, central_node_port + 3, get_chain_req)
    print(json.dumps(chain_response, indent=4))

    print("\n--- Incentive Balances ---")
    balance_req_doctor = {"action": "get_balance", "user": doctor_username}
    print(f"Doctor ({doctor_username}) balance:", send_request(central_node_host, central_node_port + 1, balance_req_doctor))

    balance_req_diag = {"action": "get_balance", "user": diag_username}
    print(f"Diagnostic center ({diag_username}) balance:", send_request(central_node_host, central_node_port + 2, balance_req_diag))

    # Keep the main thread alive to allow the node servers to continue running
    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        print("Stopping the nodes...")

if __name__ == "__main__":
    main()
