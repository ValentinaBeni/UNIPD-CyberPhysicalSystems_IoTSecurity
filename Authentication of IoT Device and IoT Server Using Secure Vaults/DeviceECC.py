from typing import Tuple
import os
import threading
import time
from ecdsa import NIST256p, SigningKey

class DeviceECC(threading.Thread):
    """
    Class representing a device that uses ECC for authentication with the server.
    Implements key generation, signing, and verification using ECC signatures.
    """

    def __init__(self, device_id, server):
        super().__init__()
        self.device_id = device_id
        self.server = server
        self.private_key = SigningKey.generate(curve=NIST256p)
        self.public_key = self.private_key.verifying_key
        self.status = None
        self.key_gen_time = None
        self.sign_time = None
        self.verify_time = None


    def get_public_key(self) -> bytes:
        return self.public_key.to_pem()


    def sign_key(self, key) -> Tuple[bytes, float]:
        start_time = time.time()
        sign = self.private_key.sign(key)
        sign_time = time.time() - start_time
        return sign, sign_time
    

    def run(self) -> None:
        self.server.register_device(self, self.get_public_key())

        start_time = time.time()
        key = os.urandom(32)
        key_gen_time = time.time() - start_time
        print(f"Device {self.device_id} generated key in {key_gen_time*1000:.4f} ms.")

        signature, signature_time = self.sign_key(key)
        print(f"Device {self.device_id} signed key in {signature_time*1000:.4f} ms.")

        verification_result, verification_time = self.server.is_signature_valid_ECC(self.device_id, key, signature)
        self.status = "Success" if verification_result else "Failed"
        print(f"Device {self.device_id} authentication status: {self.status}.")
        print(f"Device {self.device_id} verification time: {verification_time*1000:.4f} ms.")

        self.key_gen_time = key_gen_time
        self.sign_time = signature_time
        self.verify_time = verification_time
