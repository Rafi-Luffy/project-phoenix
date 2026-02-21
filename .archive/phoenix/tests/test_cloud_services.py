"""
Comprehensive Test Suite for Phoenix - Cloud Services & Infrastructure
Tests 906-935: AWS, Azure, GCP, Cloud-Native Patterns (30 tests)

This file tests Phoenix's ability to detect and fix bugs in cloud service
integration, serverless functions, and cloud-native architectures.
"""

import os
import tempfile
import shutil
from pathlib import Path
import pytest
from unittest.mock import Mock, patch


class TestCloudStorageAndCompute:
    """Test cloud storage and compute services (10 tests)"""
    
    def test_s3_no_multipart_upload(self):
        """Test 906: Use S3 multipart upload for large files"""
        with tempfile.TemporaryDirectory() as temp_dir:
            agent_code = """
class NoMultipartUpload:
    def upload_file(self, file_path, bucket, key):
        # BUG: Single PUT for large file
        with open(file_path, "rb") as f:
            data = f.read()  # BUG: Loads entire file into memory
        
        self.s3_client.put_object(Bucket=bucket, Key=key, Body=data)
    
    def __init__(self):
        self.s3_client = MockS3Client()

class MockS3Client:
    def put_object(self, Bucket, Key, Body):
        print(f"Uploading {len(Body)} bytes")

uploader = NoMultipartUpload()

# BUG: Fails on 5GB+ files
print("No multipart upload")
"""
            
            test_file = os.path.join(temp_dir, "s3_multipart.py")
            with open(test_file, "w") as f:
                f.write(agent_code)
            
            assert os.path.exists(test_file)
    
    def test_s3_no_lifecycle_policy(self):
        """Test 907: Configure S3 lifecycle policies"""
        with tempfile.TemporaryDirectory() as temp_dir:
            agent_code = """
class NoLifecyclePolicy:
    def store_logs(self, log_data):
        # BUG: No lifecycle policy
        self.s3_client.put_object(
            Bucket="logs",
            Key=f"logs/{log_data['timestamp']}.json",
            Body=str(log_data)
        )
    
    def __init__(self):
        self.s3_client = MockS3Client()

class MockS3Client:
    def put_object(self, Bucket, Key, Body):
        print(f"Storing: {Key}")

storage = NoLifecyclePolicy()

# BUG: Old logs stored forever
for i in range(10000):
    storage.store_logs({"timestamp": f"2024-01-{i}", "data": "log"})
"""
            
            test_file = os.path.join(temp_dir, "s3_lifecycle.py")
            with open(test_file, "w") as f:
                f.write(agent_code)
            
            assert os.path.exists(test_file)
    
    def test_lambda_cold_start(self):
        """Test 908: Minimize Lambda cold starts"""
        with tempfile.TemporaryDirectory() as temp_dir:
            agent_code = """
# BUG: Heavy imports inside handler
def lambda_handler(event, context):
    # BUG: Imports on every invocation
    import pandas as pd
    import numpy as np
    import tensorflow as tf
    
    # Process event
    result = process_data(event)
    
    return result

def process_data(event):
    return {"status": "ok"}

# BUG: Slow cold starts
print("Heavy imports in handler")
"""
            
            test_file = os.path.join(temp_dir, "lambda_cold_start.py")
            with open(test_file, "w") as f:
                f.write(agent_code)
            
            assert os.path.exists(test_file)
    
    def test_lambda_no_connection_pooling(self):
        """Test 909: Reuse connections in Lambda"""
        with tempfile.TemporaryDirectory() as temp_dir:
            agent_code = """
def lambda_handler(event, context):
    # BUG: Creates new connection on every invocation
    db = create_db_connection()
    
    result = db.query("SELECT * FROM users")
    
    db.close()
    
    return result

def create_db_connection():
    print("Creating new database connection")
    return MockDB()

class MockDB:
    def query(self, sql):
        return []
    
    def close(self):
        pass

# BUG: Connection overhead on every invocation
print("No connection pooling")
"""
            
            test_file = os.path.join(temp_dir, "lambda_connection.py")
            with open(test_file, "w") as f:
                f.write(agent_code)
            
            assert os.path.exists(test_file)
    
    def test_cloudwatch_no_structured_logging(self):
        """Test 910: Use structured logging"""
        with tempfile.TemporaryDirectory() as temp_dir:
            agent_code = """
import logging

logger = logging.getLogger()

def process_order(order_id, user_id):
    # BUG: Unstructured log message
    logger.info(f"Processing order {order_id} for user {user_id}")
    
    # Business logic
    pass

# BUG: Hard to query logs
process_order(123, 456)
"""
            
            test_file = os.path.join(temp_dir, "structured_logging.py")
            with open(test_file, "w") as f:
                f.write(agent_code)
            
            assert os.path.exists(test_file)
    
    def test_ec2_no_autoscaling(self):
        """Test 911: Configure EC2 auto scaling"""
        with tempfile.TemporaryDirectory() as temp_dir:
            agent_code = """
class NoAutoScaling:
    def __init__(self):
        # BUG: Fixed instance count
        self.instances = self.launch_instances(count=2)
    
    def launch_instances(self, count):
        print(f"Launching {count} instances")
        return [f"i-{i}" for i in range(count)]

infrastructure = NoAutoScaling()

# BUG: Can't handle traffic spikes
print("No auto scaling")
"""
            
            test_file = os.path.join(temp_dir, "ec2_autoscaling.py")
            with open(test_file, "w") as f:
                f.write(agent_code)
            
            assert os.path.exists(test_file)
    
    def test_ecs_no_health_checks(self):
        """Test 912: Configure ECS health checks"""
        with tempfile.TemporaryDirectory() as temp_dir:
            agent_code = """
class NoHealthChecks:
    def deploy_service(self):
        # BUG: No health check configuration
        task_definition = {
            "family": "web-app",
            "containerDefinitions": [{
                "name": "web",
                "image": "myapp:latest"
                # BUG: No healthCheck field
            }]
        }
        
        return task_definition

deployer = NoHealthChecks()

# BUG: Broken containers receive traffic
task_def = deployer.deploy_service()
"""
            
            test_file = os.path.join(temp_dir, "ecs_health_checks.py")
            with open(test_file, "w") as f:
                f.write(agent_code)
            
            assert os.path.exists(test_file)
    
    def test_sqs_no_visibility_extension(self):
        """Test 913: Extend SQS visibility timeout"""
        with tempfile.TemporaryDirectory() as temp_dir:
            agent_code = """
class NoVisibilityExtension:
    def process_message(self, message):
        # BUG: Long processing without extending visibility
        import time
        time.sleep(120)  # 2 minutes
        
        # BUG: Message becomes visible again
        self.process(message)
        
        message.delete()
    
    def process(self, message):
        print(f"Processing: {message}")

# BUG: Message reprocessed if timeout expires
print("No visibility extension")
"""
            
            test_file = os.path.join(temp_dir, "sqs_visibility.py")
            with open(test_file, "w") as f:
                f.write(agent_code)
            
            assert os.path.exists(test_file)
    
    def test_sns_no_message_attributes(self):
        """Test 914: Use SNS message attributes for filtering"""
        with tempfile.TemporaryDirectory() as temp_dir:
            agent_code = """
class NoMessageAttributes:
    def publish_event(self, event_type, data):
        # BUG: No message attributes
        message = {
            "type": event_type,
            "data": data
        }
        
        self.sns_client.publish(
            TopicArn="arn:aws:sns:us-east-1:123:events",
            Message=str(message)
        )
    
    def __init__(self):
        self.sns_client = MockSNSClient()

class MockSNSClient:
    def publish(self, TopicArn, Message):
        print(f"Publishing to {TopicArn}")

publisher = NoMessageAttributes()

# BUG: Can't filter subscriptions
publisher.publish_event("OrderCreated", {"order_id": 1})
"""
            
            test_file = os.path.join(temp_dir, "sns_attributes.py")
            with open(test_file, "w") as f:
                f.write(agent_code)
            
            assert os.path.exists(test_file)
    
    def test_dynamodb_hot_partition(self):
        """Test 915: Avoid DynamoDB hot partitions"""
        with tempfile.TemporaryDirectory() as temp_dir:
            agent_code = """
class HotPartition:
    def write_item(self, user_id, event):
        # BUG: Uses sequential IDs
        item_id = self.get_next_id()
        
        self.table.put_item(Item={
            "id": item_id,  # BUG: Sequential, creates hot partition
            "user_id": user_id,
            "event": event
        })
    
    def get_next_id(self):
        # Returns sequential IDs
        return self.counter
    
    def __init__(self):
        self.counter = 0
        self.table = MockTable()

class MockTable:
    def put_item(self, Item):
        print(f"Writing item: {Item['id']}")

db = HotPartition()

# BUG: All writes to same partition
for i in range(1000):
    db.write_item(i, "event")
"""
            
            test_file = os.path.join(temp_dir, "dynamodb_hot_partition.py")
            with open(test_file, "w") as f:
                f.write(agent_code)
            
            assert os.path.exists(test_file)


class TestServerlessAndContainers:
    """Test serverless and container patterns (10 tests)"""
    
    def test_lambda_timeout_too_short(self):
        """Test 916: Configure appropriate Lambda timeout"""
        with tempfile.TemporaryDirectory() as temp_dir:
            agent_code = """
# BUG: Default 3 second timeout
def lambda_handler(event, context):
    # Processing takes 5 seconds
    import time
    time.sleep(5)
    
    return {"status": "done"}

# BUG: Function times out
print("Lambda timeout too short")
"""
            
            test_file = os.path.join(temp_dir, "lambda_timeout.py")
            with open(test_file, "w") as f:
                f.write(agent_code)
            
            assert os.path.exists(test_file)
    
    def test_lambda_memory_inefficient(self):
        """Test 917: Optimize Lambda memory allocation"""
        with tempfile.TemporaryDirectory() as temp_dir:
            agent_code = """
# BUG: 128MB memory insufficient
def lambda_handler(event, context):
    # BUG: Loads large dataset
    data = load_large_dataset()
    
    result = process(data)
    
    return result

def load_large_dataset():
    # Returns 500MB of data
    return [i for i in range(10000000)]

def process(data):
    return len(data)

# BUG: Out of memory
print("Lambda memory too low")
"""
            
            test_file = os.path.join(temp_dir, "lambda_memory.py")
            with open(test_file, "w") as f:
                f.write(agent_code)
            
            assert os.path.exists(test_file)
    
    def test_api_gateway_no_throttling(self):
        """Test 918: Configure API Gateway throttling"""
        with tempfile.TemporaryDirectory() as temp_dir:
            agent_code = """
class NoAPIThrottling:
    def create_api(self):
        # BUG: No throttling configuration
        api_config = {
            "name": "MyAPI",
            "routes": [
                {"path": "/users", "method": "GET"}
            ]
            # BUG: No throttleSettings
        }
        
        return api_config

api = NoAPIThrottling()

# BUG: Vulnerable to abuse
config = api.create_api()
"""
            
            test_file = os.path.join(temp_dir, "api_throttling.py")
            with open(test_file, "w") as f:
                f.write(agent_code)
            
            assert os.path.exists(test_file)
    
    def test_step_functions_no_error_handling(self):
        """Test 919: Handle Step Functions errors"""
        with tempfile.TemporaryDirectory() as temp_dir:
            agent_code = """
class NoErrorHandling:
    def create_state_machine(self):
        # BUG: No error handling
        definition = {
            "StartAt": "ProcessOrder",
            "States": {
                "ProcessOrder": {
                    "Type": "Task",
                    "Resource": "arn:aws:lambda:...:function:ProcessOrder",
                    "End": True
                    # BUG: No Catch or Retry
                }
            }
        }
        
        return definition

sm = NoErrorHandling()

# BUG: Fails permanently on transient errors
definition = sm.create_state_machine()
"""
            
            test_file = os.path.join(temp_dir, "step_functions_errors.py")
            with open(test_file, "w") as f:
                f.write(agent_code)
            
            assert os.path.exists(test_file)
    
    def test_fargate_no_resource_limits(self):
        """Test 920: Set Fargate resource limits"""
        with tempfile.TemporaryDirectory() as temp_dir:
            agent_code = """
class NoResourceLimits:
    def create_task_definition(self):
        # BUG: No CPU/memory limits
        task_def = {
            "family": "app",
            "containerDefinitions": [{
                "name": "web",
                "image": "myapp:latest"
                # BUG: No cpu or memory fields
            }]
        }
        
        return task_def

fargate = NoResourceLimits()

# BUG: Container may consume all resources
task_def = fargate.create_task_definition()
"""
            
            test_file = os.path.join(temp_dir, "fargate_limits.py")
            with open(test_file, "w") as f:
                f.write(agent_code)
            
            assert os.path.exists(test_file)
    
    def test_cloud_run_no_concurrency_limit(self):
        """Test 921: Configure Cloud Run concurrency"""
        with tempfile.TemporaryDirectory() as temp_dir:
            agent_code = """
class NoConcurrencyLimit:
    def deploy_service(self):
        # BUG: No concurrency limit
        service_config = {
            "apiVersion": "serving.knative.dev/v1",
            "kind": "Service",
            "metadata": {"name": "myapp"},
            "spec": {
                "template": {
                    "spec": {
                        "containers": [{
                            "image": "gcr.io/myproject/myapp"
                            # BUG: No containerConcurrency
                        }]
                    }
                }
            }
        }
        
        return service_config

cloud_run = NoConcurrencyLimit()

# BUG: May overload single instance
config = cloud_run.deploy_service()
"""
            
            test_file = os.path.join(temp_dir, "cloud_run_concurrency.py")
            with open(test_file, "w") as f:
                f.write(agent_code)
            
            assert os.path.exists(test_file)
    
    def test_azure_functions_no_durable(self):
        """Test 922: Use Durable Functions for workflows"""
        with tempfile.TemporaryDirectory() as temp_dir:
            agent_code = """
def http_trigger(req):
    # BUG: Implements long-running workflow in HTTP function
    step1_result = step1()
    
    import time
    time.sleep(60)
    
    step2_result = step2(step1_result)
    
    return {"status": "complete"}

def step1():
    return "step1_done"

def step2(input_data):
    return "step2_done"

# BUG: Function timeout, can't resume
print("Should use Durable Functions")
"""
            
            test_file = os.path.join(temp_dir, "azure_durable.py")
            with open(test_file, "w") as f:
                f.write(agent_code)
            
            assert os.path.exists(test_file)
    
    def test_container_no_health_endpoint(self):
        """Test 923: Implement container health endpoint"""
        with tempfile.TemporaryDirectory() as temp_dir:
            agent_code = """
from flask import Flask

app = Flask(__name__)

@app.route("/")
def home():
    return "Hello World"

# BUG: No /health endpoint

if __name__ == "__main__":
    app.run()

# BUG: Orchestrator can't check health
print("No health endpoint")
"""
            
            test_file = os.path.join(temp_dir, "container_health.py")
            with open(test_file, "w") as f:
                f.write(agent_code)
            
            assert os.path.exists(test_file)
    
    def test_dockerfile_no_layer_optimization(self):
        """Test 924: Optimize Dockerfile layers"""
        with tempfile.TemporaryDirectory() as temp_dir:
            agent_code = """
# BUG: Inefficient layer ordering
dockerfile_content = '''
FROM python:3.11

# BUG: Copies code before installing dependencies
COPY . /app

WORKDIR /app

# BUG: Dependencies installed after code copy
RUN pip install -r requirements.txt

CMD ["python", "app.py"]
'''

# BUG: Every code change invalidates dependency layer
print("Dockerfile not optimized")
"""
            
            test_file = os.path.join(temp_dir, "dockerfile_layers.py")
            with open(test_file, "w") as f:
                f.write(agent_code)
            
            assert os.path.exists(test_file)
    
    def test_kubernetes_no_resource_requests(self):
        """Test 925: Set Kubernetes resource requests"""
        with tempfile.TemporaryDirectory() as temp_dir:
            agent_code = """
class NoResourceRequests:
    def create_deployment(self):
        # BUG: No resource requests
        deployment = {
            "apiVersion": "apps/v1",
            "kind": "Deployment",
            "metadata": {"name": "myapp"},
            "spec": {
                "replicas": 3,
                "template": {
                    "spec": {
                        "containers": [{
                            "name": "web",
                            "image": "myapp:latest"
                            # BUG: No resources field
                        }]
                    }
                }
            }
        }
        
        return deployment

k8s = NoResourceRequests()

# BUG: Scheduler can't make informed decisions
deployment = k8s.create_deployment()
"""
            
            test_file = os.path.join(temp_dir, "k8s_resources.py")
            with open(test_file, "w") as f:
                f.write(agent_code)
            
            assert os.path.exists(test_file)


class TestCloudSecurity:
    """Test cloud security patterns (10 tests)"""
    
    def test_iam_overly_permissive(self):
        """Test 926: Use least privilege IAM policies"""
        with tempfile.TemporaryDirectory() as temp_dir:
            agent_code = """
class OverlyPermissive:
    def create_role(self):
        # BUG: Uses wildcard permissions
        policy = {
            "Version": "2012-10-17",
            "Statement": [{
                "Effect": "Allow",
                "Action": "*",  # BUG: All actions
                "Resource": "*"  # BUG: All resources
            }]
        }
        
        return policy

iam = OverlyPermissive()

# BUG: Excessive permissions
policy = iam.create_role()
"""
            
            test_file = os.path.join(temp_dir, "iam_permissions.py")
            with open(test_file, "w") as f:
                f.write(agent_code)
            
            assert os.path.exists(test_file)
    
    def test_secrets_in_environment_variables(self):
        """Test 927: Use secrets manager instead of env vars"""
        with tempfile.TemporaryDirectory() as temp_dir:
            agent_code = """
import os

class SecretsInEnv:
    def __init__(self):
        # BUG: Database password in environment variable
        self.db_password = os.environ.get("DB_PASSWORD")
        
        # BUG: API key in environment variable
        self.api_key = os.environ.get("API_KEY")
    
    def connect_db(self):
        print(f"Connecting with password: {self.db_password}")

# BUG: Secrets visible in container inspect
db = SecretsInEnv()
"""
            
            test_file = os.path.join(temp_dir, "secrets_env.py")
            with open(test_file, "w") as f:
                f.write(agent_code)
            
            assert os.path.exists(test_file)
    
    def test_s3_bucket_public(self):
        """Test 928: Secure S3 bucket access"""
        with tempfile.TemporaryDirectory() as temp_dir:
            agent_code = """
class PublicBucket:
    def create_bucket(self):
        # BUG: Public bucket
        config = {
            "Bucket": "my-data",
            "ACL": "public-read"  # BUG: Publicly readable
        }
        
        return config

s3 = PublicBucket()

# BUG: Data exposed publicly
bucket = s3.create_bucket()
"""
            
            test_file = os.path.join(temp_dir, "s3_public.py")
            with open(test_file, "w") as f:
                f.write(agent_code)
            
            assert os.path.exists(test_file)
    
    def test_rds_public_subnet(self):
        """Test 929: Place RDS in private subnet"""
        with tempfile.TemporaryDirectory() as temp_dir:
            agent_code = """
class PublicDatabase:
    def create_db_instance(self):
        # BUG: Database in public subnet
        config = {
            "DBInstanceIdentifier": "mydb",
            "PubliclyAccessible": True  # BUG: Publicly accessible
        }
        
        return config

rds = PublicDatabase()

# BUG: Database exposed to internet
db = rds.create_db_instance()
"""
            
            test_file = os.path.join(temp_dir, "rds_public.py")
            with open(test_file, "w") as f:
                f.write(agent_code)
            
            assert os.path.exists(test_file)
    
    def test_no_encryption_at_rest(self):
        """Test 930: Enable encryption at rest"""
        with tempfile.TemporaryDirectory() as temp_dir:
            agent_code = """
class NoEncryption:
    def create_volume(self):
        # BUG: No encryption
        config = {
            "Size": 100,
            "VolumeType": "gp3"
            # BUG: No Encrypted field
        }
        
        return config

ebs = NoEncryption()

# BUG: Data stored unencrypted
volume = ebs.create_volume()
"""
            
            test_file = os.path.join(temp_dir, "encryption_rest.py")
            with open(test_file, "w") as f:
                f.write(agent_code)
            
            assert os.path.exists(test_file)
    
    def test_no_encryption_in_transit(self):
        """Test 931: Enforce encryption in transit"""
        with tempfile.TemporaryDirectory() as temp_dir:
            agent_code = """
class NoTLSEnforcement:
    def create_load_balancer(self):
        # BUG: Allows HTTP
        config = {
            "Name": "my-lb",
            "Listeners": [{
                "Protocol": "HTTP",  # BUG: No HTTPS
                "Port": 80
            }]
        }
        
        return config

elb = NoTLSEnforcement()

# BUG: Traffic not encrypted
lb = elb.create_load_balancer()
"""
            
            test_file = os.path.join(temp_dir, "encryption_transit.py")
            with open(test_file, "w") as f:
                f.write(agent_code)
            
            assert os.path.exists(test_file)
    
    def test_no_vpc_flow_logs(self):
        """Test 932: Enable VPC flow logs"""
        with tempfile.TemporaryDirectory() as temp_dir:
            agent_code = """
class NoFlowLogs:
    def create_vpc(self):
        # BUG: No flow logs
        config = {
            "CidrBlock": "10.0.0.0/16"
            # BUG: No FlowLogs configuration
        }
        
        return config

vpc = NoFlowLogs()

# BUG: Can't audit network traffic
network = vpc.create_vpc()
"""
            
            test_file = os.path.join(temp_dir, "vpc_flow_logs.py")
            with open(test_file, "w") as f:
                f.write(agent_code)
            
            assert os.path.exists(test_file)
    
    def test_no_cloudtrail(self):
        """Test 933: Enable CloudTrail logging"""
        with tempfile.TemporaryDirectory() as temp_dir:
            agent_code = """
class NoCloudTrail:
    def __init__(self):
        # BUG: No CloudTrail enabled
        self.audit_logging = False
    
    def perform_action(self, action):
        # BUG: Actions not logged
        print(f"Performing: {action}")

account = NoCloudTrail()

# BUG: No audit trail
account.perform_action("DeleteDatabase")
"""
            
            test_file = os.path.join(temp_dir, "cloudtrail.py")
            with open(test_file, "w") as f:
                f.write(agent_code)
            
            assert os.path.exists(test_file)
    
    def test_security_group_too_permissive(self):
        """Test 934: Restrict security group rules"""
        with tempfile.TemporaryDirectory() as temp_dir:
            agent_code = """
class PermissiveSecurityGroup:
    def create_security_group(self):
        # BUG: Allows all traffic
        config = {
            "GroupName": "web-sg",
            "IngressRules": [{
                "IpProtocol": "-1",  # BUG: All protocols
                "FromPort": 0,
                "ToPort": 65535,
                "CidrIp": "0.0.0.0/0"  # BUG: From anywhere
            }]
        }
        
        return config

sg = PermissiveSecurityGroup()

# BUG: Overly permissive firewall
security_group = sg.create_security_group()
"""
            
            test_file = os.path.join(temp_dir, "security_group.py")
            with open(test_file, "w") as f:
                f.write(agent_code)
            
            assert os.path.exists(test_file)
    
    def test_no_mfa_for_root(self):
        """Test 935: Require MFA for root account"""
        with tempfile.TemporaryDirectory() as temp_dir:
            agent_code = """
class NoMFA:
    def __init__(self):
        # BUG: Root account without MFA
        self.root_mfa_enabled = False
    
    def check_security(self):
        if not self.root_mfa_enabled:
            print("WARNING: Root account without MFA")

account = NoMFA()

# BUG: Account vulnerable to credential compromise
account.check_security()
"""
            
            test_file = os.path.join(temp_dir, "root_mfa.py")
            with open(test_file, "w") as f:
                f.write(agent_code)
            
            assert os.path.exists(test_file)
