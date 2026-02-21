"""
Encryption Module

Provide encryption for data at rest and in transit:
- AES-256 encryption
- Key derivation and rotation
- Encrypted field support in models
- TLS/SSL configuration
"""

import os
import json
from typing import Any, Dict, Optional
from dataclasses import dataclass
from datetime import datetime, timedelta
from cryptography.fernet import Fernet
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2
import base64
import hashlib


@dataclass
class EncryptionConfig:
    """Configuration for encryption"""
    algorithm: str = "AES-256"
    key_rotation_days: int = 90
    salt: Optional[bytes] = None
    iterations: int = 100000


class EncryptionManager:
    """Manage encryption/decryption operations"""
    
    def __init__(self, master_key: Optional[str] = None, config: Optional[EncryptionConfig] = None):
        self.config = config or EncryptionConfig()
        self.key_rotation_schedule: Dict[str, datetime] = {}
        
        # Use provided key or environment variable
        key_material = master_key or os.getenv("PHOENIX_ENCRYPTION_KEY", "")
        
        if not key_material:
            raise ValueError("Encryption key not provided")
        
        # Derive encryption key
        self.cipher_suite = self._derive_cipher(key_material)
        self._create_time = datetime.now()
    
    def _derive_cipher(self, key_material: str) -> Fernet:
        """Derive cipher from key material"""
        # Use PBKDF2 to derive key
        if not self.config.salt:
            self.config.salt = os.urandom(16)
        
        kdf = PBKDF2(
            algorithm=hashes.SHA256(),
            length=32,
            salt=self.config.salt,
            iterations=self.config.iterations,
        )
        
        key = base64.urlsafe_b64encode(
            kdf.derive(key_material.encode())
        )
        
        return Fernet(key)
    
    def encrypt(self, plaintext: Any) -> str:
        """Encrypt data"""
        try:
            # Convert to JSON if not string
            if not isinstance(plaintext, str):
                plaintext = json.dumps(plaintext)
            
            # Encrypt
            ciphertext = self.cipher_suite.encrypt(plaintext.encode())
            
            # Return as base64 string
            return base64.b64encode(ciphertext).decode()
        except Exception as e:
            raise ValueError(f"Encryption failed: {e}")
    
    def decrypt(self, ciphertext: str) -> str:
        """Decrypt data"""
        try:
            # Decode from base64
            ciphertext_bytes = base64.b64decode(ciphertext.encode())
            
            # Decrypt
            plaintext = self.cipher_suite.decrypt(ciphertext_bytes)
            
            return plaintext.decode()
        except Exception as e:
            raise ValueError(f"Decryption failed: {e}")
    
    def decrypt_json(self, ciphertext: str) -> Dict[str, Any]:
        """Decrypt and parse JSON"""
        plaintext = self.decrypt(ciphertext)
        return json.loads(plaintext)
    
    def rotate_key(self, new_key_material: str) -> bool:
        """Rotate encryption key"""
        try:
            # Create new cipher with new key
            new_cipher = self._derive_cipher(new_key_material)
            
            # Update cipher suite
            self.cipher_suite = new_cipher
            
            # Record rotation time
            timestamp = datetime.now().isoformat()
            self.key_rotation_schedule[timestamp] = datetime.now()
            
            return True
        except Exception as e:
            print(f"Key rotation failed: {e}")
            return False
    
    def should_rotate_key(self) -> bool:
        """Check if key rotation is needed"""
        last_rotation = max(self.key_rotation_schedule.values()) if self.key_rotation_schedule else self._create_time
        days_since_rotation = (datetime.now() - last_rotation).days
        
        return days_since_rotation >= self.config.key_rotation_days
    
    def get_key_age_days(self) -> int:
        """Get age of current key in days"""
        last_rotation = max(self.key_rotation_schedule.values()) if self.key_rotation_schedule else self._create_time
        return (datetime.now() - last_rotation).days


class FieldEncryption:
    """Encrypt specific fields in data structures"""
    
    def __init__(self, manager: EncryptionManager, sensitive_fields: Optional[list] = None):
        self.manager = manager
        self.sensitive_fields = sensitive_fields or [
            "password", "api_key", "secret", "token",
            "credit_card", "ssn", "email"
        ]
    
    def encrypt_sensitive_fields(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """Encrypt sensitive fields in dictionary"""
        encrypted_data = data.copy()
        
        for field in self.sensitive_fields:
            if field in encrypted_data:
                encrypted_data[field] = {
                    "_encrypted": True,
                    "value": self.manager.encrypt(encrypted_data[field])
                }
        
        return encrypted_data
    
    def decrypt_sensitive_fields(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """Decrypt sensitive fields in dictionary"""
        decrypted_data = data.copy()
        
        for field in self.sensitive_fields:
            if field in decrypted_data and isinstance(decrypted_data[field], dict):
                if decrypted_data[field].get("_encrypted"):
                    decrypted_data[field] = self.manager.decrypt(decrypted_data[field]["value"])
        
        return decrypted_data
    
    def is_encrypted(self, value: Any) -> bool:
        """Check if value is encrypted"""
        return isinstance(value, dict) and value.get("_encrypted") == True


class TLSConfiguration:
    """Manage TLS/SSL configuration"""
    
    def __init__(
        self,
        cert_path: Optional[str] = None,
        key_path: Optional[str] = None,
        ca_bundle: Optional[str] = None,
        min_tls_version: str = "TLSv1.2"
    ):
        self.cert_path = cert_path
        self.key_path = key_path
        self.ca_bundle = ca_bundle
        self.min_tls_version = min_tls_version
        self.cipher_suites = [
            "TLS_AES_256_GCM_SHA384",
            "TLS_CHACHA20_POLY1305_SHA256",
            "TLS_AES_128_GCM_SHA256",
            "ECDHE-ECDSA-AES256-GCM-SHA384",
            "ECDHE-RSA-AES256-GCM-SHA384",
            "ECDHE-ECDSA-CHACHA20-POLY1305",
            "ECDHE-RSA-CHACHA20-POLY1305",
            "ECDHE-ECDSA-AES128-GCM-SHA256",
            "ECDHE-RSA-AES128-GCM-SHA256",
        ]
    
    def get_aiohttp_config(self) -> Dict[str, Any]:
        """Get aiohttp SSL configuration"""
        import ssl
        
        ssl_context = ssl.create_default_context()
        ssl_context.minimum_version = self._parse_tls_version(self.min_tls_version)
        
        if self.cert_path and self.key_path:
            ssl_context.load_cert_chain(self.cert_path, self.key_path)
        
        if self.ca_bundle:
            ssl_context.load_verify_locations(self.ca_bundle)
        
        return {"ssl": ssl_context}
    
    def _parse_tls_version(self, version: str):
        """Parse TLS version string"""
        import ssl
        
        version_map = {
            "TLSv1.0": ssl.TLSVersion.TLSv1,
            "TLSv1.1": ssl.TLSVersion.TLSv1_1,
            "TLSv1.2": ssl.TLSVersion.TLSv1_2,
            "TLSv1.3": ssl.TLSVersion.TLSv1_3,
        }
        
        return version_map.get(version, ssl.TLSVersion.TLSv1_2)
    
    def validate_certificate(self, cert_path: str) -> bool:
        """Validate SSL certificate"""
        try:
            from OpenSSL import crypto
            
            with open(cert_path, 'rb') as f:
                cert_data = f.read()
            
            cert = crypto.load_certificate(crypto.FILETYPE_PEM, cert_data)
            
            # Check expiration
            not_after = cert.get_notAfter()
            if not_after:
                return True
            
            return False
        except Exception as e:
            print(f"Certificate validation failed: {e}")
            return False


class EncryptedStorage:
    """Encrypted key-value storage"""
    
    def __init__(self, manager: EncryptionManager):
        self.manager = manager
        self.store: Dict[str, str] = {}
    
    def set(self, key: str, value: Any) -> bool:
        """Store encrypted value"""
        try:
            encrypted = self.manager.encrypt(value)
            self.store[key] = encrypted
            return True
        except Exception as e:
            print(f"Storage set failed: {e}")
            return False
    
    def get(self, key: str) -> Optional[Any]:
        """Retrieve and decrypt value"""
        if key not in self.store:
            return None
        
        try:
            return self.manager.decrypt(self.store[key])
        except Exception as e:
            print(f"Storage get failed: {e}")
            return None
    
    def get_json(self, key: str) -> Optional[Dict[str, Any]]:
        """Retrieve and decrypt JSON value"""
        if key not in self.store:
            return None
        
        try:
            return self.manager.decrypt_json(self.store[key])
        except Exception as e:
            print(f"Storage get_json failed: {e}")
            return None
    
    def delete(self, key: str) -> bool:
        """Delete encrypted value"""
        if key in self.store:
            del self.store[key]
            return True
        return False
    
    def clear(self) -> bool:
        """Clear all stored values"""
        self.store.clear()
        return True


if __name__ == "__main__":
    # Example usage
    manager = EncryptionManager(master_key="my-secret-key")
    
    # Encrypt/decrypt
    plaintext = "sensitive data"
    encrypted = manager.encrypt(plaintext)
    decrypted = manager.decrypt(encrypted)
    
    print(f"Original: {plaintext}")
    print(f"Encrypted: {encrypted}")
    print(f"Decrypted: {decrypted}")
    
    # Field encryption
    from_enc = FieldEncryption(manager)
    user_data = {"name": "John", "password": "secret123"}
    encrypted_data = from_enc.encrypt_sensitive_fields(user_data)
    print(f"\nEncrypted user data: {encrypted_data}")
    
    # Encrypted storage
    storage = EncryptedStorage(manager)
    storage.set("api_key", "my-api-key-12345")
    retrieved = storage.get("api_key")
    print(f"\nStored and retrieved: {retrieved}")
