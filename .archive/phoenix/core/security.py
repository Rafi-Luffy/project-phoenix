"""
Security Module
Provides authentication, authorization, encryption, and audit logging
"""

from dataclasses import dataclass, field
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Set
from enum import Enum
import hashlib
import secrets
from abc import ABC, abstractmethod
import json


class AuthenticationMethod(Enum):
    """Supported authentication methods"""
    JWT = "jwt"
    API_KEY = "api_key"
    OAUTH2 = "oauth2"
    BASIC = "basic"


class PermissionLevel(Enum):
    """Permission levels"""
    ADMIN = "admin"
    DEVELOPER = "developer"
    OPERATOR = "operator"
    VIEWER = "viewer"


class AuditAction(Enum):
    """Types of actions to audit"""
    CREATE = "create"
    READ = "read"
    UPDATE = "update"
    DELETE = "delete"
    EXECUTE = "execute"
    LOGIN = "login"
    LOGOUT = "logout"
    CONFIG_CHANGE = "config_change"
    INCIDENT_CREATION = "incident_creation"
    RECOVERY_EXECUTION = "recovery_execution"


@dataclass
class User:
    """User account"""
    user_id: str
    username: str
    email: str
    password_hash: str
    permission_level: PermissionLevel
    enabled: bool = True
    created_at: datetime = field(default_factory=datetime.now)
    last_login: Optional[datetime] = None
    mfa_enabled: bool = False
    mfa_secret: Optional[str] = None
    api_keys: List[str] = field(default_factory=list)


@dataclass
class AuditLog:
    """Audit log entry"""
    timestamp: datetime
    user_id: str
    action: AuditAction
    resource_type: str
    resource_id: str
    details: Dict = field(default_factory=dict)
    success: bool = True
    ip_address: Optional[str] = None
    user_agent: Optional[str] = None


class PasswordManager:
    """Secure password management"""
    
    @staticmethod
    def hash_password(password: str, salt: Optional[str] = None) -> str:
        """Hash password with salt"""
        if salt is None:
            salt = secrets.token_hex(16)
        
        hash_obj = hashlib.pbkdf2_hmac(
            'sha256',
            password.encode(),
            salt.encode(),
            100000
        )
        return f"{salt}${hash_obj.hex()}"
    
    @staticmethod
    def verify_password(password: str, password_hash: str) -> bool:
        """Verify password against hash"""
        try:
            salt, stored_hash = password_hash.split('$')
            new_hash = hashlib.pbkdf2_hmac(
                'sha256',
                password.encode(),
                salt.encode(),
                100000
            )
            return new_hash.hex() == stored_hash
        except:
            return False
    
    @staticmethod
    def generate_secure_password() -> str:
        """Generate secure random password"""
        return secrets.token_urlsafe(24)


class TokenManager:
    """Manages authentication tokens"""
    
    def __init__(self, secret_key: str, expiration_hours: int = 24):
        self.secret_key = secret_key
        self.expiration_hours = expiration_hours
        self.tokens: Dict[str, Dict] = {}
        self.lock = __import__('threading').Lock()
    
    def create_token(self, user_id: str) -> str:
        """Create authentication token"""
        token = secrets.token_urlsafe(32)
        
        with self.lock:
            self.tokens[token] = {
                "user_id": user_id,
                "created_at": datetime.now(),
                "expires_at": datetime.now() + timedelta(hours=self.expiration_hours)
            }
        
        return token
    
    def verify_token(self, token: str) -> Optional[str]:
        """Verify token and return user_id"""
        with self.lock:
            if token not in self.tokens:
                return None
            
            token_data = self.tokens[token]
            if datetime.now() > token_data["expires_at"]:
                del self.tokens[token]
                return None
            
            return token_data["user_id"]
    
    def revoke_token(self, token: str) -> bool:
        """Revoke a token"""
        with self.lock:
            if token in self.tokens:
                del self.tokens[token]
                return True
        return False
    
    def revoke_user_tokens(self, user_id: str) -> int:
        """Revoke all tokens for a user"""
        with self.lock:
            tokens_to_revoke = [
                t for t, d in self.tokens.items()
                if d["user_id"] == user_id
            ]
            for token in tokens_to_revoke:
                del self.tokens[token]
        return len(tokens_to_revoke)


class APIKeyManager:
    """Manages API keys for programmatic access"""
    
    def __init__(self):
        self.api_keys: Dict[str, Dict] = {}
        self.lock = __import__('threading').Lock()
    
    def create_api_key(self, user_id: str, name: str, permissions: List[str]) -> str:
        """Create a new API key"""
        api_key = f"phoenix_{secrets.token_urlsafe(32)}"
        key_hash = hashlib.sha256(api_key.encode()).hexdigest()
        
        with self.lock:
            self.api_keys[key_hash] = {
                "user_id": user_id,
                "name": name,
                "permissions": permissions,
                "created_at": datetime.now(),
                "last_used": None,
                "enabled": True
            }
        
        return api_key
    
    def verify_api_key(self, api_key: str) -> Optional[str]:
        """Verify API key and return user_id"""
        key_hash = hashlib.sha256(api_key.encode()).hexdigest()
        
        with self.lock:
            if key_hash not in self.api_keys:
                return None
            
            key_data = self.api_keys[key_hash]
            if not key_data["enabled"]:
                return None
            
            # Update last used
            self.api_keys[key_hash]["last_used"] = datetime.now()
            return key_data["user_id"]
    
    def get_key_permissions(self, api_key: str) -> Optional[List[str]]:
        """Get permissions for an API key"""
        key_hash = hashlib.sha256(api_key.encode()).hexdigest()
        
        with self.lock:
            if key_hash not in self.api_keys:
                return None
            return self.api_keys[key_hash]["permissions"]
    
    def revoke_api_key(self, api_key: str) -> bool:
        """Revoke an API key"""
        key_hash = hashlib.sha256(api_key.encode()).hexdigest()
        
        with self.lock:
            if key_hash in self.api_keys:
                self.api_keys[key_hash]["enabled"] = False
                return True
        return False


class RoleBasedAccessControl:
    """Role-based access control (RBAC)"""
    
    def __init__(self):
        self.roles: Dict[str, Set[str]] = {
            "admin": {"*"},  # Full access
            "developer": {"read", "execute", "create_incidents"},
            "operator": {"read", "execute", "acknowledge_incidents"},
            "viewer": {"read"}
        }
        self.lock = __import__('threading').Lock()
    
    def has_permission(self, permission_level: PermissionLevel, required_permission: str) -> bool:
        """Check if user has required permission"""
        if permission_level == PermissionLevel.ADMIN:
            return True
        
        with self.lock:
            role_name = permission_level.value
            if role_name not in self.roles:
                return False
            
            permissions = self.roles[role_name]
            return "*" in permissions or required_permission in permissions
    
    def add_permission(self, role: str, permission: str) -> bool:
        """Add permission to role"""
        with self.lock:
            if role not in self.roles:
                self.roles[role] = set()
            self.roles[role].add(permission)
        return True
    
    def remove_permission(self, role: str, permission: str) -> bool:
        """Remove permission from role"""
        with self.lock:
            if role in self.roles:
                self.roles[role].discard(permission)
                return True
        return False


class AuditLogger:
    """Comprehensive audit logging"""
    
    def __init__(self, max_entries: int = 100000):
        self.logs: List[AuditLog] = []
        self.max_entries = max_entries
        self.lock = __import__('threading').Lock()
    
    def log_action(
        self,
        user_id: str,
        action: AuditAction,
        resource_type: str,
        resource_id: str,
        details: Dict = None,
        success: bool = True,
        ip_address: Optional[str] = None
    ):
        """Log an action"""
        entry = AuditLog(
            timestamp=datetime.now(),
            user_id=user_id,
            action=action,
            resource_type=resource_type,
            resource_id=resource_id,
            details=details or {},
            success=success,
            ip_address=ip_address
        )
        
        with self.lock:
            self.logs.append(entry)
            
            # Maintain size limit
            if len(self.logs) > self.max_entries:
                self.logs = self.logs[-self.max_entries:]
    
    def get_logs_by_user(self, user_id: str, limit: int = 100) -> List[AuditLog]:
        """Get audit logs for a user"""
        with self.lock:
            logs = [l for l in self.logs if l.user_id == user_id]
            return logs[-limit:]
    
    def get_logs_by_action(self, action: AuditAction, limit: int = 100) -> List[AuditLog]:
        """Get audit logs by action type"""
        with self.lock:
            logs = [l for l in self.logs if l.action == action]
            return logs[-limit:]
    
    def get_recent_logs(self, limit: int = 100) -> List[AuditLog]:
        """Get recent audit logs"""
        with self.lock:
            return self.logs[-limit:]


class EncryptionManager:
    """Manages encryption/decryption operations"""
    
    @staticmethod
    def encrypt_data(data: str, encryption_key: str) -> str:
        """Encrypt data using Fernet-like approach"""
        try:
            from cryptography.fernet import Fernet
            cipher = Fernet(encryption_key.encode() if isinstance(encryption_key, str) else encryption_key)
            return cipher.encrypt(data.encode()).decode()
        except ImportError:
            # Fallback: simple XOR encryption (NOT for production!)
            return ''.join(chr(ord(c) ^ ord(encryption_key[i % len(encryption_key)])) 
                          for i, c in enumerate(data))
    
    @staticmethod
    def decrypt_data(encrypted_data: str, encryption_key: str) -> str:
        """Decrypt data"""
        try:
            from cryptography.fernet import Fernet
            cipher = Fernet(encryption_key.encode() if isinstance(encryption_key, str) else encryption_key)
            return cipher.decrypt(encrypted_data.encode()).decode()
        except ImportError:
            # Fallback
            return ''.join(chr(ord(c) ^ ord(encryption_key[i % len(encryption_key)])) 
                          for i, c in enumerate(encrypted_data))


class SecurityPolicy:
    """Security policies and rules"""
    
    def __init__(self):
        self.password_min_length = 12
        self.password_require_uppercase = True
        self.password_require_numbers = True
        self.password_require_special = True
        self.max_login_attempts = 5
        self.lockout_duration_minutes = 30
        self.session_timeout_minutes = 60
        self.mfa_enabled_for_admins = True
        self.enforce_https = True
        self.enable_audit_logging = True
    
    def validate_password(self, password: str) -> tuple[bool, str]:
        """Validate password against policy"""
        if len(password) < self.password_min_length:
            return False, f"Password must be at least {self.password_min_length} characters"
        
        if self.password_require_uppercase and not any(c.isupper() for c in password):
            return False, "Password must contain uppercase letters"
        
        if self.password_require_numbers and not any(c.isdigit() for c in password):
            return False, "Password must contain numbers"
        
        if self.password_require_special and not any(c in "!@#$%^&*" for c in password):
            return False, "Password must contain special characters"
        
        return True, "Password valid"


class SecurityManager:
    """Centralized security management"""
    
    def __init__(self, secret_key: str = None):
        self.secret_key = secret_key or secrets.token_urlsafe(32)
        self.password_manager = PasswordManager()
        self.token_manager = TokenManager(self.secret_key)
        self.api_key_manager = APIKeyManager()
        self.rbac = RoleBasedAccessControl()
        self.audit_logger = AuditLogger()
        self.encryption_manager = EncryptionManager()
        self.security_policy = SecurityPolicy()
        
        self.users: Dict[str, User] = {}
        self.lock = __import__('threading').Lock()
    
    def create_user(
        self,
        username: str,
        email: str,
        password: str,
        permission_level: PermissionLevel = PermissionLevel.VIEWER
    ) -> Optional[User]:
        """Create a new user"""
        # Validate password
        valid, msg = self.security_policy.validate_password(password)
        if not valid:
            return None
        
        user_id = f"user_{secrets.token_hex(8)}"
        password_hash = self.password_manager.hash_password(password)
        
        user = User(
            user_id=user_id,
            username=username,
            email=email,
            password_hash=password_hash,
            permission_level=permission_level
        )
        
        with self.lock:
            self.users[user_id] = user
        
        # Audit
        self.audit_logger.log_action(
            user_id,
            AuditAction.CREATE,
            "user",
            user_id,
            {"username": username}
        )
        
        return user
    
    def authenticate_user(self, username: str, password: str) -> Optional[str]:
        """Authenticate user and return token"""
        # Find user by username
        user = None
        user_id = None
        with self.lock:
            for uid, u in self.users.items():
                if u.username == username:
                    user = u
                    user_id = uid
                    break
        
        if not user or not user.enabled:
            return None
        
        # Verify password
        if not self.password_manager.verify_password(password, user.password_hash):
            self.audit_logger.log_action(
                user_id,
                AuditAction.LOGIN,
                "user",
                user_id,
                success=False
            )
            return None
        
        # Update last login
        with self.lock:
            user.last_login = datetime.now()
        
        # Create token
        token = self.token_manager.create_token(user_id)
        
        # Audit
        self.audit_logger.log_action(
            user_id,
            AuditAction.LOGIN,
            "user",
            user_id,
            success=True
        )
        
        return token
    
    def validate_request(self, token_or_key: str) -> Optional[User]:
        """Validate incoming request and return user"""
        # Try token first
        user_id = self.token_manager.verify_token(token_or_key)
        if user_id:
            with self.lock:
                return self.users.get(user_id)
        
        # Try API key
        user_id = self.api_key_manager.verify_api_key(token_or_key)
        if user_id:
            with self.lock:
                return self.users.get(user_id)
        
        return None
