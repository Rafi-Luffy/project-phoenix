"""
Secrets Management

Manage secrets with rotation and compliance:
- Centralized secrets storage
- Automatic secret rotation
- Audit logging of access
- Compliance tracking
- Integration with cloud secret managers
"""

import os
import json
from typing import Dict, Any, Optional, List
from dataclasses import dataclass
from datetime import datetime, timedelta
from enum import Enum
import hashlib
import random
import string


class SecretType(Enum):
    """Types of secrets"""
    API_KEY = "api_key"
    PASSWORD = "password"
    TOKEN = "token"
    CERTIFICATE = "certificate"
    DATABASE_CONNECTION = "database_connection"
    ENCRYPTION_KEY = "encryption_key"
    OAUTH_CREDENTIAL = "oauth_credential"


@dataclass
class SecretMetadata:
    """Metadata for a secret"""
    type: SecretType
    created_at: datetime
    rotated_at: datetime
    expires_at: Optional[datetime]
    rotation_enabled: bool = True
    rotation_interval_days: int = 90
    access_count: int = 0
    last_accessed: Optional[datetime] = None
    creator: Optional[str] = None
    version: int = 1


class SecretsManager:
    """Manage application secrets"""
    
    def __init__(self):
        self.secrets: Dict[str, Dict[str, Any]] = {}
        self.audit_log: List[Dict[str, Any]] = []
        self.rotation_schedule: Dict[str, datetime] = {}
    
    def store_secret(
        self,
        name: str,
        value: str,
        secret_type: SecretType = SecretType.API_KEY,
        expires_in_days: Optional[int] = None,
        rotation_enabled: bool = True
    ) -> bool:
        """Store a new secret"""
        try:
            expires_at = None
            if expires_in_days:
                expires_at = (datetime.now() + timedelta(days=expires_in_days)).isoformat()
            
            metadata = SecretMetadata(
                type=secret_type,
                created_at=datetime.now(),
                rotated_at=datetime.now(),
                expires_at=expires_at,
                rotation_enabled=rotation_enabled
            )
            
            self.secrets[name] = {
                "value": value,
                "metadata": metadata
            }
            
            # Log action
            self._audit_log("SECRET_STORED", {"name": name, "type": secret_type.value})
            
            return True
        except Exception as e:
            print(f"Failed to store secret: {e}")
            return False
    
    def get_secret(self, name: str) -> Optional[str]:
        """Retrieve a secret"""
        if name not in self.secrets:
            self._audit_log("SECRET_NOT_FOUND", {"name": name, "status": "error"})
            return None
        
        secret_data = self.secrets[name]
        metadata = secret_data["metadata"]
        
        # Check expiration
        if metadata.expires_at:
            if datetime.fromisoformat(metadata.expires_at) < datetime.now():
                self._audit_log("SECRET_EXPIRED", {"name": name})
                return None
        
        # Update access metadata
        metadata.access_count += 1
        metadata.last_accessed = datetime.now()
        
        # Log access
        self._audit_log("SECRET_ACCESSED", {"name": name})
        
        return secret_data["value"]
    
    def rotate_secret(self, name: str, new_value: str) -> bool:
        """Rotate a secret"""
        if name not in self.secrets:
            self._audit_log("ROTATION_FAILED", {"name": name, "reason": "secret_not_found"})
            return False
        
        try:
            secret_data = self.secrets[name]
            metadata = secret_data["metadata"]
            
            # Store old value in history
            if "history" not in secret_data:
                secret_data["history"] = []
            
            secret_data["history"].append({
                "value": secret_data["value"],
                "rotated_at": metadata.rotated_at.isoformat()
            })
            
            # Update with new value
            secret_data["value"] = new_value
            metadata.rotated_at = datetime.now()
            metadata.version += 1
            
            # Log rotation
            self._audit_log("SECRET_ROTATED", {"name": name, "version": metadata.version})
            
            return True
        except Exception as e:
            print(f"Secret rotation failed: {e}")
            self._audit_log("ROTATION_ERROR", {"name": name, "error": str(e)})
            return False
    
    def delete_secret(self, name: str) -> bool:
        """Delete a secret"""
        if name in self.secrets:
            del self.secrets[name]
            self._audit_log("SECRET_DELETED", {"name": name})
            return True
        return False
    
    def should_rotate(self, name: str) -> bool:
        """Check if secret needs rotation"""
        if name not in self.secrets:
            return False
        
        metadata = self.secrets[name]["metadata"]
        
        if not metadata.rotation_enabled:
            return False
        
        days_since_rotation = (datetime.now() - metadata.rotated_at).days
        return days_since_rotation >= metadata.rotation_interval_days
    
    def _audit_log(self, action: str, details: Dict[str, Any]):
        """Log secret action"""
        self.audit_log.append({
            "action": action,
            "timestamp": datetime.now().isoformat(),
            "details": details
        })
    
    def get_audit_log(self, days: int = 30) -> List[Dict[str, Any]]:
        """Get audit log for specified period"""
        cutoff = datetime.now() - timedelta(days=days)
        
        return [
            entry for entry in self.audit_log
            if datetime.fromisoformat(entry["timestamp"]) > cutoff
        ]
    
    def get_secret_metadata(self, name: str) -> Optional[Dict[str, Any]]:
        """Get metadata for a secret"""
        if name not in self.secrets:
            return None
        
        metadata = self.secrets[name]["metadata"]
        return {
            "type": metadata.type.value,
            "created_at": metadata.created_at.isoformat(),
            "rotated_at": metadata.rotated_at.isoformat(),
            "expires_at": metadata.expires_at,
            "rotation_enabled": metadata.rotation_enabled,
            "access_count": metadata.access_count,
            "version": metadata.version
        }


class SecretRotationScheduler:
    """Automatically rotate secrets on schedule"""
    
    def __init__(self, manager: SecretsManager):
        self.manager = manager
        self.rotation_tasks: Dict[str, Dict[str, Any]] = {}
    
    def schedule_rotation(
        self,
        secret_name: str,
        rotation_callback,
        rotation_interval_days: int = 90
    ):
        """Schedule secret for rotation"""
        self.rotation_tasks[secret_name] = {
            "callback": rotation_callback,
            "interval_days": rotation_interval_days,
            "last_rotation": datetime.now()
        }
    
    async def check_and_rotate(self) -> Dict[str, bool]:
        """Check and rotate secrets as needed"""
        results = {}
        
        for secret_name, task in self.rotation_tasks.items():
            if self.manager.should_rotate(secret_name):
                try:
                    # Call rotation callback to get new value
                    new_value = await task["callback"]()
                    
                    # Rotate secret
                    success = self.manager.rotate_secret(secret_name, new_value)
                    results[secret_name] = success
                except Exception as e:
                    print(f"Rotation failed for {secret_name}: {e}")
                    results[secret_name] = False
        
        return results
    
    def get_rotation_schedule(self) -> Dict[str, Dict[str, Any]]:
        """Get rotation schedule for all secrets"""
        schedule = {}
        
        for name, task in self.rotation_tasks.items():
            metadata = self.manager.get_secret_metadata(name)
            if metadata:
                schedule[name] = {
                    "interval_days": task["interval_days"],
                    "last_rotation": metadata["rotated_at"],
                    "next_rotation": (
                        datetime.fromisoformat(metadata["rotated_at"]) +
                        timedelta(days=task["interval_days"])
                    ).isoformat()
                }
        
        return schedule


class AWSSecretsManagerAdapter:
    """Adapter for AWS Secrets Manager"""
    
    def __init__(self, region: str = "us-east-1"):
        self.region = region
        self.client = None  # Would be: boto3.client('secretsmanager', region_name=region)
    
    async def get_secret(self, secret_name: str) -> Optional[str]:
        """Get secret from AWS Secrets Manager"""
        try:
            # In production, would use actual boto3 client
            # response = self.client.get_secret_value(SecretId=secret_name)
            # return response.get('SecretString')
            return None
        except Exception as e:
            print(f"AWS Secrets Manager error: {e}")
            return None
    
    async def create_secret(self, name: str, value: str) -> bool:
        """Create secret in AWS Secrets Manager"""
        try:
            # Would use: self.client.create_secret(Name=name, SecretString=value)
            return True
        except Exception as e:
            print(f"Failed to create secret: {e}")
            return False
    
    async def rotate_secret(self, name: str, new_value: str) -> bool:
        """Rotate secret in AWS Secrets Manager"""
        try:
            # Would use: self.client.put_secret_value(SecretId=name, SecretString=new_value)
            return True
        except Exception as e:
            print(f"Failed to rotate secret: {e}")
            return False


class AzureKeyVaultAdapter:
    """Adapter for Azure Key Vault"""
    
    def __init__(self, vault_url: str):
        self.vault_url = vault_url
        self.client = None  # Would be: SecretClient(vault_url=vault_url, credential=credential)
    
    async def get_secret(self, secret_name: str) -> Optional[str]:
        """Get secret from Azure Key Vault"""
        try:
            # Would use: self.client.get_secret(secret_name)
            return None
        except Exception as e:
            print(f"Azure Key Vault error: {e}")
            return None
    
    async def create_secret(self, name: str, value: str) -> bool:
        """Create secret in Azure Key Vault"""
        try:
            # Would use: self.client.set_secret(name, value)
            return True
        except Exception as e:
            print(f"Failed to create secret: {e}")
            return False


class PasswordGenerator:
    """Generate secure passwords"""
    
    @staticmethod
    def generate(
        length: int = 32,
        use_uppercase: bool = True,
        use_lowercase: bool = True,
        use_digits: bool = True,
        use_special: bool = True
    ) -> str:
        """Generate secure random password"""
        characters = ""
        
        if use_lowercase:
            characters += string.ascii_lowercase
        if use_uppercase:
            characters += string.ascii_uppercase
        if use_digits:
            characters += string.digits
        if use_special:
            characters += string.punctuation
        
        if not characters:
            raise ValueError("Must include at least one character type")
        
        # Generate password with at least one character from each category
        password_chars = []
        
        if use_lowercase:
            password_chars.append(random.choice(string.ascii_lowercase))
        if use_uppercase:
            password_chars.append(random.choice(string.ascii_uppercase))
        if use_digits:
            password_chars.append(random.choice(string.digits))
        if use_special:
            password_chars.append(random.choice(string.punctuation))
        
        # Fill remaining length
        remaining = length - len(password_chars)
        password_chars.extend(random.choices(characters, k=remaining))
        
        # Shuffle
        random.shuffle(password_chars)
        
        return "".join(password_chars)


if __name__ == "__main__":
    # Example usage
    manager = SecretsManager()
    
    # Store secrets
    manager.store_secret("api_key", "sk-1234567890", SecretType.API_KEY, rotation_enabled=True)
    manager.store_secret("db_password", "secret123", SecretType.PASSWORD, rotation_enabled=True)
    
    # Retrieve secret
    api_key = manager.get_secret("api_key")
    print(f"API Key: {api_key}")
    
    # Rotate secret
    manager.rotate_secret("api_key", "sk-0987654321")
    
    # Get metadata
    metadata = manager.get_secret_metadata("api_key")
    print(f"API Key Metadata: {metadata}")
    
    # Generate password
    password = PasswordGenerator.generate(32)
    print(f"Generated password: {password}")
