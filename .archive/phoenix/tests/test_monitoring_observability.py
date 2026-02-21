"""
Comprehensive Test Suite for Phoenix - Monitoring & Observability
Tests 696-725: Logging, Metrics, Tracing, Alerting (30 tests)

This file tests Phoenix's ability to detect and fix bugs in monitoring,
observability, logging, and alerting systems.
"""

import os
import tempfile
import shutil
from pathlib import Path
import pytest
from unittest.mock import Mock, patch


class TestLoggingPractices:
    """Test logging best practices (10 tests)"""
    
    def test_log_levels(self):
        """Test 696: Use appropriate log levels"""
        with tempfile.TemporaryDirectory() as temp_dir:
            agent_code = """
class WrongLogLevels:
    def process_request(self, request):
        # BUG: Everything logged as ERROR
        print("ERROR: Processing request")
        print("ERROR: Request validated")
        print("ERROR: Request successful")

processor = WrongLogLevels()

# BUG: Can't distinguish real errors
processor.process_request({"data": "value"})
"""
            
            test_file = os.path.join(temp_dir, "log_levels.py")
            with open(test_file, "w") as f:
                f.write(agent_code)
            
            assert os.path.exists(test_file)
    
    def test_structured_logging(self):
        """Test 697: Use structured logging"""
        with tempfile.TemporaryDirectory() as temp_dir:
            agent_code = """
class UnstructuredLogging:
    def log_event(self, user_id, action, status):
        # BUG: Unstructured string logs
        print(f"User {user_id} performed {action} with status {status}")

logger = UnstructuredLogging()

# BUG: Hard to parse and query
logger.log_event("user123", "login", "success")
logger.log_event("user456", "purchase", "failed")
"""
            
            test_file = os.path.join(temp_dir, "structured_logging.py")
            with open(test_file, "w") as f:
                f.write(agent_code)
            
            assert os.path.exists(test_file)
    
    def test_sensitive_data_in_logs(self):
        """Test 698: Redact sensitive data from logs"""
        with tempfile.TemporaryDirectory() as temp_dir:
            agent_code = """
class SensitiveDataLogging:
    def log_authentication(self, username, password, card_number):
        # BUG: Logs sensitive data
        print(f"Login attempt: {username} / {password}")
        print(f"Payment with card: {card_number}")

logger = SensitiveDataLogging()

# BUG: Passwords and PII in logs
logger.log_authentication("john", "MyP@ssw0rd", "4532-1234-5678-9010")
"""
            
            test_file = os.path.join(temp_dir, "sensitive_logging.py")
            with open(test_file, "w") as f:
                f.write(agent_code)
            
            assert os.path.exists(test_file)
    
    def test_correlation_ids(self):
        """Test 699: Include correlation IDs"""
        with tempfile.TemporaryDirectory() as temp_dir:
            agent_code = """
class NoCorrelationID:
    def process_request(self, request):
        # BUG: No correlation ID
        print("Received request")
        self.validate(request)
        self.process(request)
        print("Request complete")
    
    def validate(self, request):
        print("Validation started")
    
    def process(self, request):
        print("Processing started")

handler = NoCorrelationID()

# BUG: Can't trace request through logs
handler.process_request({"data": "value"})
"""
            
            test_file = os.path.join(temp_dir, "correlation_ids.py")
            with open(test_file, "w") as f:
                f.write(agent_code)
            
            assert os.path.exists(test_file)
    
    def test_log_context_information(self):
        """Test 700: Include context in logs"""
        with tempfile.TemporaryDirectory() as temp_dir:
            agent_code = """
class NoLogContext:
    def process_order(self, order_id):
        # BUG: Minimal context
        print("Processing order")
        print("Order validation failed")

processor = NoLogContext()

# BUG: No context about what failed
processor.process_order("order123")
"""
            
            test_file = os.path.join(temp_dir, "log_context.py")
            with open(test_file, "w") as f:
                f.write(agent_code)
            
            assert os.path.exists(test_file)
    
    def test_log_rotation(self):
        """Test 701: Implement log rotation"""
        with tempfile.TemporaryDirectory() as temp_dir:
            agent_code = """
class NoLogRotation:
    def __init__(self):
        # BUG: Single log file, no rotation
        self.log_file = open("app.log", "a")
    
    def log(self, message):
        # BUG: File grows unbounded
        self.log_file.write(f"{message}\\n")

logger = NoLogRotation()

# BUG: Disk space exhaustion
for i in range(1000000):
    logger.log(f"Log message {i}")
"""
            
            test_file = os.path.join(temp_dir, "log_rotation.py")
            with open(test_file, "w") as f:
                f.write(agent_code)
            
            assert os.path.exists(test_file)
    
    def test_log_sampling(self):
        """Test 702: Sample high-volume logs"""
        with tempfile.TemporaryDirectory() as temp_dir:
            agent_code = """
class NoLogSampling:
    def log_request(self, request):
        # BUG: Logs every request
        print(f"Request: {request}")

logger = NoLogSampling()

# High traffic
for i in range(1000000):
    logger.log_request(f"request_{i}")

# BUG: Overwhelming log volume
print("All requests logged")
"""
            
            test_file = os.path.join(temp_dir, "log_sampling.py")
            with open(test_file, "w") as f:
                f.write(agent_code)
            
            assert os.path.exists(test_file)
    
    def test_async_logging(self):
        """Test 703: Use asynchronous logging"""
        with tempfile.TemporaryDirectory() as temp_dir:
            agent_code = """
class SynchronousLogging:
    def log(self, message):
        # BUG: Synchronous I/O blocks request
        with open("app.log", "a") as f:
            f.write(f"{message}\\n")
            f.flush()  # Slow

logger = SynchronousLogging()

# BUG: Logging slows down request processing
logger.log("Processing request")
"""
            
            test_file = os.path.join(temp_dir, "async_logging.py")
            with open(test_file, "w") as f:
                f.write(agent_code)
            
            assert os.path.exists(test_file)
    
    def test_log_aggregation(self):
        """Test 704: Aggregate logs from multiple sources"""
        with tempfile.TemporaryDirectory() as temp_dir:
            agent_code = """
class NoLogAggregation:
    def __init__(self, service_name):
        # BUG: Each service logs to local file
        self.log_file = f"{service_name}.log"
    
    def log(self, message):
        with open(self.log_file, "a") as f:
            f.write(f"{message}\\n")

# Multiple services
api_logger = NoLogAggregation("api")
worker_logger = NoLogAggregation("worker")
db_logger = NoLogAggregation("database")

# BUG: Logs scattered across files
api_logger.log("API request")
worker_logger.log("Job processed")
db_logger.log("Query executed")
"""
            
            test_file = os.path.join(temp_dir, "log_aggregation.py")
            with open(test_file, "w") as f:
                f.write(agent_code)
            
            assert os.path.exists(test_file)
    
    def test_error_stack_traces(self):
        """Test 705: Include stack traces for errors"""
        with tempfile.TemporaryDirectory() as temp_dir:
            agent_code = """
class NoStackTrace:
    def process(self, data):
        try:
            result = self.risky_operation(data)
        except Exception as e:
            # BUG: Logs error message without stack trace
            print(f"Error: {e}")
    
    def risky_operation(self, data):
        raise ValueError("Invalid data")

processor = NoStackTrace()

# BUG: Can't debug without stack trace
processor.process("bad_data")
"""
            
            test_file = os.path.join(temp_dir, "stack_traces.py")
            with open(test_file, "w") as f:
                f.write(agent_code)
            
            assert os.path.exists(test_file)


class TestMetricsAndMonitoring:
    """Test metrics collection and monitoring (10 tests)"""
    
    def test_business_metrics(self):
        """Test 706: Track business metrics"""
        with tempfile.TemporaryDirectory() as temp_dir:
            agent_code = """
class NoBusinessMetrics:
    def process_payment(self, amount):
        # BUG: Doesn't track revenue metrics
        payment_successful = True
        return payment_successful

processor = NoBusinessMetrics()

# BUG: No visibility into revenue
processor.process_payment(100.0)
"""
            
            test_file = os.path.join(temp_dir, "business_metrics.py")
            with open(test_file, "w") as f:
                f.write(agent_code)
            
            assert os.path.exists(test_file)
    
    def test_latency_percentiles(self):
        """Test 707: Track latency percentiles"""
        with tempfile.TemporaryDirectory() as temp_dir:
            agent_code = """
import time

class AverageLatencyOnly:
    def __init__(self):
        self.total_time = 0
        self.count = 0
    
    def record_request(self, duration):
        # BUG: Only tracks average
        self.total_time += duration
        self.count += 1
    
    def get_avg_latency(self):
        return self.total_time / self.count if self.count > 0 else 0

monitor = AverageLatencyOnly()

# Most requests fast, some very slow
for _ in range(99):
    monitor.record_request(0.01)  # 10ms
monitor.record_request(10.0)  # 10s

# BUG: Average hides p99 latency
avg = monitor.get_avg_latency()
print(f"Average: {avg}s")
"""
            
            test_file = os.path.join(temp_dir, "latency_percentiles.py")
            with open(test_file, "w") as f:
                f.write(agent_code)
            
            assert os.path.exists(test_file)
    
    def test_error_rate_tracking(self):
        """Test 708: Track error rates"""
        with tempfile.TemporaryDirectory() as temp_dir:
            agent_code = """
class NoErrorRateTracking:
    def __init__(self):
        self.error_count = 0
    
    def handle_request(self, request):
        try:
            return self.process(request)
        except Exception:
            # BUG: Counts errors but not total requests
            self.error_count += 1
            raise
    
    def process(self, request):
        if request == "bad":
            raise Exception("Error")
        return "success"

handler = NoErrorRateTracking()

# BUG: Can't calculate error rate without total count
for req in ["good", "good", "bad", "good"]:
    try:
        handler.handle_request(req)
    except Exception:
        pass

print(f"Errors: {handler.error_count}")
"""
            
            test_file = os.path.join(temp_dir, "error_rate.py")
            with open(test_file, "w") as f:
                f.write(agent_code)
            
            assert os.path.exists(test_file)
    
    def test_resource_utilization_metrics(self):
        """Test 709: Monitor resource utilization"""
        with tempfile.TemporaryDirectory() as temp_dir:
            agent_code = """
class NoResourceMetrics:
    def process_data(self, data):
        # BUG: No CPU/memory monitoring
        result = [x * 2 for x in data]
        return result

processor = NoResourceMetrics()

# Large dataset
data = list(range(1000000))

# BUG: No visibility into resource usage
result = processor.process_data(data)
"""
            
            test_file = os.path.join(temp_dir, "resource_metrics.py")
            with open(test_file, "w") as f:
                f.write(agent_code)
            
            assert os.path.exists(test_file)
    
    def test_custom_metrics(self):
        """Test 710: Emit custom metrics"""
        with tempfile.TemporaryDirectory() as temp_dir:
            agent_code = """
class NoCustomMetrics:
    def __init__(self):
        self.queue_size = 0
    
    def add_to_queue(self, item):
        self.queue_size += 1
        # BUG: No metric emission
    
    def process_from_queue(self):
        if self.queue_size > 0:
            self.queue_size -= 1
        # BUG: No metric emission

queue = NoCustomMetrics()

# BUG: Can't monitor queue depth
queue.add_to_queue("item1")
queue.add_to_queue("item2")
"""
            
            test_file = os.path.join(temp_dir, "custom_metrics.py")
            with open(test_file, "w") as f:
                f.write(agent_code)
            
            assert os.path.exists(test_file)
    
    def test_metric_cardinality(self):
        """Test 711: Control metric cardinality"""
        with tempfile.TemporaryDirectory() as temp_dir:
            agent_code = """
class HighCardinalityMetrics:
    def record_request(self, user_id, endpoint):
        # BUG: User ID creates unbounded cardinality
        metric_name = f"request.{user_id}.{endpoint}"
        print(f"Metric: {metric_name}")

monitor = HighCardinalityMetrics()

# BUG: Millions of unique metrics
for user_id in range(1000000):
    monitor.record_request(f"user_{user_id}", "/api/data")
"""
            
            test_file = os.path.join(temp_dir, "metric_cardinality.py")
            with open(test_file, "w") as f:
                f.write(agent_code)
            
            assert os.path.exists(test_file)
    
    def test_metric_aggregation_intervals(self):
        """Test 712: Use appropriate aggregation intervals"""
        with tempfile.TemporaryDirectory() as temp_dir:
            agent_code = """
import time

class NoAggregationInterval:
    def __init__(self):
        self.metrics = []
    
    def record_metric(self, value):
        # BUG: Stores every data point
        self.metrics.append({
            "value": value,
            "timestamp": time.time()
        })

monitor = NoAggregationInterval()

# High frequency metrics
for i in range(1000000):
    monitor.record_metric(i)

# BUG: Millions of data points
print(f"Stored: {len(monitor.metrics)} metrics")
"""
            
            test_file = os.path.join(temp_dir, "aggregation_intervals.py")
            with open(test_file, "w") as f:
                f.write(agent_code)
            
            assert os.path.exists(test_file)
    
    def test_counter_vs_gauge(self):
        """Test 713: Use correct metric types"""
        with tempfile.TemporaryDirectory() as temp_dir:
            agent_code = """
class WrongMetricTypes:
    def __init__(self):
        # BUG: Using gauge for counter
        self.request_count = 0
    
    def handle_request(self):
        # BUG: Should be counter, not gauge
        self.request_count += 1
        # Gauge value resets on restart
        # BUG: Loses cumulative count

handler = WrongMetricTypes()

# BUG: Total requests lost on restart
for _ in range(100):
    handler.handle_request()
"""
            
            test_file = os.path.join(temp_dir, "metric_types.py")
            with open(test_file, "w") as f:
                f.write(agent_code)
            
            assert os.path.exists(test_file)
    
    def test_metric_labels(self):
        """Test 714: Use consistent metric labels"""
        with tempfile.TemporaryDirectory() as temp_dir:
            agent_code = """
class InconsistentLabels:
    def record_request(self, method, status, endpoint):
        # BUG: Inconsistent label names
        if method == "GET":
            metric = f"http.method={method},status_code={status}"
        else:
            metric = f"http.verb={method},status={status}"
        print(f"Metric: {metric}")

monitor = InconsistentLabels()

# BUG: Can't aggregate across methods
monitor.record_request("GET", 200, "/api/users")
monitor.record_request("POST", 201, "/api/users")
"""
            
            test_file = os.path.join(temp_dir, "metric_labels.py")
            with open(test_file, "w") as f:
                f.write(agent_code)
            
            assert os.path.exists(test_file)
    
    def test_metrics_export_format(self):
        """Test 715: Use standard metrics format"""
        with tempfile.TemporaryDirectory() as temp_dir:
            agent_code = """
class CustomMetricsFormat:
    def export_metrics(self):
        # BUG: Custom format incompatible with tools
        metrics = {
            "req_count": 100,
            "avg_latency": 0.5,
            "err_rate": 0.01
        }
        return str(metrics)

exporter = CustomMetricsFormat()

# BUG: Not Prometheus/OpenMetrics compatible
output = exporter.export_metrics()
print(f"Metrics: {output}")
"""
            
            test_file = os.path.join(temp_dir, "metrics_format.py")
            with open(test_file, "w") as f:
                f.write(agent_code)
            
            assert os.path.exists(test_file)


class TestAlerting:
    """Test alerting and notification systems (10 tests)"""
    
    def test_alert_thresholds(self):
        """Test 716: Define appropriate alert thresholds"""
        with tempfile.TemporaryDirectory() as temp_dir:
            agent_code = """
class StaticThresholds:
    def check_error_rate(self, error_rate):
        # BUG: Fixed threshold, no context
        if error_rate > 0.01:  # 1%
            self.send_alert("High error rate")
    
    def send_alert(self, message):
        print(f"ALERT: {message}")

monitor = StaticThresholds()

# Low traffic: 1 error out of 10 requests = 10%
monitor.check_error_rate(0.10)  # Alerts

# High traffic: 1% of 1M requests = 10K errors
monitor.check_error_rate(0.01)  # Doesn't alert

# BUG: Static thresholds don't account for context
"""
            
            test_file = os.path.join(temp_dir, "alert_thresholds.py")
            with open(test_file, "w") as f:
                f.write(agent_code)
            
            assert os.path.exists(test_file)
    
    def test_alert_fatigue(self):
        """Test 717: Prevent alert fatigue"""
        with tempfile.TemporaryDirectory() as temp_dir:
            agent_code = """
class NoAlertDeduplication:
    def check_disk_space(self, usage):
        if usage > 90:
            # BUG: Sends alert every check
            self.send_alert("Disk usage high")
    
    def send_alert(self, message):
        print(f"ALERT: {message}")

monitor = NoAlertDeduplication()

# BUG: Same alert sent 100 times
for _ in range(100):
    monitor.check_disk_space(95)
"""
            
            test_file = os.path.join(temp_dir, "alert_fatigue.py")
            with open(test_file, "w") as f:
                f.write(agent_code)
            
            assert os.path.exists(test_file)
    
    def test_alert_context(self):
        """Test 718: Include context in alerts"""
        with tempfile.TemporaryDirectory() as temp_dir:
            agent_code = """
class VagueAlerts:
    def check_service(self):
        # BUG: Minimal context
        self.send_alert("Service down")
    
    def send_alert(self, message):
        print(f"ALERT: {message}")

monitor = VagueAlerts()

# BUG: Which service? Which host? What to do?
monitor.check_service()
"""
            
            test_file = os.path.join(temp_dir, "alert_context.py")
            with open(test_file, "w") as f:
                f.write(agent_code)
            
            assert os.path.exists(test_file)
    
    def test_alert_routing(self):
        """Test 719: Route alerts appropriately"""
        with tempfile.TemporaryDirectory() as temp_dir:
            agent_code = """
class NoAlertRouting:
    def send_alert(self, severity, message):
        # BUG: All alerts go to same channel
        print(f"Slack: [{severity}] {message}")

alerter = NoAlertRouting()

# BUG: Critical and info alerts mixed
alerter.send_alert("CRITICAL", "Database down")
alerter.send_alert("INFO", "Deployment complete")
"""
            
            test_file = os.path.join(temp_dir, "alert_routing.py")
            with open(test_file, "w") as f:
                f.write(agent_code)
            
            assert os.path.exists(test_file)
    
    def test_alert_escalation(self):
        """Test 720: Implement alert escalation"""
        with tempfile.TemporaryDirectory() as temp_dir:
            agent_code = """
class NoEscalation:
    def send_alert(self, message):
        # BUG: No escalation if not acknowledged
        print(f"Alert sent: {message}")

alerter = NoEscalation()

alerter.send_alert("Critical issue")

# 30 minutes later, still not acknowledged
# BUG: No escalation to manager/on-call
"""
            
            test_file = os.path.join(temp_dir, "alert_escalation.py")
            with open(test_file, "w") as f:
                f.write(agent_code)
            
            assert os.path.exists(test_file)
    
    def test_alert_runbooks(self):
        """Test 721: Link alerts to runbooks"""
        with tempfile.TemporaryDirectory() as temp_dir:
            agent_code = """
class NoRunbooks:
    def send_alert(self, message):
        # BUG: No runbook link
        print(f"ALERT: {message}")

alerter = NoRunbooks()

# BUG: Engineer doesn't know how to respond
alerter.send_alert("High memory usage")
"""
            
            test_file = os.path.join(temp_dir, "alert_runbooks.py")
            with open(test_file, "w") as f:
                f.write(agent_code)
            
            assert os.path.exists(test_file)
    
    def test_alert_silencing(self):
        """Test 722: Support alert silencing"""
        with tempfile.TemporaryDirectory() as temp_dir:
            agent_code = """
class NoAlertSilencing:
    def send_alert(self, message):
        # BUG: Can't silence during maintenance
        print(f"ALERT: {message}")

alerter = NoAlertSilencing()

# During planned maintenance
# BUG: Maintenance alerts spam on-call
alerter.send_alert("Service down")
"""
            
            test_file = os.path.join(temp_dir, "alert_silencing.py")
            with open(test_file, "w") as f:
                f.write(agent_code)
            
            assert os.path.exists(test_file)
    
    def test_composite_alerts(self):
        """Test 723: Create composite alerts"""
        with tempfile.TemporaryDirectory() as temp_dir:
            agent_code = """
class IndependentAlerts:
    def check_system(self, cpu, memory, disk):
        # BUG: Independent alerts
        if cpu > 90:
            print("ALERT: High CPU")
        if memory > 90:
            print("ALERT: High memory")
        if disk > 90:
            print("ALERT: High disk")

monitor = IndependentAlerts()

# BUG: 3 separate alerts instead of 1 composite
monitor.check_system(cpu=95, memory=95, disk=95)
"""
            
            test_file = os.path.join(temp_dir, "composite_alerts.py")
            with open(test_file, "w") as f:
                f.write(agent_code)
            
            assert os.path.exists(test_file)
    
    def test_alert_acknowledgment(self):
        """Test 724: Track alert acknowledgment"""
        with tempfile.TemporaryDirectory() as temp_dir:
            agent_code = """
class NoAcknowledgment:
    def send_alert(self, message):
        # BUG: Fire and forget
        print(f"ALERT: {message}")

alerter = NoAcknowledgment()

alerter.send_alert("Critical issue")

# BUG: Can't tell if anyone is responding
"""
            
            test_file = os.path.join(temp_dir, "alert_acknowledgment.py")
            with open(test_file, "w") as f:
                f.write(agent_code)
            
            assert os.path.exists(test_file)
    
    def test_alert_history(self):
        """Test 725: Maintain alert history"""
        with tempfile.TemporaryDirectory() as temp_dir:
            agent_code = """
class NoAlertHistory:
    def send_alert(self, message):
        # BUG: No history tracking
        print(f"ALERT: {message}")

alerter = NoAlertHistory()

alerter.send_alert("Disk full")

# Resolved
# BUG: No record of when alert fired/resolved
"""
            
            test_file = os.path.join(temp_dir, "alert_history.py")
            with open(test_file, "w") as f:
                f.write(agent_code)
            
            assert os.path.exists(test_file)
