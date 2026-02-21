"""
Maintenance & Updates - Module 6.3

Model versioning, blue-green deployments, rollback procedures,
configuration management, and update strategies.
"""

import time
import threading
import json
from dataclasses import dataclass, field
from enum import Enum
from typing import Any, Dict, List, Optional, Callable
from collections import deque
import hashlib


class DeploymentStrategy(Enum):
    """Deployment strategies"""
    BLUE_GREEN = "blue_green"
    CANARY = "canary"
    ROLLING = "rolling"
    SHADOW = "shadow"


class DeploymentStatus(Enum):
    """Status of deployment"""
    PENDING = "pending"
    IN_PROGRESS = "in_progress"
    COMPLETED = "completed"
    FAILED = "failed"
    ROLLED_BACK = "rolled_back"


class ConfigurationSource(Enum):
    """Source of configuration"""
    ENV_VARS = "env_vars"
    CONFIG_FILE = "config_file"
    DATABASE = "database"
    VAULT = "vault"
    GIT = "git"


class VersionType(Enum):
    """Types of versions"""
    PATCH = "patch"       # 1.0.0 -> 1.0.1
    MINOR = "minor"       # 1.0.0 -> 1.1.0
    MAJOR = "major"       # 1.0.0 -> 2.0.0


@dataclass
class ModelVersion:
    """Version of deployed model/service"""
    version_id: str
    version_number: str
    created_at: float = field(default_factory=time.time)
    deployed_at: Optional[float] = None
    model_hash: str = ""
    config_hash: str = ""
    performance_metrics: Dict[str, float] = field(default_factory=dict)
    is_current: bool = False
    rollback_available: bool = True
    changelog: str = ""
    dependencies: List[str] = field(default_factory=list)


@dataclass
class Deployment:
    """Deployment execution"""
    deployment_id: str
    version_id: str
    strategy: DeploymentStrategy
    status: DeploymentStatus
    started_at: float = field(default_factory=time.time)
    completed_at: Optional[float] = None
    duration: float = 0.0
    from_version: Optional[str] = None
    to_version: str = ""
    rollout_percentage: float = 0.0
    instances_updated: int = 0
    total_instances: int = 0
    errors: List[str] = field(default_factory=list)


@dataclass
class ConfigurationSnapshot:
    """Snapshot of configuration at point in time"""
    snapshot_id: str
    timestamp: float
    config_data: Dict[str, Any]
    source: ConfigurationSource
    version_tag: Optional[str] = None
    validated: bool = False
    hash: str = ""


class ModelVersioningSystem:
    """Manage model/service versions"""

    def __init__(self):
        self.versions: Dict[str, ModelVersion] = {}
        self.current_version: Optional[str] = None
        self.version_history: deque = deque(maxlen=100)
        self.lock = threading.RLock()

    def create_version(self, version_number: str,
                      model_hash: str,
                      config_hash: str,
                      changelog: str) -> str:
        """Create new version"""
        with self.lock:
            version_id = f"v_{int(time.time() * 1000)}"

            version = ModelVersion(
                version_id=version_id,
                version_number=version_number,
                model_hash=model_hash,
                config_hash=config_hash,
                changelog=changelog
            )

            self.versions[version_id] = version
            self.version_history.append({
                "version_id": version_id,
                "version_number": version_number,
                "created_at": version.created_at
            })

            return version_id

    def mark_version_deployed(self, version_id: str,
                             performance_metrics: Dict[str, float]) -> bool:
        """Mark version as deployed"""
        with self.lock:
            if version_id not in self.versions:
                return False

            version = self.versions[version_id]
            version.deployed_at = time.time()
            version.performance_metrics = performance_metrics

            # Set as current
            if self.current_version:
                self.versions[self.current_version].is_current = False

            version.is_current = True
            self.current_version = version_id

            return True

    def get_version(self, version_id: str) -> Optional[ModelVersion]:
        """Get version details"""
        with self.lock:
            return self.versions.get(version_id)

    def get_current_version(self) -> Optional[ModelVersion]:
        """Get current deployed version"""
        with self.lock:
            if self.current_version:
                return self.versions.get(self.current_version)
            return None

    def get_version_history(self, limit: int = 20) -> List[Dict[str, Any]]:
        """Get version history"""
        with self.lock:
            history = list(self.version_history)[-limit:]
            return [
                {
                    "version_id": h["version_id"],
                    "version_number": h["version_number"],
                    "created_at": h["created_at"],
                    "is_current": h["version_id"] == self.current_version
                }
                for h in history
            ]

    def list_available_versions(self) -> List[Dict[str, Any]]:
        """List all available versions"""
        with self.lock:
            versions = []
            for version_id, version in self.versions.items():
                versions.append({
                    "version_id": version_id,
                    "version_number": version.version_number,
                    "created_at": version.created_at,
                    "deployed_at": version.deployed_at,
                    "is_current": version.is_current,
                    "rollback_available": version.rollback_available
                })

            return sorted(versions, key=lambda v: v["created_at"], reverse=True)


class BlueGreenDeployment:
    """Blue-green deployment strategy"""

    def __init__(self):
        self.blue_environment: Dict[str, Any] = {}
        self.green_environment: Dict[str, Any] = {}
        self.active_environment: str = "blue"
        self.deployment_history: deque = deque(maxlen=50)
        self.lock = threading.RLock()

    def deploy_to_inactive_environment(self, version_id: str,
                                       deployment_fn: Callable) -> bool:
        """Deploy to inactive (standby) environment"""
        with self.lock:
            target_env = "green" if self.active_environment == "blue" else "blue"

            deployment = Deployment(
                deployment_id=f"deploy_{int(time.time() * 1000)}",
                version_id=version_id,
                strategy=DeploymentStrategy.BLUE_GREEN,
                status=DeploymentStatus.IN_PROGRESS,
                to_version=version_id
            )

            try:
                deployment_fn(version_id)

                # Update environment
                target_dict = (self.green_environment
                              if target_env == "green"
                              else self.blue_environment)
                target_dict["version"] = version_id
                target_dict["deployed_at"] = time.time()

                deployment.status = DeploymentStatus.COMPLETED
                deployment.completed_at = time.time()
                deployment.duration = deployment.completed_at - deployment.started_at

                self.deployment_history.append(deployment)
                return True

            except Exception as e:
                deployment.status = DeploymentStatus.FAILED
                deployment.errors.append(str(e))
                self.deployment_history.append(deployment)
                return False

    def switch_environment(self) -> bool:
        """Switch from blue to green or vice versa"""
        with self.lock:
            self.active_environment = (
                "green" if self.active_environment == "blue" else "blue"
            )
            return True

    def get_active_environment(self) -> Dict[str, Any]:
        """Get active environment"""
        with self.lock:
            if self.active_environment == "blue":
                return {"environment": "blue", **self.blue_environment}
            else:
                return {"environment": "green", **self.green_environment}

    def get_deployment_status(self) -> Dict[str, Any]:
        """Get deployment status"""
        with self.lock:
            active = self.get_active_environment()
            standby_env = (
                "green" if self.active_environment == "blue" else "blue"
            )
            standby_dict = (
                self.green_environment if standby_env == "green" else self.blue_environment
            )

            return {
                "active_environment": self.active_environment,
                "active_version": active.get("version"),
                "standby_environment": standby_env,
                "standby_version": standby_dict.get("version"),
                "total_deployments": len(self.deployment_history)
            }


class CanaryDeployment:
    """Canary deployment strategy"""

    def __init__(self):
        self.canary_version: Optional[str] = None
        self.canary_traffic_percentage: float = 0.0
        self.canary_metrics: Dict[str, float] = {}
        self.deployment_history: deque = deque(maxlen=50)
        self.lock = threading.RLock()

    def start_canary_deployment(self, version_id: str,
                               initial_traffic: float = 0.05) -> bool:
        """Start canary deployment with small traffic percentage"""
        with self.lock:
            self.canary_version = version_id
            self.canary_traffic_percentage = initial_traffic

            deployment = Deployment(
                deployment_id=f"canary_{int(time.time() * 1000)}",
                version_id=version_id,
                strategy=DeploymentStrategy.CANARY,
                status=DeploymentStatus.IN_PROGRESS,
                rollout_percentage=initial_traffic * 100
            )

            self.deployment_history.append(deployment)
            return True

    def increase_canary_traffic(self, percentage: float) -> bool:
        """Increase traffic to canary"""
        with self.lock:
            if self.canary_version:
                self.canary_traffic_percentage = min(percentage, 1.0)
                return True
            return False

    def abort_canary(self, reason: str) -> bool:
        """Abort canary deployment"""
        with self.lock:
            if self.canary_version:
                # Create abort entry
                self.canary_version = None
                self.canary_traffic_percentage = 0.0
                return True
            return False

    def promote_canary_to_production(self) -> bool:
        """Promote canary to full production"""
        with self.lock:
            if self.canary_version:
                canary_version = self.canary_version
                self.canary_version = None
                self.canary_traffic_percentage = 0.0
                return True
            return False

    def get_canary_status(self) -> Dict[str, Any]:
        """Get canary status"""
        with self.lock:
            return {
                "active": self.canary_version is not None,
                "canary_version": self.canary_version,
                "traffic_percentage": self.canary_traffic_percentage * 100,
                "metrics": self.canary_metrics
            }


class RollbackProcedures:
    """Manage rollback procedures"""

    def __init__(self):
        self.rollback_history: deque = deque(maxlen=100)
        self.rollback_in_progress: bool = False
        self.lock = threading.RLock()

    def initiate_rollback(self, from_version: str,
                         to_version: str,
                         reason: str,
                         rollback_fn: Callable) -> bool:
        """Initiate rollback to previous version"""
        with self.lock:
            if self.rollback_in_progress:
                return False

            self.rollback_in_progress = True

            rollback_record = {
                "rollback_id": f"rollback_{int(time.time() * 1000)}",
                "from_version": from_version,
                "to_version": to_version,
                "reason": reason,
                "initiated_at": time.time(),
                "completed_at": None,
                "status": "in_progress",
                "errors": []
            }

            try:
                rollback_fn(to_version)
                rollback_record["status"] = "completed"
                rollback_record["completed_at"] = time.time()

            except Exception as e:
                rollback_record["status"] = "failed"
                rollback_record["errors"].append(str(e))
                self.rollback_in_progress = False
                return False

            self.rollback_history.append(rollback_record)
            self.rollback_in_progress = False
            return True

    def get_rollback_history(self, limit: int = 20) -> List[Dict[str, Any]]:
        """Get rollback history"""
        with self.lock:
            return list(self.rollback_history)[-limit:]

    def can_rollback_to_version(self, version_id: str) -> bool:
        """Check if rollback is possible to version"""
        with self.lock:
            # For now, always allow rollback (in production, check if version is retained)
            return True

    def get_rollback_status(self) -> Dict[str, Any]:
        """Get rollback status"""
        with self.lock:
            return {
                "rollback_in_progress": self.rollback_in_progress,
                "total_rollbacks": len(self.rollback_history),
                "last_rollback": (
                    self.rollback_history[-1] if self.rollback_history else None
                )
            }


class ConfigurationManagement:
    """Manage configurations"""

    def __init__(self):
        self.configurations: Dict[str, ConfigurationSnapshot] = {}
        self.active_config_id: Optional[str] = None
        self.config_history: deque = deque(maxlen=100)
        self.validators: Dict[str, Callable] = {}
        self.lock = threading.RLock()

    def save_configuration(self, config_data: Dict[str, Any],
                          source: ConfigurationSource,
                          version_tag: Optional[str] = None) -> str:
        """Save configuration snapshot"""
        with self.lock:
            config_id = f"cfg_{int(time.time() * 1000)}"
            config_hash = self._calculate_hash(json.dumps(config_data, sort_keys=True))

            snapshot = ConfigurationSnapshot(
                snapshot_id=config_id,
                timestamp=time.time(),
                config_data=config_data,
                source=source,
                version_tag=version_tag,
                hash=config_hash
            )

            # Validate configuration
            if self._validate_configuration(config_data):
                snapshot.validated = True

            self.configurations[config_id] = snapshot
            self.config_history.append(config_id)

            if self.active_config_id is None:
                self.active_config_id = config_id

            return config_id

    def get_configuration(self, config_id: str) -> Optional[ConfigurationSnapshot]:
        """Get configuration snapshot"""
        with self.lock:
            return self.configurations.get(config_id)

    def get_active_configuration(self) -> Optional[Dict[str, Any]]:
        """Get currently active configuration"""
        with self.lock:
            if self.active_config_id:
                config = self.configurations.get(self.active_config_id)
                return config.config_data if config else None
            return None

    def switch_configuration(self, config_id: str) -> bool:
        """Switch to different configuration"""
        with self.lock:
            if config_id in self.configurations:
                config = self.configurations[config_id]

                if not config.validated:
                    return False

                self.active_config_id = config_id
                return True

            return False

    def rollback_configuration(self) -> bool:
        """Rollback to previous configuration"""
        with self.lock:
            if len(self.config_history) > 1:
                self.config_history.pop()  # Remove current
                previous_config_id = self.config_history[-1]
                self.active_config_id = previous_config_id
                return True

            return False

    def register_validator(self, validator_name: str,
                          validator_fn: Callable) -> bool:
        """Register configuration validator"""
        with self.lock:
            self.validators[validator_name] = validator_fn
            return True

    def _validate_configuration(self, config: Dict[str, Any]) -> bool:
        """Validate configuration using registered validators"""
        with self.lock:
            for validator_name, validator_fn in self.validators.items():
                try:
                    if not validator_fn(config):
                        return False
                except Exception:
                    return False

            return True

    @staticmethod
    def _calculate_hash(data: str) -> str:
        """Calculate hash of data"""
        return hashlib.sha256(data.encode()).hexdigest()

    def get_configuration_history(self, limit: int = 20) -> List[Dict[str, Any]]:
        """Get configuration history"""
        with self.lock:
            history = list(self.config_history)[-limit:]
            return [
                {
                    "config_id": cfg_id,
                    "timestamp": self.configurations[cfg_id].timestamp,
                    "source": self.configurations[cfg_id].source.value,
                    "validated": self.configurations[cfg_id].validated,
                    "is_active": cfg_id == self.active_config_id
                }
                for cfg_id in history
                if cfg_id in self.configurations
            ]

    def validate_configuration_change(self, new_config: Dict[str, Any]) -> bool:
        """Validate new configuration"""
        return self._validate_configuration(new_config)
