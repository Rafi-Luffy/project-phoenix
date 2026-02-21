"""
Scalability Features - Module 6.1

Horizontal scaling architecture, auto-scaling policies,
load testing, and resource monitoring for production systems.
"""

import time
import threading
import random
from dataclasses import dataclass, field
from enum import Enum
from typing import Any, Dict, List, Optional, Callable
from collections import defaultdict, deque
import statistics


class ScalingStrategy(Enum):
    """Types of scaling strategies"""
    HORIZONTAL = "horizontal"  # Add more instances
    VERTICAL = "vertical"      # Add more resources per instance
    HYBRID = "hybrid"           # Both horizontal and vertical


class MetricThresholdType(Enum):
    """Types of metric thresholds"""
    CPU_USAGE = "cpu_usage"
    MEMORY_USAGE = "memory_usage"
    NETWORK_LATENCY = "network_latency"
    QUEUE_LENGTH = "queue_length"
    REQUEST_RATE = "request_rate"
    ERROR_RATE = "error_rate"


class InstanceStatus(Enum):
    """Status of instance"""
    STARTING = "starting"
    HEALTHY = "healthy"
    DEGRADED = "degraded"
    UNHEALTHY = "unhealthy"
    TERMINATING = "terminating"
    TERMINATED = "terminated"


@dataclass
class ScalingPolicy:
    """Auto-scaling policy configuration"""
    policy_id: str
    name: str
    scaling_strategy: ScalingStrategy
    scale_up_threshold: Dict[MetricThresholdType, float]
    scale_down_threshold: Dict[MetricThresholdType, float]
    cooldown_period: int = 300  # seconds
    min_instances: int = 2
    max_instances: int = 100
    scale_up_amount: int = 1
    scale_down_amount: int = 1


@dataclass
class Instance:
    """Server instance"""
    instance_id: str
    instance_type: str  # t2.micro, m5.large, etc.
    region: str
    availability_zone: str
    status: InstanceStatus = InstanceStatus.STARTING
    cpu_usage: float = 0.0
    memory_usage: float = 0.0
    network_latency: float = 0.0
    requests_processed: int = 0
    current_connections: int = 0
    created_at: float = field(default_factory=time.time)
    last_heartbeat: float = field(default_factory=time.time)


@dataclass
class LoadTestResult:
    """Result of load test execution"""
    test_id: str
    target_rps: int  # requests per second
    peak_rps: int
    actual_rps: float
    average_latency: float
    p95_latency: float
    p99_latency: float
    error_rate: float
    total_requests: int
    failed_requests: int
    success_rate: float
    duration: float
    throughput_per_instance: float


class HorizontalScalingArchitecture:
    """Manages horizontal scaling (more instances)"""

    def __init__(self):
        self.instances: Dict[str, Instance] = {}
        self.instance_pools: Dict[str, List[str]] = defaultdict(list)  # region -> instances
        self.load_balancer = LoadBalancer()
        self.lock = threading.RLock()

    def launch_instance(self, instance_type: str, region: str,
                       availability_zone: str) -> Optional[Instance]:
        """Launch new instance"""
        with self.lock:
            instance_id = f"i-{int(time.time() * 1000)}{random.randint(1000, 9999)}"

            instance = Instance(
                instance_id=instance_id,
                instance_type=instance_type,
                region=region,
                availability_zone=availability_zone,
                status=InstanceStatus.STARTING
            )

            self.instances[instance_id] = instance
            self.instance_pools[region].append(instance_id)

            # Simulate startup time
            threading.Thread(
                target=self._initialize_instance,
                args=(instance_id,)
            ).start()

            return instance

    def terminate_instance(self, instance_id: str) -> bool:
        """Terminate instance"""
        with self.lock:
            if instance_id not in self.instances:
                return False

            instance = self.instances[instance_id]
            instance.status = InstanceStatus.TERMINATING

            # Simulate graceful shutdown
            threading.Thread(
                target=self._shutdown_instance,
                args=(instance_id,)
            ).start()

            return True

    def get_instance_metrics(self, instance_id: str) -> Optional[Dict[str, Any]]:
        """Get metrics for instance"""
        with self.lock:
            if instance_id not in self.instances:
                return None

            instance = self.instances[instance_id]
            return {
                "instance_id": instance_id,
                "status": instance.status.value,
                "cpu_usage": instance.cpu_usage,
                "memory_usage": instance.memory_usage,
                "network_latency": instance.network_latency,
                "current_connections": instance.current_connections,
                "requests_processed": instance.requests_processed
            }

    def get_healthy_instances(self, region: Optional[str] = None) -> List[str]:
        """Get list of healthy instances"""
        with self.lock:
            healthy = [
                iid for iid, inst in self.instances.items()
                if inst.status == InstanceStatus.HEALTHY
            ]

            if region:
                healthy = [
                    iid for iid in healthy
                    if self.instances[iid].region == region
                ]

            return healthy

    def scale_horizontally(self, num_instances: int, instance_type: str,
                          region: str) -> List[Instance]:
        """Scale up by launching multiple instances"""
        new_instances = []

        for i in range(num_instances):
            az = f"{region}-{chr(97 + (i % 3))}"  # Distribute across AZs
            instance = self.launch_instance(instance_type, region, az)
            if instance:
                new_instances.append(instance)

        return new_instances

    def _initialize_instance(self, instance_id: str):
        """Initialize instance (background task)"""
        time.sleep(random.uniform(2, 5))  # Simulate startup time

        with self.lock:
            if instance_id in self.instances:
                self.instances[instance_id].status = InstanceStatus.HEALTHY
                self.instances[instance_id].last_heartbeat = time.time()

    def _shutdown_instance(self, instance_id: str):
        """Shutdown instance (background task)"""
        time.sleep(random.uniform(5, 10))  # Simulate graceful shutdown

        with self.lock:
            if instance_id in self.instances:
                self.instances[instance_id].status = InstanceStatus.TERMINATED


class AutoScalingPolicies:
    """Manage auto-scaling policies"""

    def __init__(self):
        self.policies: Dict[str, ScalingPolicy] = {}
        self.scaling_history: List[Dict[str, Any]] = []
        self.last_scaling_time: float = 0
        self.lock = threading.RLock()

    def create_policy(self, policy: ScalingPolicy) -> bool:
        """Create scaling policy"""
        with self.lock:
            if policy.policy_id in self.policies:
                return False

            self.policies[policy.policy_id] = policy
            return True

    def evaluate_scaling_needs(self, current_metrics: Dict[str, float],
                              policy_id: str,
                              current_instance_count: int) -> Optional[Dict[str, Any]]:
        """Evaluate if scaling is needed"""
        with self.lock:
            if policy_id not in self.policies:
                return None

            policy = self.policies[policy_id]

            # Check if cooldown period is active
            time_since_last_scaling = time.time() - self.last_scaling_time
            if time_since_last_scaling < policy.cooldown_period:
                return None

            # Check scale-up conditions
            for metric_type, threshold in policy.scale_up_threshold.items():
                if current_metrics.get(metric_type.value, 0) > threshold:
                    new_count = min(
                        current_instance_count + policy.scale_up_amount,
                        policy.max_instances
                    )

                    if new_count > current_instance_count:
                        self.last_scaling_time = time.time()
                        return {
                            "action": "scale_up",
                            "reason": f"{metric_type.value} exceeded threshold",
                            "new_instance_count": new_count,
                            "instances_to_add": new_count - current_instance_count
                        }

            # Check scale-down conditions
            for metric_type, threshold in policy.scale_down_threshold.items():
                if current_metrics.get(metric_type.value, 0) < threshold:
                    new_count = max(
                        current_instance_count - policy.scale_down_amount,
                        policy.min_instances
                    )

                    if new_count < current_instance_count:
                        self.last_scaling_time = time.time()
                        return {
                            "action": "scale_down",
                            "reason": f"{metric_type.value} below threshold",
                            "new_instance_count": new_count,
                            "instances_to_remove": current_instance_count - new_count
                        }

            return None

    def record_scaling_action(self, action: Dict[str, Any]):
        """Record scaling action"""
        with self.lock:
            self.scaling_history.append({
                "timestamp": time.time(),
                **action
            })

    def get_scaling_history(self, limit: int = 100) -> List[Dict[str, Any]]:
        """Get scaling history"""
        with self.lock:
            return self.scaling_history[-limit:]


class LoadBalancer:
    """Load balancing across instances"""

    def __init__(self):
        self.request_history: Dict[str, deque] = defaultdict(lambda: deque(maxlen=1000))
        self.lock = threading.RLock()

    def select_instance(self, available_instances: List[Instance],
                       strategy: str = "least_connections") -> Optional[str]:
        """Select instance using specified strategy"""
        with self.lock:
            if not available_instances:
                return None

            if strategy == "round_robin":
                return self._round_robin(available_instances)
            elif strategy == "least_connections":
                return self._least_connections(available_instances)
            elif strategy == "weighted_response_time":
                return self._weighted_response_time(available_instances)
            else:
                return available_instances[0].instance_id

    def _round_robin(self, instances: List[Instance]) -> str:
        """Select instance using round-robin"""
        return instances[int(time.time() * 1000) % len(instances)].instance_id

    def _least_connections(self, instances: List[Instance]) -> str:
        """Select instance with least connections"""
        return min(instances, key=lambda i: i.current_connections).instance_id

    def _weighted_response_time(self, instances: List[Instance]) -> str:
        """Select instance based on weighted response time"""
        # Lower latency gets more weight
        weights = [1.0 / (max(i.network_latency, 0.1)) for i in instances]
        total_weight = sum(weights)
        normalized_weights = [w / total_weight for w in weights]

        random_value = random.random()
        cumulative = 0
        for instance, weight in zip(instances, normalized_weights):
            cumulative += weight
            if random_value <= cumulative:
                return instance.instance_id

        return instances[-1].instance_id

    def record_request(self, instance_id: str, latency: float):
        """Record request for metrics"""
        with self.lock:
            self.request_history[instance_id].append({
                "timestamp": time.time(),
                "latency": latency
            })


class ResourceMonitoring:
    """Monitor resource usage"""

    def __init__(self):
        self.instance_metrics: Dict[str, deque] = defaultdict(
            lambda: deque(maxlen=10000)
        )
        self.alerts: List[Dict[str, Any]] = []
        self.alert_thresholds: Dict[str, float] = {
            "cpu_usage": 80.0,
            "memory_usage": 85.0,
            "error_rate": 5.0
        }
        self.lock = threading.RLock()

    def update_instance_metrics(self, instance_id: str,
                               metrics: Dict[str, float]):
        """Update metrics for instance"""
        with self.lock:
            metrics_with_timestamp = {
                **metrics,
                "timestamp": time.time()
            }
            self.instance_metrics[instance_id].append(metrics_with_timestamp)

            # Check thresholds and generate alerts
            for metric_name, threshold in self.alert_thresholds.items():
                if metrics.get(metric_name, 0) > threshold:
                    self.generate_alert(
                        instance_id,
                        metric_name,
                        metrics[metric_name],
                        threshold
                    )

    def generate_alert(self, instance_id: str, metric_name: str,
                      current_value: float, threshold: float):
        """Generate alert for metric threshold"""
        with self.lock:
            self.alerts.append({
                "instance_id": instance_id,
                "metric": metric_name,
                "current_value": current_value,
                "threshold": threshold,
                "timestamp": time.time(),
                "severity": "high" if current_value > threshold * 1.1 else "medium"
            })

    def get_instance_metrics_summary(self, instance_id: str,
                                     time_window: int = 300) -> Dict[str, Any]:
        """Get metrics summary for instance"""
        with self.lock:
            if instance_id not in self.instance_metrics:
                return {}

            current_time = time.time()
            recent_metrics = [
                m for m in self.instance_metrics[instance_id]
                if current_time - m["timestamp"] <= time_window
            ]

            if not recent_metrics:
                return {}

            # Calculate statistics
            cpu_values = [m.get("cpu_usage", 0) for m in recent_metrics]
            memory_values = [m.get("memory_usage", 0) for m in recent_metrics]

            return {
                "instance_id": instance_id,
                "measurement_count": len(recent_metrics),
                "cpu_usage_mean": statistics.mean(cpu_values),
                "cpu_usage_max": max(cpu_values),
                "memory_usage_mean": statistics.mean(memory_values),
                "memory_usage_max": max(memory_values)
            }

    def get_cluster_health(self) -> Dict[str, Any]:
        """Get overall cluster health"""
        with self.lock:
            all_metrics = []
            for instance_id, metrics_deque in self.instance_metrics.items():
                if metrics_deque:
                    all_metrics.extend(metrics_deque)

            if not all_metrics:
                return {}

            cpu_values = [m.get("cpu_usage", 0) for m in all_metrics]
            error_rates = [m.get("error_rate", 0) for m in all_metrics]

            return {
                "total_instances": len(self.instance_metrics),
                "avg_cpu_usage": statistics.mean(cpu_values),
                "max_cpu_usage": max(cpu_values),
                "avg_error_rate": statistics.mean(error_rates),
                "active_alerts": len([a for a in self.alerts
                                     if time.time() - a["timestamp"] < 3600]),
                "health_status": "healthy" if statistics.mean(error_rates) < 1.0 else "degraded"
            }


class LoadTestingFramework:
    """Framework for load testing"""

    def __init__(self):
        self.test_results: List[LoadTestResult] = []

    def run_load_test(self, target_function: Callable,
                     target_rps: int,
                     duration_seconds: int,
                     payload_generator: Callable) -> LoadTestResult:
        """Run load test"""
        test_id = f"load_test_{int(time.time() * 1000)}"
        start_time = time.time()
        request_times = []
        errors = 0
        requests_sent = 0

        requests_per_second = target_rps
        time_per_request = 1.0 / requests_per_second if requests_per_second > 0 else 0.1

        elapsed = 0
        while elapsed < duration_seconds:
            batch_start = time.time()
            request_start = time.time()

            try:
                payload = payload_generator()
                target_function(payload)
                latency = time.time() - request_start
                request_times.append(latency)
                requests_sent += 1

            except Exception:
                errors += 1
                requests_sent += 1

            elapsed = time.time() - start_time
            sleep_time = max(0, time_per_request - (time.time() - batch_start))
            if sleep_time > 0:
                time.sleep(sleep_time)

        # Calculate statistics
        total_duration = time.time() - start_time
        actual_rps = requests_sent / total_duration

        if request_times:
            avg_latency = statistics.mean(request_times)
            sorted_times = sorted(request_times)
            p95_idx = int(len(sorted_times) * 0.95)
            p99_idx = int(len(sorted_times) * 0.99)
            p95_latency = sorted_times[min(p95_idx, len(sorted_times) - 1)]
            p99_latency = sorted_times[min(p99_idx, len(sorted_times) - 1)]
        else:
            avg_latency = 0
            p95_latency = 0
            p99_latency = 0

        error_rate = errors / requests_sent if requests_sent > 0 else 0
        success_rate = 1 - error_rate

        result = LoadTestResult(
            test_id=test_id,
            target_rps=target_rps,
            peak_rps=requests_sent,
            actual_rps=actual_rps,
            average_latency=avg_latency,
            p95_latency=p95_latency,
            p99_latency=p99_latency,
            error_rate=error_rate,
            total_requests=requests_sent,
            failed_requests=errors,
            success_rate=success_rate,
            duration=total_duration,
            throughput_per_instance=actual_rps
        )

        self.test_results.append(result)
        return result

    def get_load_test_report(self, test_id: Optional[str] = None) -> Dict[str, Any]:
        """Get load test report"""
        if test_id:
            for result in self.test_results:
                if result.test_id == test_id:
                    return {
                        "test_id": result.test_id,
                        "target_rps": result.target_rps,
                        "actual_rps": result.actual_rps,
                        "avg_latency": result.average_latency,
                        "p95_latency": result.p95_latency,
                        "p99_latency": result.p99_latency,
                        "success_rate": result.success_rate,
                        "total_requests": result.total_requests
                    }
        else:
            return {
                "total_tests": len(self.test_results),
                "avg_success_rate": statistics.mean([r.success_rate for r in self.test_results])
                if self.test_results else 0,
                "max_rps_achieved": max([r.actual_rps for r in self.test_results])
                if self.test_results else 0
            }
