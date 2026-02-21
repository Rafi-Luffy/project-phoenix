"""
Authentication and Authorization System
Manages user authentication, JWT tokens, and role-based access control
"""

from datetime import datetime, timedelta
from typing import Dict, Optional, List
from enum import Enum
import hashlib
import secrets
import jwt
import logging

logger = logging.getLogger(__name__)


class UserRole(Enum):
    """User role definitions"""
    ADMIN = "admin"
    SYSTEM_ENGINEER = "system_engineer"
    OPERATOR = "operator"
    MONITOR = "monitor"
    VIEWER = "viewer"


class PermissionLevel(Enum):
    """Permission levels for actions"""
    CREATE = "create"
    READ = "read"
    UPDATE = "update"
    DELETE = "delete"
    EXECUTE = "execute"
    APPROVE = "approve"


class User:
    """User account representation"""
    
    def __init__(self, user_id: str, username: str, email: str, role: UserRole):
        self.user_id = user_id
        self.username = username
        self.email = email
        self.role = role
        self.created_at = datetime.now()
        self.last_login = None
        self.is_active = True
        self.password_hash = None
        self.mfa_enabled = False
    
    def set_password(self, password: str):
        """Hash and store password"""
        salt = secrets.token_hex(16)
        self.password_hash = f"{salt}${hashlib.pbkdf2_hmac('sha256', password.encode(), salt.encode(), 100000).hex()}"
    
    def verify_password(self, password: str) -> bool:
        """Verify provided password against stored hash"""
        if not self.password_hash:
            return False
        salt, stored_hash = self.password_hash.split('$')
        new_hash = hashlib.pbkdf2_hmac('sha256', password.encode(), salt.encode(), 100000).hex()
        return new_hash == stored_hash


class TokenData:
    """JWT token data"""
    
    def __init__(self, user_id: str, username: str, role: UserRole, token: str, expires_at: datetime):
        self.user_id = user_id
        self.username = username
        self.role = role
        self.token = token
        self.expires_at = expires_at


class AccessControl:
    """Role-based access control (RBAC)"""
    
    def __init__(self):
        self.role_permissions: Dict[UserRole, List[PermissionLevel]] = {
            UserRole.ADMIN: [PermissionLevel.CREATE, PermissionLevel.READ, PermissionLevel.UPDATE, PermissionLevel.DELETE, PermissionLevel.EXECUTE, PermissionLevel.APPROVE],
            UserRole.SYSTEM_ENGINEER: [PermissionLevel.CREATE, PermissionLevel.READ, PermissionLevel.UPDATE, PermissionLevel.EXECUTE, PermissionLevel.APPROVE],
            UserRole.OPERATOR: [PermissionLevel.READ, PermissionLevel.EXECUTE],
            UserRole.MONITOR: [PermissionLevel.READ],
            UserRole.VIEWER: [PermissionLevel.READ]
        }
    
    def has_permission(self, user_role: UserRole, required_permission: PermissionLevel) -> bool:
        """Check if user role has required permission"""
        permissions = self.role_permissions.get(user_role, [])
        return required_permission in permissions
    
    def get_permissions(self, user_role: UserRole) -> List[PermissionLevel]:
        """Get all permissions for a role"""
        return self.role_permissions.get(user_role, [])


class AuthenticationManager:
    """Manages user authentication and token generation"""
    
    def __init__(self, secret_key: str = None, token_expiration_hours: int = 24):
        self.secret_key = secret_key or secrets.token_urlsafe(32)
        self.token_expiration_hours = token_expiration_hours
        self.users: Dict[str, User] = {}
        self.access_control = AccessControl()
        self.valid_tokens: Dict[str, TokenData] = {}
        self.failed_login_attempts: Dict[str, int] = {}
        self.max_failed_attempts = 5
    
    def register_user(self, username: str, email: str, password: str, role: UserRole = UserRole.VIEWER) -> Optional[str]:
        """Register a new user"""
        if any(u.username == username for u in self.users.values()):
            logger.warning(f"Registration failed: username {username} already exists")
            return None
        
        import uuid
        user_id = str(uuid.uuid4())
        user = User(user_id, username, email, role)
        user.set_password(password)
        self.users[user_id] = user
        
        logger.info(f"User registered: {username} ({role.value})")
        return user_id
    
    def authenticate(self, username: str, password: str) -> Optional[TokenData]:
        """Authenticate user and generate JWT token"""
        
        # Check failed login attempts
        if self.failed_login_attempts.get(username, 0) >= self.max_failed_attempts:
            logger.warning(f"Authentication blocked: too many failed attempts for {username}")
            return None
        
        user = next((u for u in self.users.values() if u.username == username), None)
        if not user or not user.verify_password(password):
            self.failed_login_attempts[username] = self.failed_login_attempts.get(username, 0) + 1
            logger.warning(f"Authentication failed: invalid credentials for {username}")
            return None
        
        if not user.is_active:
            logger.warning(f"Authentication failed: user {username} is inactive")
            return None
        
        # Reset failed attempts
        self.failed_login_attempts[username] = 0
        user.last_login = datetime.now()
        
        # Generate JWT token
        expires_at = datetime.now() + timedelta(hours=self.token_expiration_hours)
        payload = {
            'user_id': user.user_id,
            'username': user.username,
            'role': user.role.value,
            'exp': expires_at
        }
        
        token = jwt.encode(payload, self.secret_key, algorithm="HS256")
        token_data = TokenData(user.user_id, user.username, user.role, token, expires_at)
        self.valid_tokens[token] = token_data
        
        logger.info(f"User authenticated: {username}")
        return token_data
    
    def verify_token(self, token: str) -> Optional[TokenData]:
        """Verify JWT token and return token data"""
        if token not in self.valid_tokens:
            try:
                payload = jwt.decode(token, self.secret_key, algorithms=["HS256"])
                user = self.users.get(payload['user_id'])
                if not user:
                    return None
                
                expires_at = datetime.fromtimestamp(payload['exp'])
                token_data = TokenData(
                    payload['user_id'],
                    payload['username'],
                    UserRole(payload['role']),
                    token,
                    expires_at
                )
                self.valid_tokens[token] = token_data
                return token_data
            except jwt.InvalidTokenError:
                logger.warning(f"Invalid token provided")
                return None
        
        token_data = self.valid_tokens[token]
        if datetime.now() > token_data.expires_at:
            del self.valid_tokens[token]
            logger.info(f"Token expired for {token_data.username}")
            return None
        
        return token_data
    
    def revoke_token(self, token: str):
        """Revoke a token"""
        if token in self.valid_tokens:
            del self.valid_tokens[token]
            logger.info(f"Token revoked")
    
    def get_user(self, user_id: str) -> Optional[User]:
        """Get user by ID"""
        return self.users.get(user_id)
    
    def update_user_role(self, user_id: str, new_role: UserRole) -> bool:
        """Update user role"""
        user = self.users.get(user_id)
        if not user:
            return False
        user.role = new_role
        logger.info(f"User role updated: {user.username} -> {new_role.value}")
        return True
    
    def deactivate_user(self, user_id: str) -> bool:
        """Deactivate user account"""
        user = self.users.get(user_id)
        if not user:
            return False
        user.is_active = False
        logger.info(f"User deactivated: {user.username}")
        return True
    
    def check_permission(self, token: str, required_permission: PermissionLevel) -> bool:
        """Check if token holder has required permission"""
        token_data = self.verify_token(token)
        if not token_data:
            return False
        return self.access_control.has_permission(token_data.role, required_permission)
