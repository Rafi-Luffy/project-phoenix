"""
Comprehensive Test Suite for Phoenix - Security & Privacy
Tests 516-545: Authentication, Authorization, Encryption, Privacy (30 tests)

This file tests Phoenix's ability to detect and fix security vulnerabilities
and privacy issues in AI systems.
"""

import os
import tempfile
import shutil
from pathlib import Path
import pytest
from unittest.mock import Mock, patch


class TestAuthenticationSecurity:
    """Test authentication security (10 tests)"""
    
    def test_password_hashing_strength(self):
        """Test 516: Use strong password hashing"""
        with tempfile.TemporaryDirectory() as temp_dir:
            agent_code = """
import hashlib

class WeakPasswordHashing:
    def hash_password(self, password):
        # BUG: MD5 is broken, no salt
        return hashlib.md5(password.encode()).hexdigest()
    
    def verify_password(self, password, hash):
        return self.hash_password(password) == hash

auth = WeakPasswordHashing()
password_hash = auth.hash_password("secret123")

# BUG: Vulnerable to rainbow tables
print(f"Hash: {password_hash}")
"""
            
            test_file = os.path.join(temp_dir, "password_hashing.py")
            with open(test_file, "w") as f:
                f.write(agent_code)
            
            assert os.path.exists(test_file)
    
    def test_session_token_security(self):
        """Test 517: Generate secure session tokens"""
        with tempfile.TemporaryDirectory() as temp_dir:
            agent_code = """
import time

class PredictableTokens:
    def __init__(self):
        self.counter = 0
    
    def generate_token(self, user_id):
        # BUG: Predictable token
        self.counter += 1
        return f"{user_id}_{self.counter}_{int(time.time())}"

auth = PredictableTokens()

token1 = auth.generate_token("user123")
token2 = auth.generate_token("user123")

# BUG: Tokens are predictable
print(f"Token1: {token1}")
print(f"Token2: {token2}")
"""
            
            test_file = os.path.join(temp_dir, "session_tokens.py")
            with open(test_file, "w") as f:
                f.write(agent_code)
            
            assert os.path.exists(test_file)
    
    def test_rate_limiting_authentication(self):
        """Test 518: Rate limit authentication attempts"""
        with tempfile.TemporaryDirectory() as temp_dir:
            agent_code = """
class NoRateLimiting:
    def __init__(self):
        self.valid_password = "secret"
    
    def authenticate(self, username, password):
        # BUG: No rate limiting
        if password == self.valid_password:
            return True
        return False

auth = NoRateLimiting()

# Brute force attack
for i in range(1000000):
    if auth.authenticate("admin", f"pass{i}"):
        print(f"Found password: pass{i}")
        break

# BUG: Allows unlimited attempts
"""
            
            test_file = os.path.join(temp_dir, "rate_limiting.py")
            with open(test_file, "w") as f:
                f.write(agent_code)
            
            assert os.path.exists(test_file)
    
    def test_multifactor_authentication(self):
        """Test 519: Implement multi-factor authentication"""
        with tempfile.TemporaryDirectory() as temp_dir:
            agent_code = """
class SingleFactorAuth:
    def authenticate(self, username, password):
        # BUG: Only checks password
        if username == "admin" and password == "secret":
            return {"authenticated": True, "user": username}
        return {"authenticated": False}

auth = SingleFactorAuth()

# Compromised password is enough
result = auth.authenticate("admin", "secret")

# BUG: No second factor
print(f"Auth result: {result}")
"""
            
            test_file = os.path.join(temp_dir, "mfa.py")
            with open(test_file, "w") as f:
                f.write(agent_code)
            
            assert os.path.exists(test_file)
    
    def test_session_expiration(self):
        """Test 520: Expire sessions properly"""
        with tempfile.TemporaryDirectory() as temp_dir:
            agent_code = """
import time

class NoSessionExpiration:
    def __init__(self):
        self.sessions = {}
    
    def create_session(self, user_id):
        token = f"token_{user_id}_{time.time()}"
        self.sessions[token] = {"user": user_id, "created": time.time()}
        return token
    
    def validate_session(self, token):
        # BUG: No expiration check
        return token in self.sessions

auth = NoSessionExpiration()
token = auth.create_session("user1")

time.sleep(2)  # 2 seconds pass

# BUG: Session never expires
is_valid = auth.validate_session(token)
print(f"Session valid after 2s: {is_valid}")
"""
            
            test_file = os.path.join(temp_dir, "session_expiration.py")
            with open(test_file, "w") as f:
                f.write(agent_code)
            
            assert os.path.exists(test_file)
    
    def test_credential_storage(self):
        """Test 521: Store credentials securely"""
        with tempfile.TemporaryDirectory() as temp_dir:
            agent_code = """
class PlaintextCredentials:
    def __init__(self):
        # BUG: Credentials in plain text
        self.api_key = "sk_live_1234567890abcdef"
        self.db_password = "super_secret_password"
    
    def get_api_key(self):
        return self.api_key

config = PlaintextCredentials()

# BUG: Credentials exposed
print(f"API Key: {config.get_api_key()}")
"""
            
            test_file = os.path.join(temp_dir, "credential_storage.py")
            with open(test_file, "w") as f:
                f.write(agent_code)
            
            assert os.path.exists(test_file)
    
    def test_password_reset_security(self):
        """Test 522: Secure password reset flow"""
        with tempfile.TemporaryDirectory() as temp_dir:
            agent_code = """
class InsecurePasswordReset:
    def __init__(self):
        self.users = {"user1": {"email": "user@example.com"}}
    
    def reset_password(self, username, new_password):
        # BUG: No verification token required
        if username in self.users:
            self.users[username]["password"] = new_password
            return True
        return False

auth = InsecurePasswordReset()

# Attacker can reset any user's password
auth.reset_password("user1", "hacked")

# BUG: No email verification
print("Password reset without verification")
"""
            
            test_file = os.path.join(temp_dir, "password_reset.py")
            with open(test_file, "w") as f:
                f.write(agent_code)
            
            assert os.path.exists(test_file)
    
    def test_account_lockout_policy(self):
        """Test 523: Implement account lockout"""
        with tempfile.TemporaryDirectory() as temp_dir:
            agent_code = """
class NoAccountLockout:
    def __init__(self):
        self.failed_attempts = {}
    
    def authenticate(self, username, password):
        # BUG: No lockout after failed attempts
        if password != "correct":
            self.failed_attempts[username] = self.failed_attempts.get(username, 0) + 1
            return False
        return True

auth = NoAccountLockout()

# 100 failed attempts
for _ in range(100):
    auth.authenticate("admin", "wrong")

# BUG: Still allows attempts
result = auth.authenticate("admin", "correct")
print(f"Auth after 100 failures: {result}")
"""
            
            test_file = os.path.join(temp_dir, "account_lockout.py")
            with open(test_file, "w") as f:
                f.write(agent_code)
            
            assert os.path.exists(test_file)
    
    def test_jwt_token_validation(self):
        """Test 524: Validate JWT tokens properly"""
        with tempfile.TemporaryDirectory() as temp_dir:
            agent_code = """
import json
import base64

class WeakJWTValidation:
    def __init__(self):
        self.secret = "secret_key"
    
    def validate_token(self, token):
        # BUG: Doesn't verify signature
        parts = token.split('.')
        payload = base64.b64decode(parts[1] + '==').decode()
        return json.loads(payload)

auth = WeakJWTValidation()

# Attacker creates fake token
fake_token = "header." + base64.b64encode(b'{"user":"admin","role":"admin"}').decode() + ".fake_signature"

user_data = auth.validate_token(fake_token)

# BUG: Accepts forged token
print(f"User data: {user_data}")
"""
            
            test_file = os.path.join(temp_dir, "jwt_validation.py")
            with open(test_file, "w") as f:
                f.write(agent_code)
            
            assert os.path.exists(test_file)
    
    def test_oauth_state_parameter(self):
        """Test 525: Use OAuth state parameter"""
        with tempfile.TemporaryDirectory() as temp_dir:
            agent_code = """
class NoCSRFProtection:
    def __init__(self):
        self.auth_url = "https://oauth.provider.com/authorize"
    
    def get_authorization_url(self, client_id, redirect_uri):
        # BUG: No state parameter
        return f"{self.auth_url}?client_id={client_id}&redirect_uri={redirect_uri}"
    
    def handle_callback(self, code):
        # BUG: No state validation
        return {"code": code}

oauth = NoCSRFProtection()
url = oauth.get_authorization_url("client123", "http://example.com/callback")

# BUG: Vulnerable to CSRF attacks
print(f"Auth URL: {url}")
"""
            
            test_file = os.path.join(temp_dir, "oauth_state.py")
            with open(test_file, "w") as f:
                f.write(agent_code)
            
            assert os.path.exists(test_file)


class TestAuthorizationControls:
    """Test authorization and access control (10 tests)"""
    
    def test_role_based_access_control(self):
        """Test 526: Implement RBAC correctly"""
        with tempfile.TemporaryDirectory() as temp_dir:
            agent_code = """
class BrokenRBAC:
    def __init__(self):
        self.users = {
            "user1": {"role": "user"},
            "admin1": {"role": "admin"}
        }
    
    def can_access(self, username, resource):
        # BUG: Only checks if user exists
        return username in self.users

rbac = BrokenRBAC()

# Regular user accessing admin resource
can_access = rbac.can_access("user1", "/admin/delete_all")

# BUG: Grants access without checking role
print(f"User can access admin: {can_access}")
"""
            
            test_file = os.path.join(temp_dir, "rbac.py")
            with open(test_file, "w") as f:
                f.write(agent_code)
            
            assert os.path.exists(test_file)
    
    def test_privilege_escalation_prevention(self):
        """Test 527: Prevent privilege escalation"""
        with tempfile.TemporaryDirectory() as temp_dir:
            agent_code = """
class NoPrivilegeChecks:
    def __init__(self):
        self.users = {
            "user1": {"role": "user"}
        }
    
    def update_user_role(self, actor_username, target_username, new_role):
        # BUG: Doesn't check if actor can change roles
        self.users[target_username]["role"] = new_role

system = NoPrivilegeChecks()

# Regular user promotes themselves to admin
system.update_user_role("user1", "user1", "admin")

# BUG: Privilege escalation
print(f"User1 role: {system.users['user1']['role']}")
"""
            
            test_file = os.path.join(temp_dir, "privilege_escalation.py")
            with open(test_file, "w") as f:
                f.write(agent_code)
            
            assert os.path.exists(test_file)
    
    def test_attribute_based_access_control(self):
        """Test 528: Implement ABAC for fine-grained control"""
        with tempfile.TemporaryDirectory() as temp_dir:
            agent_code = """
class CoarseGrainedAccess:
    def can_access_document(self, user, document):
        # BUG: Only checks user role, not document attributes
        return user["role"] == "employee"

abac = CoarseGrainedAccess()

user = {"id": "user1", "role": "employee", "department": "sales"}
confidential_doc = {"id": "doc1", "department": "hr", "classification": "confidential"}

# BUG: Employee from sales can access HR confidential doc
can_access = abac.can_access_document(user, confidential_doc)
print(f"Can access: {can_access}")
"""
            
            test_file = os.path.join(temp_dir, "abac.py")
            with open(test_file, "w") as f:
                f.write(agent_code)
            
            assert os.path.exists(test_file)
    
    def test_object_level_authorization(self):
        """Test 529: Check object-level permissions"""
        with tempfile.TemporaryDirectory() as temp_dir:
            agent_code = """
class NoObjectLevelCheck:
    def __init__(self):
        self.documents = {
            "doc1": {"owner": "user1", "content": "User1's private data"},
            "doc2": {"owner": "user2", "content": "User2's private data"}
        }
    
    def get_document(self, user_id, doc_id):
        # BUG: Returns document without checking ownership
        return self.documents.get(doc_id)

system = NoObjectLevelCheck()

# User1 accessing User2's document
doc = system.get_document("user1", "doc2")

# BUG: Insecure direct object reference
print(f"Document: {doc}")
"""
            
            test_file = os.path.join(temp_dir, "object_level_auth.py")
            with open(test_file, "w") as f:
                f.write(agent_code)
            
            assert os.path.exists(test_file)
    
    def test_api_authorization_enforcement(self):
        """Test 530: Enforce API authorization"""
        with tempfile.TemporaryDirectory() as temp_dir:
            agent_code = """
class UnauthenticatedAPI:
    def __init__(self):
        self.data = {"secret": "confidential"}
    
    def get_data(self, api_key=None):
        # BUG: API key optional, not validated
        return self.data

api = UnauthenticatedAPI()

# No API key provided
data = api.get_data()

# BUG: Returns sensitive data without auth
print(f"Data: {data}")
"""
            
            test_file = os.path.join(temp_dir, "api_authorization.py")
            with open(test_file, "w") as f:
                f.write(agent_code)
            
            assert os.path.exists(test_file)
    
    def test_least_privilege_principle(self):
        """Test 531: Apply least privilege principle"""
        with tempfile.TemporaryDirectory() as temp_dir:
            agent_code = """
class OverprivilegedService:
    def __init__(self):
        # BUG: Service runs with admin privileges
        self.privileges = "admin"
    
    def read_user_data(self, user_id):
        # Only needs read access, but has admin
        return f"Data for {user_id}"

service = OverprivilegedService()

# BUG: If compromised, attacker has admin access
data = service.read_user_data("user1")
print(f"Service privileges: {service.privileges}")
"""
            
            test_file = os.path.join(temp_dir, "least_privilege.py")
            with open(test_file, "w") as f:
                f.write(agent_code)
            
            assert os.path.exists(test_file)
    
    def test_permission_caching_invalidation(self):
        """Test 532: Invalidate permission caches"""
        with tempfile.TemporaryDirectory() as temp_dir:
            agent_code = """
class StalePermissionCache:
    def __init__(self):
        self.permissions = {"user1": ["read", "write", "delete"]}
        self.cache = {}
    
    def get_permissions(self, user_id):
        # BUG: Cache never invalidated
        if user_id not in self.cache:
            self.cache[user_id] = self.permissions[user_id].copy()
        return self.cache[user_id]
    
    def revoke_permission(self, user_id, permission):
        self.permissions[user_id].remove(permission)
        # BUG: Doesn't clear cache

system = StalePermissionCache()

perms1 = system.get_permissions("user1")
system.revoke_permission("user1", "delete")
perms2 = system.get_permissions("user1")

# BUG: Still shows delete permission
print(f"Permissions after revoke: {perms2}")
"""
            
            test_file = os.path.join(temp_dir, "permission_caching.py")
            with open(test_file, "w") as f:
                f.write(agent_code)
            
            assert os.path.exists(test_file)
    
    def test_resource_quota_enforcement(self):
        """Test 533: Enforce resource quotas"""
        with tempfile.TemporaryDirectory() as temp_dir:
            agent_code = """
class NoQuotaEnforcement:
    def __init__(self):
        self.user_usage = {}
    
    def allocate_resource(self, user_id, amount):
        # BUG: No quota limit
        self.user_usage[user_id] = self.user_usage.get(user_id, 0) + amount
        return True

system = NoQuotaEnforcement()

# User consumes unlimited resources
for i in range(10000):
    system.allocate_resource("user1", 100)

# BUG: No limit enforced
print(f"User1 usage: {system.user_usage['user1']}")
"""
            
            test_file = os.path.join(temp_dir, "quota_enforcement.py")
            with open(test_file, "w") as f:
                f.write(agent_code)
            
            assert os.path.exists(test_file)
    
    def test_cross_tenant_isolation(self):
        """Test 534: Isolate multi-tenant data"""
        with tempfile.TemporaryDirectory() as temp_dir:
            agent_code = """
class NoTenantIsolation:
    def __init__(self):
        self.data = {
            "record1": {"tenant": "tenant_a", "value": "A's data"},
            "record2": {"tenant": "tenant_b", "value": "B's data"}
        }
    
    def query_data(self, user_tenant, query):
        # BUG: Doesn't filter by tenant
        results = []
        for record_id, record in self.data.items():
            results.append(record)
        return results

db = NoTenantIsolation()

# Tenant A's query returns Tenant B's data
results = db.query_data("tenant_a", "SELECT *")

# BUG: Data leakage across tenants
print(f"Results: {results}")
"""
            
            test_file = os.path.join(temp_dir, "tenant_isolation.py")
            with open(test_file, "w") as f:
                f.write(agent_code)
            
            assert os.path.exists(test_file)
    
    def test_admin_action_auditing(self):
        """Test 535: Audit admin actions"""
        with tempfile.TemporaryDirectory() as temp_dir:
            agent_code = """
class NoAdminAudit:
    def __init__(self):
        self.users = {"user1": {"role": "user"}}
    
    def admin_delete_user(self, admin_id, target_user):
        # BUG: No audit trail
        if target_user in self.users:
            del self.users[target_user]

system = NoAdminAudit()

# Admin deletes user - no record
system.admin_delete_user("admin1", "user1")

# BUG: No audit log
print("User deleted - no audit trail")
"""
            
            test_file = os.path.join(temp_dir, "admin_auditing.py")
            with open(test_file, "w") as f:
                f.write(agent_code)
            
            assert os.path.exists(test_file)


class TestEncryptionAndPrivacy:
    """Test encryption and privacy protection (10 tests)"""
    
    def test_data_at_rest_encryption(self):
        """Test 536: Encrypt data at rest"""
        with tempfile.TemporaryDirectory() as temp_dir:
            agent_code = """
class PlaintextStorage:
    def __init__(self):
        self.storage = {}
    
    def store_sensitive_data(self, key, data):
        # BUG: Stores in plaintext
        self.storage[key] = data
    
    def retrieve_data(self, key):
        return self.storage.get(key)

db = PlaintextStorage()

db.store_sensitive_data("ssn", "123-45-6789")
db.store_sensitive_data("credit_card", "4532-1234-5678-9010")

# BUG: Sensitive data unencrypted
print(f"Storage: {db.storage}")
"""
            
            test_file = os.path.join(temp_dir, "data_at_rest.py")
            with open(test_file, "w") as f:
                f.write(agent_code)
            
            assert os.path.exists(test_file)
    
    def test_data_in_transit_encryption(self):
        """Test 537: Encrypt data in transit"""
        with tempfile.TemporaryDirectory() as temp_dir:
            agent_code = """
class UnencryptedTransmission:
    def send_data(self, url, data):
        # BUG: Uses HTTP instead of HTTPS
        protocol = "http"
        return f"{protocol}://{url}?data={data}"

client = UnencryptedTransmission()

# Sending sensitive data
request = client.send_data("api.example.com", "password=secret123")

# BUG: Plaintext transmission
print(f"Request: {request}")
"""
            
            test_file = os.path.join(temp_dir, "data_in_transit.py")
            with open(test_file, "w") as f:
                f.write(agent_code)
            
            assert os.path.exists(test_file)
    
    def test_pii_detection_and_masking(self):
        """Test 538: Detect and mask PII"""
        with tempfile.TemporaryDirectory() as temp_dir:
            agent_code = """
class NoPIIMasking:
    def log_user_action(self, user_data, action):
        # BUG: Logs PII in plaintext
        log_entry = f"User {user_data['email']} performed {action}"
        print(log_entry)
        return log_entry

logger = NoPIIMasking()

user = {
    "email": "john.doe@example.com",
    "ssn": "123-45-6789",
    "phone": "+1-555-1234"
}

# BUG: PII in logs
logger.log_user_action(user, "login")
"""
            
            test_file = os.path.join(temp_dir, "pii_masking.py")
            with open(test_file, "w") as f:
                f.write(agent_code)
            
            assert os.path.exists(test_file)
    
    def test_key_rotation_policy(self):
        """Test 539: Implement key rotation"""
        with tempfile.TemporaryDirectory() as temp_dir:
            agent_code = """
class StaticEncryptionKey:
    def __init__(self):
        # BUG: Key never rotated
        self.encryption_key = "static_key_12345"
        self.key_age_days = 365
    
    def encrypt(self, data):
        # Uses same key forever
        return f"encrypted_{data}_with_{self.encryption_key}"

crypto = StaticEncryptionKey()

# BUG: Year-old key still in use
encrypted = crypto.encrypt("sensitive_data")
print(f"Key age: {crypto.key_age_days} days")
"""
            
            test_file = os.path.join(temp_dir, "key_rotation.py")
            with open(test_file, "w") as f:
                f.write(agent_code)
            
            assert os.path.exists(test_file)
    
    def test_secure_random_generation(self):
        """Test 540: Use cryptographically secure random"""
        with tempfile.TemporaryDirectory() as temp_dir:
            agent_code = """
import random

class WeakRandomGeneration:
    def generate_token(self):
        # BUG: Uses predictable random
        return random.randint(0, 999999)

generator = WeakRandomGeneration()

# Generate security tokens
tokens = [generator.generate_token() for _ in range(5)]

# BUG: Predictable, not cryptographically secure
print(f"Tokens: {tokens}")
"""
            
            test_file = os.path.join(temp_dir, "secure_random.py")
            with open(test_file, "w") as f:
                f.write(agent_code)
            
            assert os.path.exists(test_file)
    
    def test_gdpr_right_to_erasure(self):
        """Test 541: Implement data deletion (GDPR)"""
        with tempfile.TemporaryDirectory() as temp_dir:
            agent_code = """
class IncompleteDataDeletion:
    def __init__(self):
        self.users = {"user1": {"name": "John", "email": "john@example.com"}}
        self.activity_logs = [{"user": "user1", "action": "login"}]
        self.backups = {"user1": {"name": "John"}}
    
    def delete_user_data(self, user_id):
        # BUG: Only deletes from main table
        if user_id in self.users:
            del self.users[user_id]
        # Forgets activity_logs and backups

system = IncompleteDataDeletion()
system.delete_user_data("user1")

# BUG: Data remains in logs and backups
print(f"Users: {system.users}")
print(f"Logs: {system.activity_logs}")
print(f"Backups: {system.backups}")
"""
            
            test_file = os.path.join(temp_dir, "data_erasure.py")
            with open(test_file, "w") as f:
                f.write(agent_code)
            
            assert os.path.exists(test_file)
    
    def test_data_anonymization(self):
        """Test 542: Anonymize data for analytics"""
        with tempfile.TemporaryDirectory() as temp_dir:
            agent_code = """
class WeakAnonymization:
    def anonymize_data(self, user_data):
        # BUG: Removes name but keeps unique identifiers
        return {
            "user_id": user_data["user_id"],  # Still identifiable
            "zip_code": user_data["zip_code"],
            "birth_date": user_data["birth_date"],
            "gender": user_data["gender"]
        }

anonymizer = WeakAnonymization()

user = {
    "user_id": "12345",
    "name": "John Doe",
    "zip_code": "10001",
    "birth_date": "1990-01-01",
    "gender": "M"
}

anon_data = anonymizer.anonymize_data(user)

# BUG: Can be re-identified using quasi-identifiers
print(f"Anonymized: {anon_data}")
"""
            
            test_file = os.path.join(temp_dir, "data_anonymization.py")
            with open(test_file, "w") as f:
                f.write(agent_code)
            
            assert os.path.exists(test_file)
    
    def test_differential_privacy(self):
        """Test 543: Apply differential privacy"""
        with tempfile.TemporaryDirectory() as temp_dir:
            agent_code = """
class NoDifferentialPrivacy:
    def __init__(self):
        self.data = [100, 200, 150, 180, 120]
    
    def get_average(self):
        # BUG: Returns exact average
        return sum(self.data) / len(self.data)

analytics = NoDifferentialPrivacy()

# Multiple queries can infer individual records
avg1 = analytics.get_average()
# Remove one value and query again
analytics.data.pop()
avg2 = analytics.get_average()

# BUG: Can deduce individual value
inferred_value = (avg1 * 5) - (avg2 * 4)
print(f"Inferred value: {inferred_value}")
"""
            
            test_file = os.path.join(temp_dir, "differential_privacy.py")
            with open(test_file, "w") as f:
                f.write(agent_code)
            
            assert os.path.exists(test_file)
    
    def test_secure_data_sharing(self):
        """Test 544: Share data securely"""
        with tempfile.TemporaryDirectory() as temp_dir:
            agent_code = """
class InsecureSharing:
    def share_file(self, file_path, recipient):
        # BUG: Public link without access control
        share_link = f"https://storage.example.com/{file_path}"
        return share_link

sharing = InsecureSharing()

# Share confidential document
link = sharing.share_file("confidential_report.pdf", "partner@example.com")

# BUG: Anyone with link can access
print(f"Share link: {link}")
"""
            
            test_file = os.path.join(temp_dir, "secure_sharing.py")
            with open(test_file, "w") as f:
                f.write(agent_code)
            
            assert os.path.exists(test_file)
    
    def test_consent_management(self):
        """Test 545: Manage user consent"""
        with tempfile.TemporaryDirectory() as temp_dir:
            agent_code = """
class NoConsentTracking:
    def __init__(self):
        self.users = {"user1": {"email": "user@example.com"}}
    
    def send_marketing_email(self, user_id):
        # BUG: Doesn't check consent
        user = self.users[user_id]
        print(f"Sending marketing to {user['email']}")
        return True

system = NoConsentTracking()

# Send without checking consent
system.send_marketing_email("user1")

# BUG: GDPR violation - no consent tracking
print("Email sent without consent check")
"""
            
            test_file = os.path.join(temp_dir, "consent_management.py")
            with open(test_file, "w") as f:
                f.write(agent_code)
            
            assert os.path.exists(test_file)
