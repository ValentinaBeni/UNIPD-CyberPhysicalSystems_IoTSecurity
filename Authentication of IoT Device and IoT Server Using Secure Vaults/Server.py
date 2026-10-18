from typing import Tuple
import os
import random
import threading
import time
from Crypto.Cipher import AES
from Crypto.Util.Padding import pad
from ecdsa import VerifyingKey
from DeviceECC import DeviceECC

class Server(threading.Thread):
    """
    Class representing the server responsible for device authentication and vault synchronization.
    Implements a multi-step authentication protocol using ECC signatures and vault-based challenges.
    """

    def __init__(self, challenge_1_length:int=0, key_size:int=0):
        super().__init__()
        self.device_vaults = {}
        self.device_sessions = {}
        self.challenge_1_length = challenge_1_length
        self.key_size = key_size
        self.lock = threading.Lock()
        self.registered_devices = {}


    def register_device(self, device: DeviceECC, public_key_pem=None) -> None:
        print("--------------------------------------------------------------")
        print(f"Server registering device {device.device_id}.")
        with self.lock:
            if public_key_pem: # Register device with public key for ECC authentication
                public_key = VerifyingKey.from_pem(public_key_pem)
                self.registered_devices[device.device_id] = {"public_key": public_key, "auth_duration": 0.0}
            else: # Register device without public key for vault-based authentication
                self.device_vaults[device.device_id] = device.vault


    def is_signature_valid_ECC(self, device_id, key, signature) -> bool:
        if device_id not in self.registered_devices:
            print(f"Device {device_id} not registered for ECC authentication.")
            return False
        
        public_key = self.registered_devices[device_id]["public_key"]
        start_time = time.time()
        
        try:
            result = public_key.verify(signature, key)
        except Exception:
            print(f"Device {device_id} provided an invalid signature.")
            result = False
            
        self.registered_devices[device_id]["auth_duration"] = time.time() - start_time
        return result, self.registered_devices[device_id]["auth_duration"]


    def is_valid_session(self, device_id, session_id) -> bool:
        with self.lock:
            if session_id > 0 and device_id in self.device_vaults:
                self.device_sessions[device_id] = {
                    'vault': self.device_vaults[device_id],
                    'session_id': session_id
                }
                return True
        return False


    def generate_challenge_1(self, device_id) -> Tuple[list, bytes]:
        print(f"Server generating Challenge 1 for device {device_id}.")
        with self.lock:
            session = self.device_sessions.get(device_id)
            if not session:
                raise Exception("Invalid session for device.")
            
            # Select random keys for challenge
            vault = session['vault']
            c1 = random.sample(range(len(vault.keys)), self.challenge_1_length)
            r1 = os.urandom(self.key_size)  

            session.update({'c1': c1, 'r1': r1})
            return (c1, r1)


    def validate_challenge_1(self, device_id, encrypted_response) -> bool:
        print(f"Server validating Challenge 1 response for device {device_id}.")
        with self.lock:
            session = self.device_sessions.get(device_id)
            if not session:
                return False
            
            vault = session['vault']
            c1 = session['c1']
            r1 = session['r1']

            k1 = vault.perform_xor_over_keys(c1)
            decrypted_response = AES.new(k1, AES.MODE_ECB).decrypt(encrypted_response)
            
            r1_received = decrypted_response[:16]
            t1 = decrypted_response[16:32]
            c2 = list(decrypted_response[32:35])
            r2 = decrypted_response[35:51]

            if r1_received != r1:
                return False

            session.update({'c2': c2, 'r2': r2, 't1': t1})
            return True


    def generate_final_response(self, device_id) -> bytes:
        print(f"Server generating final response for device {device_id}.")
        with self.lock:
            session = self.device_sessions.get(device_id)
            if not session:
                raise Exception("Invalid session for device.")
            
            # Retrieve session parameters
            vault = session['vault']
            c2 = session['c2']
            r2 = session['r2']
            t1 = session['t1']

            # Create dynamic session key
            k2 = vault.perform_xor_over_keys(c2)
            dynamic_key = bytes(a ^ b for a, b in zip(k2, t1))
            
            # Encrypt final response
            t2 = os.urandom(16)  # Server-generated nonce
            payload = r2 + t2
            encrypted = AES.new(dynamic_key, AES.MODE_ECB).encrypt(pad(payload, 16))
            
            session['t2'] = t2
            return encrypted


    def synchronize_vault(self, device_id) -> None:
        print(f"Server synchronizing vault for device {device_id}.")
        with self.lock:
            session = self.device_sessions.get(device_id)
            if not session:
                return
            
            # Update vault with session nonces
            vault = session['vault']
            r1 = session['r1']
            r2 = session['r2']
            vault.update_keys(r1 + r2)
            
            # Synchronize updated vault
            self.device_vaults[device_id] = vault

