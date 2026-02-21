"""
Authentication and Authorization System
Provides JWT-based authentication, role-based access control, and API key management
"""

from datetime import datetime, timedelta
from typing import Optional, Dict, List, Set
from enum import Enum
import jwt
import secrets
from pydantic import BaseModel
import hashlib
import logging


logger = logging.getLogger(__name__)


class Role(str, Enum):
    ADMIN = "admin"
    AGENT_MANAGER = "agent_manager"
    MONITOR = "monitor"
    SYSTEM = "system"
    GUEST = "guest"


class Permission(str, Enum):
    READ_AGENTS = "read:agents"
    WRITE_AGENTS = "write:agents"
    DELETE_AGENTS = "delete:agents"
    READ_INCIDENTS = "read:incidents"
    WRITE_INCIDENTS = "write:incidents"
    RESOLVE_INCIDENTS = "resolve:incidents"
    READ_MEMORY = "read:memory"
    WRITE_MEMORY = "write:memory"
    READ_TASKS = "read:tasks"
    WRITE_TASKS = "write:tasks"
    MANAGE_USERS = "manage:users"
    VIEW_ANALYTICS = "view:analytics"
    SYSTEM_CONFIG = "system:config"


ROLE_PERMISSIONS = {
    Role.ADMIN: [
        Permission.READ_AGENTS, Permission.WRITE_AGENTS, Permission.DELETE_AGENTS,
        Permission.READ_INCIDENTS, Permission.WRITE_INCIDENTS, Permission.RESOLVE_INCIDENTS,
        Permission.READ_MEMORY, Permission.WRITE_MEMORY,
        Permission.READ_TASKS, Permission.WRITE_TASKS,
        Permission.MANAGE_USERS, Permission.VIEW_ANALYTICS, Permission.SYSTEM_CONFIG
    ],
    Role.AGENT_MANAGER: [
        Permission.READ_AGENTS, Permission.WRITE_AGENTS,
        Permission.READ_INCIDENTS, Permission.WRITE_INCIDENTS,
        Permission.READ_TASKS, Permission.WRITE_TASKS,
        Permission.VIEW_ANALYTICS
    ],
    Role.MONITOR: [
        Permission.READ_AGENTS, Permission.READ_INCIDENTS,
        Permission.READ_TASKS, Permission.VIEW_ANALYTICS
    ],
    Role.SYSTEM: [
        Permission.READ_AGENTS, Permission.WRITE_AGENTS,
        Permission.READ_INCIDENTS, Permission.WRITE_INCIDENTS, Permission.RESOLVE_INCIDENTS,
        Permission.READ_MEMORY, Permission.WRITE_MEMORY,
        Permission.READ_TASKS, Permission.WRITE_TASKS
    ],
    Role.GUEST: [Permission.READ_AGENTS, Permission.READ_INCIDENTS]
}


class TokenPayload(BaseModel):
    sub: str
    role: Role
    scopes: List[str]
    exp: datetime
    iat: datetime


class User(BaseModel):
    user_id: str
    username: str
    role: Role
    permissions: Set[Permission]
    created_at: str
    last_login: Optional[str] = None
    is_active: bool = True


class APIKey(BaseModel):
    key_id: str
    user_id: str
    key_hash: str
    created_at: str
    last_used: Optional[str] = None
    is_active: bool = True
    name: str


class AuthenticationManager:
    """Manages authentication tokens, API keys, and user credentials"""
    
    def __init__(self, secret_key: str = None, algorithm: str = "HS256", token_expiry_minutes: int = 60):
        self.secret_key = secret_key or secrets.token_urlsafe(32)
        self.algorithm = algorithm
        self.token_expiry_minutes = token_expiry_minutes
        
        self.users: Dict[str, User] = {}
        self.api_keys: Dict[str, APIKey] = {}
        self.refresh_tokens: Dict[str, Dict] = {}
        
        logger.info("AuthenticationManager initialized")
    
    def create_user(self, username: str, role: Role = Role.GUEST) -> User:
        """Create a new user with specified role"""
        import uuid
        user_id = str(uuid.uuid4())
        
        permissions = set(ROLE_PERMISSIONS.get(role, []))
        
        user = User(
            user_id=user_id,
            username=username,
            role=role,
            permissions=permissions,
            created_at=datetime.utcnow().isoformat(),
            is_active=True
        )
        
        self.users[user_id] = user
        logger.info(f"User created: {username} with role {role}")
        return user
    
    def get_user(self, user_id: str) -> Optional[User]:
        """Retrieve user by ID"""
        return self.users.get(user_id)
    
    def get_user_by_username(self, username: str) -> Optional[User]:
        """Retrieve user by username"""
        for user in self.users.values():
            if user.username == username:
                return user
        return None
    
    def create_token(self, user_id: str) -> str:
        """Create JWT token for user"""
        user = self.get_user(user_id)
        if not user or not user.is_active:
            raise ValueError(f"User {user_id} not found or inactive")
        
        now = datetime.utcnow()
        expiry = now + timedelta(minutes=self.token_expiry_minutes)
        
        payload = TokenPayload(
            sub=user_id,
            role=user.role,
            scopes=[str(p) for p in user.permissions],
            iat=now,
            exp=expiry
        )
        
        token = jwt.encode(
            payload.model_dump(mode='json'),
            self.secret_key,
            algorithm=self.algorithm
        )
        
        logger.info(f"Token created for user: {user_id}")
        return token
    
    def verify_token(self, token: str) -> Optional[TokenPayload]:
        """Verify and decode JWT token"""
        try:
            payload = jwt.decode(
                token,
                self.secret_key,
                algorithms=[self.algorithm]
            )
            
            payload['exp'] = datetime.fromisoformat(payload['exp'])
            payload['iat'] = datetime.fromisoformat(payload['iat'])
            
            token_data = TokenPayload(**payload)
            logger.debug(f"Token verified for user: {token_data.sub}")
            return token_data
        except jwt.ExpiredSignatureError:
            logger.warning("Token expired")
            return None
        except jwt.InvalidTokenError:
            logger.warning("Invalid token")
            return None
    
    def create_api_key(self, user_id: str, name: str = "Default Key") -> str:
        """Create API key for user"""
        user = self.get_user(user_id)
        if not user:
            raise ValueError(f"User {user_id} not found")
        
        import uuid
        key_id = str(uuid.uuid4())
        raw_key = secrets.token_urlsafe(32)
        key_hash = hashlib.sha256(raw_key.encode()).hexdigest()
        
        api_key = APIKey(
            key_id=key_id,
            user_id=user_id,
            key_hash=key_hash,
            created_at=datetime.utcnow().isoformat(),
            name=name,
            is_active=True
        )
        
        self.api_keys[key_id] = api_key
        logger.info(f"API key created for user: {user_id}")
        
        return raw_key
    
    def verify_api_key(self, raw_key: str) -> Optional[str]:
        """Verify API key and return user ID"""
        key_hash = hashlib.sha256(raw_key.encode()).hexdigest()
        
        for key_id, api_key in self.api_keys.items():
            if api_key.key_hash == key_hash and api_key.is_active:
                api_key.last_used = datetime.utcnow().isoformat()
                logger.debug(f"API key verified for user: {api_key.user_id}")
                return api_key.user_id
        
        logger.warning("Invalid API key attempt")
        return None
    
    def revoke_api_key(self, key_id: str) -> bool:
        """Revoke an API key"""
        if key_id in self.api_keys:
            self.api_keys[key_id].is_active = False
            logger.info(f"API key revoked: {key_id}")
            return True
        return False
    
    def deactivate_user(self, user_id: str) -> bool:
        """Deactivate a user account"""
        user = self.get_user(user_id)
        if user:
            user.is_active = False
            logger.info(f"User deactivated: {user_id}")
            return True
        return False
    
    def reactivate_user(self, user_id: str) -> bool:
        """Reactivate a user account"""
        user = self.get_user(user_id)
        if user:
            user.is_active = True
            logger.info(f"User reactivated: {user_id}")
            return True
        return False
    
    def update_user_role(self, user_id: str, new_role: Role) -> bool:
        """Update user role and permissions"""
        user = self.get_user(user_id)
        if user:
            user.role = new_role
            user.permissions = set(ROLE_PERMISSIONS.get(new_role, []))
            logger.info(f"User role updated: {user_id} to {new_role}")
            return True
        return False
    
    def has_permission(self, user_id: str, permission: Permission) -> bool:
        """Check if user has specific permission"""
        user = self.get_user(user_id)
        if not user:
            return False
        return permission in user.permissions


class AuthorizationManager:
    """Manages resource-level access control and permissions"""
    
    def __init__(self):
        self.resource_acl: Dict[str, Dict[str, List[str]]] = {}
        self.user_groups: Dict[str, Set[str]] = {}
        logger.info("AuthorizationManager initialized")
    
    def grant_access(self, user_id: str, resource_id: str, actions: List[str]):
        """Grant specific actions on a resource to a user"""
        if resource_id not in self.resource_acl:
            self.resource_acl[resource_id] = {}
        
        self.resource_acl[resource_id][user_id] = actions
        logger.info(f"Access granted: user {user_id} to resource {resource_id} for actions {actions}")
    
    def revoke_access(self, user_id: str, resource_id: str):
        """Revoke all access to a resource from a user"""
        if resource_id in self.resource_acl:
            if user_id in self.resource_acl[resource_id]:
                del self.resource_acl[resource_id][user_id]
                logger.info(f"Access revoked: user {user_id} from resource {resource_id}")
    
    def check_access(self, user_id: str, resource_id: str, action: str) -> bool:
        """Check if user can perform action on resource"""
        if resource_id not in self.resource_acl:
            return False
        
        if user_id not in self.resource_acl[resource_id]:
            return False
        
        allowed_actions = self.resource_acl[resource_id][user_id]
        return action in allowed_actions
    
    def create_group(self, group_id: str, members: Set[str] = None):
        """Create a group of users"""
        self.user_groups[group_id] = members or set()
        logger.info(f"Group created: {group_id} with {len(members or [])} members")
    
    def add_to_group(self, user_id: str, group_id: str):
        """Add user to a group"""
        if group_id not in self.user_groups:
            self.user_groups[group_id] = set()
        
        self.user_groups[group_id].add(user_id)
        logger.info(f"User {user_id} added to group {group_id}")
    
    def remove_from_group(self, user_id: str, group_id: str):
        """Remove user from a group"""
        if group_id in self.user_groups:
            self.user_groups[group_id].discard(user_id)
            logger.info(f"User {user_id} removed from group {group_id}")
    
    def grant_group_access(self, group_id: str, resource_id: str, actions: List[str]):
        """Grant resource access to all members of a group"""
        if group_id in self.user_groups:
            for user_id in self.user_groups[group_id]:
                self.grant_access(user_id, resource_id, actions)


class CredentialManager:
    """Manages user credentials and password security"""
    
    def __init__(self):
        self.password_hashes: Dict[str, str] = {}
        self.password_history: Dict[str, List[str]] = {}
        logger.info("CredentialManager initialized")
    
    def set_password(self, user_id: str, password: str):
        """Set password for user with salted hashing"""
        salt = secrets.token_hex(16)
        hash_value = hashlib.pbkdf2_hmac(
            'sha256',
            password.encode(),
            salt.encode(),
            100000
        ).hex()
        
        combined = f"{salt}${hash_value}"
        self.password_hashes[user_id] = combined
        
        if user_id not in self.password_history:
            self.password_history[user_id] = []
        
        self.password_history[user_id].append(combined)
        logger.info(f"Password set for user: {user_id}")
    
    def verify_password(self, user_id: str, password: str) -> bool:
        """Verify password against stored hash"""
        if user_id not in self.password_hashes:
            return False
        
        combined = self.password_hashes[user_id]
        salt, hash_value = combined.split('$')
        
        test_hash = hashlib.pbkdf2_hmac(
            'sha256',
            password.encode(),
            salt.encode(),
            100000
        ).hex()
        
        return test_hash == hash_value
    
    def check_password_in_history(self, user_id: str, password: str) -> bool:
        """Check if password was used before"""
        if user_id not in self.password_history:
            return False
        
        salt_hash_list = self.password_history[user_id]
        
        for combined in salt_hash_list:
            salt, hash_value = combined.split('$')
            test_hash = hashlib.pbkdf2_hmac(
                'sha256',
                password.encode(),
                salt.encode(),
                100000
            ).hex()
            if test_hash == hash_value:
                return True
        
        return False


class SessionManager:
    """Manages user sessions and session timeouts"""
    
    def __init__(self, session_timeout_minutes: int = 30):
        self.sessions: Dict[str, Dict] = {}
        self.session_timeout = timedelta(minutes=session_timeout_minutes)
        logger.info("SessionManager initialized")
    
    def create_session(self, user_id: str) -> str:
        """Create a new session"""
        import uuid
        session_id = str(uuid.uuid4())
        
        self.sessions[session_id] = {
            'user_id': user_id,
            'created_at': datetime.utcnow(),
            'last_activity': datetime.utcnow(),
            'is_active': True
        }
        
        logger.info(f"Session created for user: {user_id}")
        return session_id
    
    def get_session(self, session_id: str) -> Optional[Dict]:
        """Retrieve session by ID"""
        if session_id not in self.sessions:
            return None
        
        session = self.sessions[session_id]
        
        if not session['is_active']:
            return None
        
        if datetime.utcnow() - session['last_activity'] > self.session_timeout:
            self.invalidate_session(session_id)
            return None
        
        session['last_activity'] = datetime.utcnow()
        return session
    
    def invalidate_session(self, session_id: str):
        """End a session"""
        if session_id in self.sessions:
            self.sessions[session_id]['is_active'] = False
            logger.info(f"Session invalidated: {session_id}")
    
    def invalidate_user_sessions(self, user_id: str):
        """Invalidate all sessions for a user"""
        count = 0
        for session_id, session in self.sessions.items():
            if session['user_id'] == user_id:
                session['is_active'] = False
                count += 1
        
        logger.info(f"Invalidated {count} sessions for user: {user_id}")
