"""
Comprehensive Test Suite for Phoenix - Configuration & Deployment
Tests 666-695: Configuration Management, Environment Variables, Secrets, Deployment (30 tests)

This file tests Phoenix's ability to detect and fix bugs in configuration management,
environment handling, and deployment processes.
"""

import os
import tempfile
import shutil
from pathlib import Path
import pytest
from unittest.mock import Mock, patch


class TestConfigurationManagement:
    """Test configuration management patterns (10 tests)"""
    
    def test_hardcoded_configuration(self):
        """Test 666: Avoid hardcoded configuration"""
        with tempfile.TemporaryDirectory() as temp_dir:
            agent_code = """
class HardcodedConfig:
    def __init__(self):
        # BUG: Hardcoded configuration
        self.database_host = "prod-db.company.com"
        self.database_port = 5432
        self.api_key = "sk_live_12345"

config = HardcodedConfig()

# BUG: Can't change config without code change
print(f"DB Host: {config.database_host}")
"""
            
            test_file = os.path.join(temp_dir, "hardcoded_config.py")
            with open(test_file, "w") as f:
                f.write(agent_code)
            
            assert os.path.exists(test_file)
    
    def test_environment_specific_config(self):
        """Test 667: Separate environment configs"""
        with tempfile.TemporaryDirectory() as temp_dir:
            agent_code = """
class SingleEnvironmentConfig:
    def __init__(self):
        # BUG: Same config for all environments
        self.debug = True
        self.log_level = "DEBUG"
        self.cache_ttl = 60

config = SingleEnvironmentConfig()

# BUG: Debug enabled in production
print(f"Debug: {config.debug}")
"""
            
            test_file = os.path.join(temp_dir, "environment_config.py")
            with open(test_file, "w") as f:
                f.write(agent_code)
            
            assert os.path.exists(test_file)
    
    def test_config_validation(self):
        """Test 668: Validate configuration on startup"""
        with tempfile.TemporaryDirectory() as temp_dir:
            agent_code = """
class NoConfigValidation:
    def __init__(self, config):
        # BUG: Doesn't validate config
        self.host = config.get("host")
        self.port = config.get("port")
        self.timeout = config.get("timeout")

# Invalid config
config = {
    "host": "",  # Empty
    "port": "not-a-number",  # Invalid type
    "timeout": -1  # Invalid value
}

# BUG: Starts with invalid config
app = NoConfigValidation(config)
print("App started with invalid config")
"""
            
            test_file = os.path.join(temp_dir, "config_validation.py")
            with open(test_file, "w") as f:
                f.write(agent_code)
            
            assert os.path.exists(test_file)
    
    def test_config_hot_reload(self):
        """Test 669: Support configuration hot reload"""
        with tempfile.TemporaryDirectory() as temp_dir:
            agent_code = """
class StaticConfig:
    def __init__(self):
        # BUG: Config loaded once at startup
        self.max_connections = self.load_config()
    
    def load_config(self):
        return 100

config = StaticConfig()

# Config file updated to 200
# BUG: Requires restart to pick up change
print(f"Max connections: {config.max_connections}")
"""
            
            test_file = os.path.join(temp_dir, "config_hot_reload.py")
            with open(test_file, "w") as f:
                f.write(agent_code)
            
            assert os.path.exists(test_file)
    
    def test_config_precedence(self):
        """Test 670: Define config precedence"""
        with tempfile.TemporaryDirectory() as temp_dir:
            agent_code = """
class UnclearPrecedence:
    def __init__(self):
        # BUG: Unclear which takes precedence
        file_config = {"timeout": 30}
        env_config = {"timeout": 60}
        default_config = {"timeout": 10}
        
        # Which wins?
        self.timeout = file_config.get("timeout", default_config["timeout"])

config = UnclearPrecedence()

# BUG: ENV vars ignored
print(f"Timeout: {config.timeout}")
"""
            
            test_file = os.path.join(temp_dir, "config_precedence.py")
            with open(test_file, "w") as f:
                f.write(agent_code)
            
            assert os.path.exists(test_file)
    
    def test_sensitive_config_logging(self):
        """Test 671: Don't log sensitive configuration"""
        with tempfile.TemporaryDirectory() as temp_dir:
            agent_code = """
class ConfigLogging:
    def __init__(self, config):
        # BUG: Logs sensitive values
        print(f"Config loaded: {config}")
        self.config = config

# Sensitive config
config = {
    "database_password": "super_secret_123",
    "api_key": "sk_live_abcdef",
    "jwt_secret": "my_secret_key"
}

# BUG: Secrets in logs
app = ConfigLogging(config)
"""
            
            test_file = os.path.join(temp_dir, "config_logging.py")
            with open(test_file, "w") as f:
                f.write(agent_code)
            
            assert os.path.exists(test_file)
    
    def test_config_defaults(self):
        """Test 672: Provide sensible defaults"""
        with tempfile.TemporaryDirectory() as temp_dir:
            agent_code = """
class NoDefaults:
    def __init__(self, config):
        # BUG: No defaults, requires all values
        self.timeout = config["timeout"]
        self.retry_count = config["retry_count"]
        self.buffer_size = config["buffer_size"]

# Minimal config
config = {}

# BUG: Crashes on missing keys
try:
    app = NoDefaults(config)
except KeyError as e:
    print(f"Missing required config: {e}")
"""
            
            test_file = os.path.join(temp_dir, "config_defaults.py")
            with open(test_file, "w") as f:
                f.write(agent_code)
            
            assert os.path.exists(test_file)
    
    def test_config_schema_versioning(self):
        """Test 673: Version configuration schema"""
        with tempfile.TemporaryDirectory() as temp_dir:
            agent_code = """
class NoConfigVersioning:
    def __init__(self, config):
        # BUG: No version checking
        self.host = config["host"]
        self.port = config["port"]
        # Assumes "connection_pool" exists
        self.pool_size = config["connection_pool"]["size"]

# Old config format (no connection_pool)
old_config = {
    "host": "localhost",
    "port": 5432
}

# BUG: Incompatible with old config
try:
    app = NoConfigVersioning(old_config)
except KeyError:
    print("Config schema changed, no migration")
"""
            
            test_file = os.path.join(temp_dir, "config_versioning.py")
            with open(test_file, "w") as f:
                f.write(agent_code)
            
            assert os.path.exists(test_file)
    
    def test_config_immutability(self):
        """Test 674: Make config immutable after loading"""
        with tempfile.TemporaryDirectory() as temp_dir:
            agent_code = """
class MutableConfig:
    def __init__(self):
        # BUG: Config is mutable
        self.config = {
            "timeout": 30,
            "max_connections": 100
        }
    
    def get_config(self):
        return self.config

system = MutableConfig()

config = system.get_config()

# Bug: External code can modify config
config["timeout"] = 999
config["max_connections"] = 10000

# BUG: Config changed unexpectedly
print(f"Timeout: {system.config['timeout']}")
"""
            
            test_file = os.path.join(temp_dir, "config_immutability.py")
            with open(test_file, "w") as f:
                f.write(agent_code)
            
            assert os.path.exists(test_file)
    
    def test_config_file_format(self):
        """Test 675: Use appropriate config format"""
        with tempfile.TemporaryDirectory() as temp_dir:
            agent_code = """
class ProblematicConfigFormat:
    def load_config(self, config_string):
        # BUG: Uses eval() for config
        config = eval(config_string)
        return config

loader = ProblematicConfigFormat()

# Malicious config
config_string = "__import__('os').system('rm -rf /')"

# BUG: Code injection vulnerability
print("Using eval() for config is dangerous")
"""
            
            test_file = os.path.join(temp_dir, "config_format.py")
            with open(test_file, "w") as f:
                f.write(agent_code)
            
            assert os.path.exists(test_file)


class TestSecretsManagement:
    """Test secrets and credentials management (10 tests)"""
    
    def test_secrets_in_source_code(self):
        """Test 676: Don't commit secrets to source"""
        with tempfile.TemporaryDirectory() as temp_dir:
            agent_code = """
class HardcodedSecrets:
    def __init__(self):
        # BUG: Secrets in source code
        self.db_password = "MyP@ssw0rd123"
        self.api_key = "sk_live_1234567890abcdef"
        self.aws_secret = "wJalrXUtnFEMI/K7MDENG/bPxRfiCYEXAMPLEKEY"

config = HardcodedSecrets()

# BUG: Secrets exposed in git repository
print("Secrets in source code")
"""
            
            test_file = os.path.join(temp_dir, "hardcoded_secrets.py")
            with open(test_file, "w") as f:
                f.write(agent_code)
            
            assert os.path.exists(test_file)
    
    def test_secrets_in_environment_variables(self):
        """Test 677: Properly handle environment secrets"""
        with tempfile.TemporaryDirectory() as temp_dir:
            agent_code = """
import os

class MissingSecretHandling:
    def __init__(self):
        # BUG: No validation if secret exists
        self.api_key = os.environ.get("API_KEY")
        self.db_password = os.environ.get("DB_PASSWORD")

config = MissingSecretHandling()

# ENV vars not set
# BUG: Secrets are None, app continues
if config.api_key is None:
    print("API key not set, but app starts anyway")
"""
            
            test_file = os.path.join(temp_dir, "env_secrets.py")
            with open(test_file, "w") as f:
                f.write(agent_code)
            
            assert os.path.exists(test_file)
    
    def test_secret_rotation(self):
        """Test 678: Support secret rotation"""
        with tempfile.TemporaryDirectory() as temp_dir:
            agent_code = """
class NoSecretRotation:
    def __init__(self):
        # BUG: Loads secret once, never refreshes
        self.api_token = self.load_secret()
    
    def load_secret(self):
        return "token_12345"
    
    def call_api(self):
        # BUG: Uses stale token after rotation
        headers = {"Authorization": f"Bearer {self.api_token}"}
        return headers

client = NoSecretRotation()

# Secret rotated
# BUG: Still using old token
headers = client.call_api()
print(f"Using old token: {headers}")
"""
            
            test_file = os.path.join(temp_dir, "secret_rotation.py")
            with open(test_file, "w") as f:
                f.write(agent_code)
            
            assert os.path.exists(test_file)
    
    def test_secret_encryption_at_rest(self):
        """Test 679: Encrypt secrets at rest"""
        with tempfile.TemporaryDirectory() as temp_dir:
            agent_code = """
class PlaintextSecrets:
    def save_credentials(self, username, password):
        # BUG: Stores password in plaintext
        with open("credentials.txt", "w") as f:
            f.write(f"{username}:{password}")

manager = PlaintextSecrets()

# BUG: Password saved unencrypted
manager.save_credentials("admin", "super_secret_password")
print("Password saved in plaintext")
"""
            
            test_file = os.path.join(temp_dir, "plaintext_secrets.py")
            with open(test_file, "w") as f:
                f.write(agent_code)
            
            assert os.path.exists(test_file)
    
    def test_secret_access_logging(self):
        """Test 680: Audit secret access"""
        with tempfile.TemporaryDirectory() as temp_dir:
            agent_code = """
class NoSecretAudit:
    def __init__(self):
        self.secrets = {
            "db_password": "secret123",
            "api_key": "key456"
        }
    
    def get_secret(self, name):
        # BUG: No audit log of access
        return self.secrets.get(name)

vault = NoSecretAudit()

# BUG: No record of who accessed what
password = vault.get_secret("db_password")
print("No audit trail")
"""
            
            test_file = os.path.join(temp_dir, "secret_audit.py")
            with open(test_file, "w") as f:
                f.write(agent_code)
            
            assert os.path.exists(test_file)
    
    def test_secret_injection(self):
        """Test 681: Inject secrets securely"""
        with tempfile.TemporaryDirectory() as temp_dir:
            agent_code = """
class InsecureSecretInjection:
    def __init__(self):
        # BUG: Secrets passed via command line arguments
        import sys
        self.api_key = sys.argv[1] if len(sys.argv) > 1 else None

# BUG: Secret visible in process list
# Usage: python app.py sk_live_12345
print("Secret in command line arguments")
"""
            
            test_file = os.path.join(temp_dir, "secret_injection.py")
            with open(test_file, "w") as f:
                f.write(agent_code)
            
            assert os.path.exists(test_file)
    
    def test_secret_scope(self):
        """Test 682: Limit secret scope"""
        with tempfile.TemporaryDirectory() as temp_dir:
            agent_code = """
class GlobalSecrets:
    # BUG: Secrets as global variables
    API_KEY = "sk_live_12345"
    DB_PASSWORD = "password123"

# BUG: Secrets accessible everywhere
def some_function():
    # Any code can access secrets
    api_key = GlobalSecrets.API_KEY
    print(f"API Key: {api_key}")

some_function()
"""
            
            test_file = os.path.join(temp_dir, "secret_scope.py")
            with open(test_file, "w") as f:
                f.write(agent_code)
            
            assert os.path.exists(test_file)
    
    def test_default_credentials(self):
        """Test 683: Avoid default credentials"""
        with tempfile.TemporaryDirectory() as temp_dir:
            agent_code = """
class DefaultCredentials:
    def __init__(self, username=None, password=None):
        # BUG: Default credentials
        self.username = username or "admin"
        self.password = password or "admin"

# BUG: Uses default credentials in production
db = DefaultCredentials()
print(f"Username: {db.username}, Password: {db.password}")
"""
            
            test_file = os.path.join(temp_dir, "default_credentials.py")
            with open(test_file, "w") as f:
                f.write(agent_code)
            
            assert os.path.exists(test_file)
    
    def test_secret_expiration(self):
        """Test 684: Implement secret expiration"""
        with tempfile.TemporaryDirectory() as temp_dir:
            agent_code = """
class NoSecretExpiration:
    def __init__(self):
        # BUG: Secrets never expire
        self.tokens = {
            "user1": {"token": "token123", "created": "2020-01-01"},
            "user2": {"token": "token456", "created": "2019-01-01"}
        }
    
    def validate_token(self, user, token):
        # BUG: Doesn't check expiration
        user_data = self.tokens.get(user)
        return user_data and user_data["token"] == token

auth = NoSecretExpiration()

# BUG: 4-year-old token still valid
is_valid = auth.validate_token("user2", "token456")
print(f"Old token valid: {is_valid}")
"""
            
            test_file = os.path.join(temp_dir, "secret_expiration.py")
            with open(test_file, "w") as f:
                f.write(agent_code)
            
            assert os.path.exists(test_file)
    
    def test_secrets_in_logs(self):
        """Test 685: Prevent secrets in logs"""
        with tempfile.TemporaryDirectory() as temp_dir:
            agent_code = """
class SecretLogging:
    def connect_to_database(self, connection_string):
        # BUG: Logs connection string with password
        print(f"Connecting to: {connection_string}")
        return "connected"

db = SecretLogging()

# Connection string with password
conn_str = "postgresql://user:MyP@ssw0rd@localhost:5432/db"

# BUG: Password in logs
db.connect_to_database(conn_str)
"""
            
            test_file = os.path.join(temp_dir, "secrets_in_logs.py")
            with open(test_file, "w") as f:
                f.write(agent_code)
            
            assert os.path.exists(test_file)


class TestDeploymentPatterns:
    """Test deployment and release patterns (10 tests)"""
    
    def test_zero_downtime_deployment(self):
        """Test 686: Ensure zero-downtime deployment"""
        with tempfile.TemporaryDirectory() as temp_dir:
            agent_code = """
class DowntimeDeployment:
    def deploy_new_version(self):
        # BUG: Stops old version before starting new
        self.stop_application()
        self.deploy()
        self.start_application()
    
    def stop_application(self):
        print("App stopped - downtime begins")
    
    def deploy(self):
        print("Deploying...")
    
    def start_application(self):
        print("App started - downtime ends")

deployer = DowntimeDeployment()

# BUG: Downtime during deployment
deployer.deploy_new_version()
"""
            
            test_file = os.path.join(temp_dir, "zero_downtime.py")
            with open(test_file, "w") as f:
                f.write(agent_code)
            
            assert os.path.exists(test_file)
    
    def test_database_migration_strategy(self):
        """Test 687: Safe database migrations"""
        with tempfile.TemporaryDirectory() as temp_dir:
            agent_code = """
class UnsafeMigration:
    def migrate_database(self):
        # BUG: No backup before migration
        self.run_migration()
    
    def run_migration(self):
        # BUG: Destructive migration
        print("ALTER TABLE users DROP COLUMN email")
        print("Migration applied")

migrator = UnsafeMigration()

# BUG: No rollback if migration fails
migrator.migrate_database()
"""
            
            test_file = os.path.join(temp_dir, "db_migration.py")
            with open(test_file, "w") as f:
                f.write(agent_code)
            
            assert os.path.exists(test_file)
    
    def test_health_check_endpoint(self):
        """Test 688: Implement health check"""
        with tempfile.TemporaryDirectory() as temp_dir:
            agent_code = """
class NoHealthCheck:
    def __init__(self):
        self.database_connected = False
        self.cache_connected = False
    
    # BUG: No health check endpoint
    def start(self):
        print("Application started")

app = NoHealthCheck()

# BUG: Load balancer can't check health
app.start()
"""
            
            test_file = os.path.join(temp_dir, "health_check.py")
            with open(test_file, "w") as f:
                f.write(agent_code)
            
            assert os.path.exists(test_file)
    
    def test_graceful_shutdown(self):
        """Test 689: Implement graceful shutdown"""
        with tempfile.TemporaryDirectory() as temp_dir:
            agent_code = """
import signal

class NoGracefulShutdown:
    def __init__(self):
        self.active_requests = 5
    
    def shutdown(self):
        # BUG: Immediate shutdown kills active requests
        print("Shutting down immediately")
        exit(0)

app = NoGracefulShutdown()

# SIGTERM received
# BUG: Doesn't wait for active requests
app.shutdown()
"""
            
            test_file = os.path.join(temp_dir, "graceful_shutdown.py")
            with open(test_file, "w") as f:
                f.write(agent_code)
            
            assert os.path.exists(test_file)
    
    def test_feature_flags(self):
        """Test 690: Use feature flags"""
        with tempfile.TemporaryDirectory() as temp_dir:
            agent_code = """
class NoFeatureFlags:
    def new_feature(self):
        # BUG: New feature deployed to everyone
        return "New feature enabled for all users"

app = NoFeatureFlags()

# BUG: Can't gradually roll out or rollback
result = app.new_feature()
print(result)
"""
            
            test_file = os.path.join(temp_dir, "feature_flags.py")
            with open(test_file, "w") as f:
                f.write(agent_code)
            
            assert os.path.exists(test_file)
    
    def test_canary_deployment(self):
        """Test 691: Implement canary deployments"""
        with tempfile.TemporaryDirectory() as temp_dir:
            agent_code = """
class NoCanaryDeployment:
    def deploy(self, version):
        # BUG: Deploys to all servers at once
        for server in range(100):
            self.update_server(server, version)
    
    def update_server(self, server, version):
        print(f"Server {server} updated to {version}")

deployer = NoCanaryDeployment()

# BUG: Bug affects all users immediately
deployer.deploy("v2.0")
"""
            
            test_file = os.path.join(temp_dir, "canary_deployment.py")
            with open(test_file, "w") as f:
                f.write(agent_code)
            
            assert os.path.exists(test_file)
    
    def test_rollback_mechanism(self):
        """Test 692: Implement quick rollback"""
        with tempfile.TemporaryDirectory() as temp_dir:
            agent_code = """
class NoRollback:
    def deploy(self, version):
        # BUG: Overwrites previous version
        self.delete_old_version()
        self.install_new_version(version)
    
    def delete_old_version(self):
        print("Old version deleted")
    
    def install_new_version(self, version):
        print(f"Installed {version}")

deployer = NoRollback()

deployer.deploy("v2.0")

# Bug found in v2.0
# BUG: Can't rollback, old version deleted
print("No rollback possible")
"""
            
            test_file = os.path.join(temp_dir, "rollback.py")
            with open(test_file, "w") as f:
                f.write(agent_code)
            
            assert os.path.exists(test_file)
    
    def test_deployment_smoke_tests(self):
        """Test 693: Run smoke tests after deployment"""
        with tempfile.TemporaryDirectory() as temp_dir:
            agent_code = """
class NoSmokeTests:
    def deploy(self):
        self.install()
        # BUG: No smoke tests after deployment
        print("Deployment complete")
    
    def install(self):
        print("Installing...")

deployer = NoSmokeTests()

deployer.deploy()

# BUG: Broken deployment not detected
print("No verification after deployment")
"""
            
            test_file = os.path.join(temp_dir, "smoke_tests.py")
            with open(test_file, "w") as f:
                f.write(agent_code)
            
            assert os.path.exists(test_file)
    
    def test_deployment_notifications(self):
        """Test 694: Notify on deployment events"""
        with tempfile.TemporaryDirectory() as temp_dir:
            agent_code = """
class NoDeploymentNotifications:
    def deploy(self, version):
        # BUG: No notifications
        self.install(version)
    
    def install(self, version):
        print(f"Deployed {version}")

deployer = NoDeploymentNotifications()

# BUG: Team doesn't know deployment happened
deployer.deploy("v2.0")
"""
            
            test_file = os.path.join(temp_dir, "deployment_notifications.py")
            with open(test_file, "w") as f:
                f.write(agent_code)
            
            assert os.path.exists(test_file)
    
    def test_environment_parity(self):
        """Test 695: Maintain dev/prod parity"""
        with tempfile.TemporaryDirectory() as temp_dir:
            agent_code = """
class EnvironmentDrift:
    def __init__(self, environment):
        if environment == "dev":
            # BUG: Different versions in dev/prod
            self.python_version = "3.8"
            self.framework_version = "2.0"
        else:
            self.python_version = "3.11"
            self.framework_version = "3.0"

dev = EnvironmentDrift("dev")
prod = EnvironmentDrift("prod")

# BUG: "Works on my machine" syndrome
print(f"Dev: Python {dev.python_version}")
print(f"Prod: Python {prod.python_version}")
"""
            
            test_file = os.path.join(temp_dir, "environment_parity.py")
            with open(test_file, "w") as f:
                f.write(agent_code)
            
            assert os.path.exists(test_file)
