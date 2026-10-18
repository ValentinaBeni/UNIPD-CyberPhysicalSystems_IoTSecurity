
import hashlib
import os 
import hmac

class Vault:
    """
    Class representing secure cryptographic key storage and management system.
    Implements dynamic key updates using HMAC-based key derivation
    """
    
    def __init__(self, number_of_keys:int, key_size:int) -> None:
        """
        Initialize vault with random cryptographic keys
        Args:
            number_of_keys (int): Number of keys to generate
            key_size (int): Size of each key in bytes
        """
        self.keys = [os.urandom(key_size) for _ in range(number_of_keys)]


    def perform_xor_over_keys(self, index_list) -> bytes:
        """
        Combine multiple keys using XOR operation
        Args:
            index_list (list): List of key indexes
        """
        if not index_list:
            raise ValueError("index_list is empty.")
        
        key = self.keys[index_list[0]]

        for idx in index_list[1:]:
            key = bytes(a ^ b for a, b in zip(key, self.keys[idx]))

        return key


    def update_keys(self, data) -> None:
        """
        Update all keys in the vault using HMAC-based key derivation
        
        Args:
            data (bytes): Input data for key update derivation
        """

        if not self.keys:
            raise IndexError("There are no keys in the vault.")
        
        if not data:
            raise ValueError("The input 'data' cannot be empty.")

        message = b''.join(self.keys)
        h = hmac.new(data, message, hashlib.sha256).digest()
        
        chunk_size = len(self.keys[0])
        partitions = [h[i : i + chunk_size] for i in range(0, len(h), chunk_size)]
        
        for i in range(len(self.keys)):
            self.keys[i] = bytes(a ^ b for a, b in zip(self.keys[i], partitions[i % len(partitions)]))

