import os
import random
import threading
import time
from Vault import Vault
from Server import Server
from Crypto.Cipher import AES
from Crypto.Util.Padding import pad

class DeviceVault(threading.Thread):
    """
    Class representing a device that interacts with the server for authentication and vault synchronization.
    Implements a multi-step authentication protocol using vault-based challenges and AES encryption.
    """
    
    def __init__(self, device_id:int, server:Server, challenge_2_length:int, key_size:int, vault: Vault):
        super().__init__()
        self.device_id = device_id
        self.session_id = None
        self.server = server
        self.key_size = key_size
        self.vault = vault
        self.challenge_2_length = challenge_2_length
        self.authenticated = False
        self.encrypt_time = None
        self.decrypt_time = None
        self.vault_update_time = None
        


    def run(self):
        self.server.register_device(self)
        self.session_id = random.randint(1, 1000)
        if not self.server.is_valid_session(self.device_id, self.session_id):
            raise Exception("Invalid session.")

        print(f"Device {self.device_id} starting Challenge 1.")
        challenge1 = self.server.generate_challenge_1(self.device_id)
        if not challenge1:
            raise Exception("Failed to get Challenge 1 from server.")
        c1, r1 = challenge1

        print(f"Device {self.device_id} generating Challenge 2.")
        encrypt_start = time.time()
        k1 = self.vault.perform_xor_over_keys(c1)
        t1 = os.urandom(self.key_size)  # Device-generated 
        c2 = random.sample(range(len(self.vault.keys)), self.challenge_2_length)
        while c2 == c1:
            print(f"Device {self.device_id} generated duplicate c2, regenerating...")
            c2 = random.sample(range(len(self.vault.keys)), self.challenge_2_length)
        r2 = os.urandom(self.key_size)  # Device challenge 

        payload = r1 + t1 + bytes(c2) + r2
        encrypted_response = AES.new(k1, AES.MODE_ECB).encrypt(pad(payload, self.key_size))
        self.encrypt_time = time.time() - encrypt_start

        decrypt_start = time.time()
        if not self.server.validate_challenge_1(self.device_id, encrypted_response):
            raise Exception("Challenge 1 response validation failed.")

        print(f"Device {self.device_id} waiting for final response.")
        final_response = self.server.generate_final_response(self.device_id)
        if not final_response:
            raise Exception("Failed to get final response from server.")

        # Decrypt and validate final response
        print(f"Device {self.device_id} decrypting final response.")
        session_data = self.server.device_sessions.get(self.device_id)
        k2 = self.vault.perform_xor_over_keys(session_data['c2'])
        dynamic_key = bytes(a ^ b for a, b in zip(k2, t1))
        
        # Time decryption operation
        decrypted = AES.new(dynamic_key, AES.MODE_ECB).decrypt(final_response)
        self.decrypt_time = time.time() - decrypt_start
        
        print(f"Device {self.device_id} validating server response.")
        r2_received = decrypted[:16]
        if r2_received == r2:
            print(f"Device {self.device_id} authenticated successfully. Updating vault.")
            vault_start = time.time()
            self.server.synchronize_vault(self.device_id)
            self.vault_update_time = time.time() - vault_start
            self.authenticated = True

