"""
Role-Based Access Control (RBAC)

Implement fine-grained access control:
- Role definitions and management
- Permission assignment
- Resource-level access control
- Audit of access decisions
- JWT token integration
"""

from typing import Dict, List, Set, Optional, Callable, Any
from dataclasses import dataclass, field
from enum import Enum
from datetime import datetime, timedelta
import json


class Permission(Enum):
    """Supported permissions"""
    # Resource access
    READ = "read"
    WRITE = "write"
    DELETE = "delete"
    EXECUTE = "execute"
    
    # Administrative
    ADMIN = "admin"
    MANAGE_USERS = "manage_users"
    MANAGE_ROLES = "manage_roles"
    MANAGE_PERMISSIONS = "manage_permissions"
    
    # Configuration
    CONFIG_READ = "config:read"
    CONFIG_WRITE = "config:write"
    
    # System
    VIEW_LOGS = "view_logs"
    MANAGE_SYSTEM = "manage_system"
    EXPORT_DATA = "export_data"
    IMPORT_DATA = "import_data"


@dataclass
class Role:
    """Represents a user role"""
    name: str
    description: str
    permissions: Set[Permission] = field(default_factory=set)
    created_at: datetime = field(default_factory=datetime.now)
    is_active: bool = True
    resource_restrictions: Dict[str, List[str]] = field(default_factory=dict)  # resource_type -> resource_ids


@dataclass
class User:
    """Represents a user with roles"""
    user_id: str
    username: str
    roles: Set[Role] = field(default_factory=set)
    custom_permissions: Set[Permission] = field(default_factory=set)
    is_active: bool = True
    created_at: datetime = field(default_factory=datetime.now)
    last_login: Optional[datetime] = None


class RBACManager:
    """Manage role-based access control"""
    
    def __init__(self):
        self.roles: Dict[str, Role] = {}
        self.users: Dict[str, User] = {}
        self.access_log: List[Dict[str, Any]] = []
        self._default_roles()
    
    def _default_roles(self):
        """Create default roles"""
        # Admin role
        admin_role = Role(
            name="admin",
            description="Administrator with full access",
            permissions={p for p in Permission},
            is_active=True
        )
        self.roles["admin"] = admin_role
        
        # User role
        user_role = Role(
            name="user",
            description="Standard user with basic access",
            permissions={
                Permission.READ,
                Permission.WRITE,
                Permission.EXECUTE
            },
            is_active=True
        )
        self.roles["user"] = user_role
        
        # Viewer role
        viewer_role = Role(
            name="viewer",
            description="Read-only access",
            permissions={Permission.READ},
            is_active=True
        )
        self.roles["viewer"] = viewer_role
    
    def create_role(
        self,
        name: str,
        description: str,
        permissions: Optional[Set[Permission]] = None
    ) -> bool:
        """Create new role"""
        if name in self.roles:
            return False
        
        self.roles[name] = Role(
            name=name,
            description=description,
            permissions=permissions or set()
        )
        
        return True
    
    def add_permission_to_role(self, role_name: str, permission: Permission) -> bool:
        """Add permission to role"""
        if role_name not in self.roles:
            return False
        
        self.roles[role_name].permissions.add(permission)
        return True
    
    def remove_permission_from_role(self, role_name: str, permission: Permission) -> bool:
        """Remove permission from role"""
        if role_name not in self.roles:
            return False
        
        self.roles[role_name].permissions.discard(permission)
        return True
    
    def create_user(self, user_id: str, username: str) -> bool:
        """Create new user"""
        if user_id in self.users:
            return False
        
        self.users[user_id] = User(
            user_id=user_id,
            username=username
        )
        
        return True
    
    def assign_role_to_user(self, user_id: str, role_name: str) -> bool:
        """Assign role to user"""
        if user_id not in self.users or role_name not in self.roles:
            return False
        
        self.users[user_id].roles.add(self.roles[role_name])
        return True
    
    def remove_role_from_user(self, user_id: str, role_name: str) -> bool:
        """Remove role from user"""
        if user_id not in self.users:
            return False
        
        role = self.roles.get(role_name)
        if role:
            self.users[user_id].roles.discard(role)
            return True
        
        return False
    
    def grant_custom_permission(self, user_id: str, permission: Permission) -> bool:
        """Grant custom permission directly to user"""
        if user_id not in self.users:
            return False
        
        self.users[user_id].custom_permissions.add(permission)
        return True
    
    def revoke_custom_permission(self, user_id: str, permission: Permission) -> bool:
        """Revoke custom permission from user"""
        if user_id not in self.users:
            return False
        
        self.users[user_id].custom_permissions.discard(permission)
        return True
    
    def has_permission(
        self,
        user_id: str,
        permission: Permission,
        resource_type: Optional[str] = None,
        resource_id: Optional[str] = None
    ) -> bool:
        """Check if user has permission"""
        if user_id not in self.users:
            self._log_access(user_id, permission, False, "user_not_found")
            return False
        
        user = self.users[user_id]
        
        if not user.is_active:
            self._log_access(user_id, permission, False, "user_inactive")
            return False
        
        # Check custom permissions
        if permission in user.custom_permissions:
            self._log_access(user_id, permission, True, "custom_permission")
            return True
        
        # Check role permissions
        for role in user.roles:
            if not role.is_active:
                continue
            
            if permission in role.permissions:
                # Check resource restrictions
                if resource_type and resource_id:
                    if resource_type in role.resource_restrictions:
                        allowed_ids = role.resource_restrictions[resource_type]
                        if resource_id not in allowed_ids:
                            self._log_access(user_id, permission, False, "resource_restricted")
                            return False
                
                self._log_access(user_id, permission, True, "role_permission")
                return True
        
        self._log_access(user_id, permission, False, "no_permission")
        return False
    
    def get_user_permissions(self, user_id: str) -> Set[Permission]:
        """Get all permissions for user"""
        if user_id not in self.users:
            return set()
        
        user = self.users[user_id]
        permissions = set(user.custom_permissions)
        
        for role in user.roles:
            if role.is_active:
                permissions.update(role.permissions)
        
        return permissions
    
    def _log_access(
        self,
        user_id: str,
        permission: Permission,
        granted: bool,
        reason: str
    ):
        """Log access decision"""
        self.access_log.append({
            "timestamp": datetime.now().isoformat(),
            "user_id": user_id,
            "permission": permission.value,
            "granted": granted,
            "reason": reason
        })
    
    def get_access_log(self, user_id: Optional[str] = None, hours: int = 24) -> List[Dict[str, Any]]:
        """Get access log"""
        cutoff = datetime.now() - timedelta(hours=hours)
        
        logs = [
            entry for entry in self.access_log
            if datetime.fromisoformat(entry["timestamp"]) > cutoff
        ]
        
        if user_id:
            logs = [entry for entry in logs if entry["user_id"] == user_id]
        
        return logs


class AccessControlDecorator:
    """Decorator for access control in functions"""
    
    def __init__(self, rbac: RBACManager):
        self.rbac = rbac
    
    def require_permission(
        self,
        permission: Permission,
        resource_type: Optional[str] = None
    ):
        """Decorator requiring specific permission"""
        def decorator(func: Callable) -> Callable:
            async def wrapper(*args, **kwargs):
                # Extract user_id from context
                user_id = kwargs.get("user_id") or getattr(args[0], "user_id", None)
                
                if not user_id:
                    raise ValueError("user_id not provided")
                
                # Check permission
                has_perm = self.rbac.has_permission(
                    user_id,
                    permission,
                    resource_type=resource_type,
                    resource_id=kwargs.get("resource_id")
                )
                
                if not has_perm:
                    raise PermissionError(f"User {user_id} does not have {permission.value} permission")
                
                return await func(*args, **kwargs) if hasattr(func, "__await__") else func(*args, **kwargs)
            
            return wrapper
        
        return decorator
    
    def require_admin(self):
        """Decorator requiring admin role"""
        def decorator(func: Callable) -> Callable:
            async def wrapper(*args, **kwargs):
                user_id = kwargs.get("user_id") or getattr(args[0], "user_id", None)
                
                if not user_id:
                    raise ValueError("user_id not provided")
                
                if "admin" not in [role.name for role in self.rbac.users.get(user_id, User(user_id, "")).roles]:
                    raise PermissionError(f"User {user_id} is not an admin")
                
                return await func(*args, **kwargs) if hasattr(func, "__await__") else func(*args, **kwargs)
            
            return wrapper
        
        return decorator


class JWTTokenGenerator:
    """Generate and validate JWT tokens with RBAC claims"""
    
    def __init__(self, rbac: RBACManager, secret_key: str):
        self.rbac = rbac
        self.secret_key = secret_key
    
    def generate_token(self, user_id: str, expiry_hours: int = 24) -> str:
        """Generate JWT token with user permissions"""
        user = self.rbac.users.get(user_id)
        if not user:
            raise ValueError(f"User {user_id} not found")
        
        permissions = self.rbac.get_user_permissions(user_id)
        role_names = [role.name for role in user.roles]
        
        # In production, use PyJWT to create actual JWT token
        # For now, return mock token
        token_data = {
            "user_id": user_id,
            "username": user.username,
            "roles": role_names,
            "permissions": [p.value for p in permissions],
            "exp": (datetime.now() + timedelta(hours=expiry_hours)).isoformat(),
            "iat": datetime.now().isoformat()
        }
        
        return json.dumps(token_data)
    
    def validate_token(self, token: str) -> Optional[Dict[str, Any]]:
        """Validate and decode JWT token"""
        try:
            # In production, use PyJWT to validate
            token_data = json.loads(token)
            
            exp_time = datetime.fromisoformat(token_data["exp"])
            if exp_time < datetime.now():
                return None
            
            return token_data
        except:
            return None


class ResourceAccessControl:
    """Control access to specific resources"""
    
    def __init__(self, rbac: RBACManager):
        self.rbac = rbac
        self.resource_ownership: Dict[str, str] = {}  # resource_id -> user_id
    
    def assign_resource(self, resource_id: str, user_id: str) -> bool:
        """Assign resource to user"""
        self.resource_ownership[resource_id] = user_id
        return True
    
    def can_access_resource(
        self,
        user_id: str,
        resource_id: str,
        permission: Permission
    ) -> bool:
        """Check if user can access resource"""
        # Admin can access anything
        if self.rbac.has_permission(user_id, Permission.ADMIN):
            return True
        
        # Check if user owns resource
        if self.resource_ownership.get(resource_id) == user_id:
            return self.rbac.has_permission(user_id, permission)
        
        # Check group permissions
        return self.rbac.has_permission(user_id, permission)
    
    def transfer_resource(self, resource_id: str, new_user_id: str) -> bool:
        """Transfer resource to another user"""
        if resource_id in self.resource_ownership:
            self.resource_ownership[resource_id] = new_user_id
            return True
        return False


if __name__ == "__main__":
    # Example usage
    rbac = RBACManager()
    
    # Create users
    rbac.create_user("user-123", "john_doe")
    rbac.create_user("user-456", "jane_smith")
    
    # Assign roles
    rbac.assign_role_to_user("user-123", "user")
    rbac.assign_role_to_user("user-456", "admin")
    
    # Check permissions
    print(f"User-123 can read: {rbac.has_permission('user-123', Permission.READ)}")
    print(f"User-123 can admin: {rbac.has_permission('user-123', Permission.ADMIN)}")
    print(f"User-456 can admin: {rbac.has_permission('user-456', Permission.ADMIN)}")
    
    # Get user permissions
    perms = rbac.get_user_permissions("user-123")
    print(f"User-123 permissions: {[p.value for p in perms]}")
    
    # JWT Token
    jwt_gen = JWTTokenGenerator(rbac, "secret-key")
    token = jwt_gen.generate_token("user-123")
    print(f"Generated token: {token[:50]}...")
    
    # Access log
    log = rbac.get_access_log("user-123")
    print(f"Access log entries: {len(log)}")
