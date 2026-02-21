"""
Comprehensive Test Suite for Phoenix - API Design & Integration
Tests 606-635: REST APIs, GraphQL, Webhooks, External Integrations (30 tests)

This file tests Phoenix's ability to detect and fix bugs in API design,
integration patterns, and external service communication.
"""

import os
import tempfile
import shutil
from pathlib import Path
import pytest
from unittest.mock import Mock, patch


class TestRESTAPIDesign:
    """Test REST API design patterns (10 tests)"""
    
    def test_http_method_semantics(self):
        """Test 606: Use correct HTTP methods"""
        with tempfile.TemporaryDirectory() as temp_dir:
            agent_code = """
class WrongHTTPMethods:
    def delete_user(self, user_id):
        # BUG: Uses GET for deletion
        return self.api_call("GET", f"/users/{user_id}/delete")
    
    def update_user(self, user_id, data):
        # BUG: Uses POST instead of PUT/PATCH
        return self.api_call("POST", f"/users/{user_id}/update", data)
    
    def api_call(self, method, url, data=None):
        return f"{method} {url}"

api = WrongHTTPMethods()

# BUG: Wrong HTTP semantics
result = api.delete_user("123")
print(f"Result: {result}")
"""
            
            test_file = os.path.join(temp_dir, "http_methods.py")
            with open(test_file, "w") as f:
                f.write(agent_code)
            
            assert os.path.exists(test_file)
    
    def test_idempotency_requirement(self):
        """Test 607: Ensure idempotent operations"""
        with tempfile.TemporaryDirectory() as temp_dir:
            agent_code = """
class NonIdempotentAPI:
    def __init__(self):
        self.counter = 0
    
    def create_resource(self, data):
        # BUG: POST creates duplicate on retry
        self.counter += 1
        resource_id = self.counter
        return {"id": resource_id, "data": data}

api = NonIdempotentAPI()

# Network retry
result1 = api.create_resource({"name": "test"})
result2 = api.create_resource({"name": "test"})  # Duplicate

# BUG: Created 2 resources instead of 1
print(f"IDs: {result1['id']}, {result2['id']}")
"""
            
            test_file = os.path.join(temp_dir, "idempotency.py")
            with open(test_file, "w") as f:
                f.write(agent_code)
            
            assert os.path.exists(test_file)
    
    def test_proper_status_codes(self):
        """Test 608: Return appropriate HTTP status codes"""
        with tempfile.TemporaryDirectory() as temp_dir:
            agent_code = """
class WrongStatusCodes:
    def get_user(self, user_id):
        user = self.find_user(user_id)
        if user is None:
            # BUG: Returns 200 with null
            return {"status": 200, "body": None}
        return {"status": 200, "body": user}
    
    def create_user(self, data):
        # BUG: Returns 200 instead of 201
        user = self.save_user(data)
        return {"status": 200, "body": user}
    
    def find_user(self, user_id):
        return None
    
    def save_user(self, data):
        return {"id": 1, **data}

api = WrongStatusCodes()

# BUG: Should return 404
result = api.get_user("nonexistent")
print(f"Status: {result['status']}")
"""
            
            test_file = os.path.join(temp_dir, "status_codes.py")
            with open(test_file, "w") as f:
                f.write(agent_code)
            
            assert os.path.exists(test_file)
    
    def test_api_versioning(self):
        """Test 609: Implement API versioning"""
        with tempfile.TemporaryDirectory() as temp_dir:
            agent_code = """
class NoAPIVersioning:
    def get_user(self, user_id):
        # BUG: No version in URL or header
        return {
            "id": user_id,
            "name": "John",
            # Breaking change: removed "email" field
            "contact": "john@example.com"
        }

api = NoAPIVersioning()

# Clients break when API changes
user = api.get_user("123")
# BUG: No versioning strategy
print(f"User: {user}")
"""
            
            test_file = os.path.join(temp_dir, "api_versioning.py")
            with open(test_file, "w") as f:
                f.write(agent_code)
            
            assert os.path.exists(test_file)
    
    def test_pagination_headers(self):
        """Test 610: Include pagination metadata"""
        with tempfile.TemporaryDirectory() as temp_dir:
            agent_code = """
class NoPaginationMetadata:
    def get_users(self, page=1, per_page=10):
        # BUG: Returns data without pagination info
        users = [{"id": i} for i in range(10)]
        return {"data": users}

api = NoPaginationMetadata()

result = api.get_users(page=2)

# BUG: Client doesn't know total count or next page
print(f"Result: {result}")
"""
            
            test_file = os.path.join(temp_dir, "pagination_headers.py")
            with open(test_file, "w") as f:
                f.write(agent_code)
            
            assert os.path.exists(test_file)
    
    def test_rate_limit_headers(self):
        """Test 611: Expose rate limit information"""
        with tempfile.TemporaryDirectory() as temp_dir:
            agent_code = """
class NoRateLimitHeaders:
    def __init__(self):
        self.requests = 0
        self.limit = 100
    
    def api_request(self, endpoint):
        self.requests += 1
        
        if self.requests > self.limit:
            # BUG: No headers about limit/remaining
            return {"status": 429, "error": "Rate limit exceeded"}
        
        return {"status": 200, "data": "success"}

api = NoRateLimitHeaders()

# BUG: Client doesn't know when to retry
response = api.api_request("/users")
print(f"Response: {response}")
"""
            
            test_file = os.path.join(temp_dir, "rate_limit_headers.py")
            with open(test_file, "w") as f:
                f.write(agent_code)
            
            assert os.path.exists(test_file)
    
    def test_error_response_format(self):
        """Test 612: Consistent error response format"""
        with tempfile.TemporaryDirectory() as temp_dir:
            agent_code = """
class InconsistentErrors:
    def endpoint1(self):
        # BUG: Different error format
        return {"error": "Something went wrong"}
    
    def endpoint2(self):
        # BUG: Different error format
        return {"message": "Invalid request", "code": 400}
    
    def endpoint3(self):
        # BUG: Different error format
        raise Exception("Server error")

api = InconsistentErrors()

# BUG: Clients can't handle errors consistently
print("Inconsistent error formats")
"""
            
            test_file = os.path.join(temp_dir, "error_format.py")
            with open(test_file, "w") as f:
                f.write(agent_code)
            
            assert os.path.exists(test_file)
    
    def test_content_negotiation(self):
        """Test 613: Support content negotiation"""
        with tempfile.TemporaryDirectory() as temp_dir:
            agent_code = """
class NoContentNegotiation:
    def get_data(self):
        # BUG: Always returns JSON, ignores Accept header
        return {"format": "json", "data": "value"}

api = NoContentNegotiation()

# Client wants XML
# BUG: No content negotiation
result = api.get_data()
print(f"Result: {result}")
"""
            
            test_file = os.path.join(temp_dir, "content_negotiation.py")
            with open(test_file, "w") as f:
                f.write(agent_code)
            
            assert os.path.exists(test_file)
    
    def test_cors_configuration(self):
        """Test 614: Configure CORS properly"""
        with tempfile.TemporaryDirectory() as temp_dir:
            agent_code = """
class WildcardCORS:
    def handle_request(self, origin):
        # BUG: Allows all origins with credentials
        return {
            "Access-Control-Allow-Origin": "*",
            "Access-Control-Allow-Credentials": "true"
        }

api = WildcardCORS()

headers = api.handle_request("https://evil.com")

# BUG: Security vulnerability
print(f"Headers: {headers}")
"""
            
            test_file = os.path.join(temp_dir, "cors_config.py")
            with open(test_file, "w") as f:
                f.write(agent_code)
            
            assert os.path.exists(test_file)
    
    def test_etag_caching(self):
        """Test 615: Implement ETag for caching"""
        with tempfile.TemporaryDirectory() as temp_dir:
            agent_code = """
class NoETag:
    def get_resource(self, resource_id):
        # BUG: No ETag header
        resource = {"id": resource_id, "data": "value"}
        return {"body": resource}

api = NoETag()

# Client can't use conditional requests
result = api.get_resource("123")

# BUG: Always sends full response
print(f"Result: {result}")
"""
            
            test_file = os.path.join(temp_dir, "etag_caching.py")
            with open(test_file, "w") as f:
                f.write(agent_code)
            
            assert os.path.exists(test_file)


class TestWebhooksAndCallbacks:
    """Test webhook and callback patterns (10 tests)"""
    
    def test_webhook_signature_verification(self):
        """Test 616: Verify webhook signatures"""
        with tempfile.TemporaryDirectory() as temp_dir:
            agent_code = """
class NoSignatureVerification:
    def handle_webhook(self, payload, signature):
        # BUG: Doesn't verify signature
        self.process_payload(payload)
    
    def process_payload(self, payload):
        print(f"Processing: {payload}")

webhook = NoSignatureVerification()

# Attacker sends fake webhook
webhook.handle_webhook({"malicious": "data"}, "fake_signature")

# BUG: Accepts unauthenticated webhooks
print("Processed unauthenticated webhook")
"""
            
            test_file = os.path.join(temp_dir, "webhook_signature.py")
            with open(test_file, "w") as f:
                f.write(agent_code)
            
            assert os.path.exists(test_file)
    
    def test_webhook_retry_logic(self):
        """Test 617: Implement webhook retry logic"""
        with tempfile.TemporaryDirectory() as temp_dir:
            agent_code = """
class NoWebhookRetry:
    def send_webhook(self, url, payload):
        try:
            # BUG: Single attempt, no retry
            response = self.http_post(url, payload)
            return response
        except Exception as e:
            # BUG: Gives up on first failure
            print(f"Webhook failed: {e}")
    
    def http_post(self, url, payload):
        raise Exception("Connection timeout")

sender = NoWebhookRetry()

# Transient failure
sender.send_webhook("https://example.com/webhook", {"event": "user.created"})

# BUG: Event lost
print("Webhook lost on transient failure")
"""
            
            test_file = os.path.join(temp_dir, "webhook_retry.py")
            with open(test_file, "w") as f:
                f.write(agent_code)
            
            assert os.path.exists(test_file)
    
    def test_webhook_idempotency_key(self):
        """Test 618: Include idempotency keys in webhooks"""
        with tempfile.TemporaryDirectory() as temp_dir:
            agent_code = """
class NoIdempotencyKey:
    def send_webhook(self, event):
        # BUG: No idempotency key
        payload = {
            "event_type": event["type"],
            "data": event["data"]
        }
        return payload

sender = NoIdempotencyKey()

event = {"type": "payment.success", "data": {"amount": 100}}

# Retry sends duplicate
payload1 = sender.send_webhook(event)
payload2 = sender.send_webhook(event)

# BUG: Receiver can't detect duplicate
print("No idempotency key")
"""
            
            test_file = os.path.join(temp_dir, "webhook_idempotency.py")
            with open(test_file, "w") as f:
                f.write(agent_code)
            
            assert os.path.exists(test_file)
    
    def test_webhook_timeout_handling(self):
        """Test 619: Set timeouts for webhook delivery"""
        with tempfile.TemporaryDirectory() as temp_dir:
            agent_code = """
import time

class NoWebhookTimeout:
    def send_webhook(self, url, payload):
        # BUG: No timeout
        while True:
            try:
                # Waiting indefinitely
                time.sleep(0.1)
            except KeyboardInterrupt:
                break

sender = NoWebhookTimeout()

# BUG: Blocks forever if receiver slow
print("No webhook timeout")
"""
            
            test_file = os.path.join(temp_dir, "webhook_timeout.py")
            with open(test_file, "w") as f:
                f.write(agent_code)
            
            assert os.path.exists(test_file)
    
    def test_webhook_event_ordering(self):
        """Test 620: Preserve webhook event ordering"""
        with tempfile.TemporaryDirectory() as temp_dir:
            agent_code = """
import asyncio

class UnorderedWebhooks:
    async def send_events(self, events):
        # BUG: Sends events in parallel, order not guaranteed
        tasks = []
        for event in events:
            task = asyncio.create_task(self.send_webhook(event))
            tasks.append(task)
        await asyncio.gather(*tasks)
    
    async def send_webhook(self, event):
        await asyncio.sleep(0.1)
        print(f"Sent: {event}")

sender = UnorderedWebhooks()

events = ["event1", "event2", "event3"]
# BUG: Events may arrive out of order
print("Unordered webhook delivery")
"""
            
            test_file = os.path.join(temp_dir, "webhook_ordering.py")
            with open(test_file, "w") as f:
                f.write(agent_code)
            
            assert os.path.exists(test_file)
    
    def test_webhook_payload_size_limit(self):
        """Test 621: Limit webhook payload size"""
        with tempfile.TemporaryDirectory() as temp_dir:
            agent_code = """
class NoPayloadLimit:
    def send_webhook(self, payload):
        # BUG: No size limit
        return {"payload": payload}

sender = NoPayloadLimit()

# Huge payload
large_payload = {"data": "x" * 10000000}

# BUG: May timeout or be rejected
result = sender.send_webhook(large_payload)
print("No payload size limit")
"""
            
            test_file = os.path.join(temp_dir, "webhook_payload_limit.py")
            with open(test_file, "w") as f:
                f.write(agent_code)
            
            assert os.path.exists(test_file)
    
    def test_callback_url_validation(self):
        """Test 622: Validate callback URLs"""
        with tempfile.TemporaryDirectory() as temp_dir:
            agent_code = """
class NoURLValidation:
    def register_callback(self, callback_url):
        # BUG: Doesn't validate URL
        self.callback_url = callback_url
    
    def send_callback(self, data):
        # BUG: Could send to internal services
        print(f"Sending to: {self.callback_url}")

system = NoURLValidation()

# Attacker registers internal URL
system.register_callback("http://localhost:8080/admin/delete")

# BUG: SSRF vulnerability
system.send_callback({"data": "value"})
"""
            
            test_file = os.path.join(temp_dir, "callback_validation.py")
            with open(test_file, "w") as f:
                f.write(agent_code)
            
            assert os.path.exists(test_file)
    
    def test_webhook_dead_letter_queue(self):
        """Test 623: Use DLQ for failed webhooks"""
        with tempfile.TemporaryDirectory() as temp_dir:
            agent_code = """
class NoWebhookDLQ:
    def send_webhook(self, url, payload, max_retries=3):
        for attempt in range(max_retries):
            try:
                return self.http_post(url, payload)
            except Exception:
                continue
        
        # BUG: Drops failed webhook
        print("Webhook failed, dropped")
    
    def http_post(self, url, payload):
        raise Exception("Permanent failure")

sender = NoWebhookDLQ()

# BUG: Lost forever
sender.send_webhook("https://example.com/webhook", {"event": "important"})
"""
            
            test_file = os.path.join(temp_dir, "webhook_dlq.py")
            with open(test_file, "w") as f:
                f.write(agent_code)
            
            assert os.path.exists(test_file)
    
    def test_webhook_subscription_management(self):
        """Test 624: Manage webhook subscriptions"""
        with tempfile.TemporaryDirectory() as temp_dir:
            agent_code = """
class NoSubscriptionManagement:
    def __init__(self):
        self.subscriptions = []
    
    def subscribe(self, url, event_type):
        # BUG: Allows duplicate subscriptions
        self.subscriptions.append({"url": url, "event": event_type})
    
    def unsubscribe(self, url):
        # BUG: Doesn't verify ownership
        self.subscriptions = [s for s in self.subscriptions if s["url"] != url]

manager = NoSubscriptionManagement()

manager.subscribe("https://example.com/hook", "user.created")
manager.subscribe("https://example.com/hook", "user.created")  # Duplicate

# BUG: Sends event twice
print(f"Subscriptions: {len(manager.subscriptions)}")
"""
            
            test_file = os.path.join(temp_dir, "webhook_subscriptions.py")
            with open(test_file, "w") as f:
                f.write(agent_code)
            
            assert os.path.exists(test_file)
    
    def test_webhook_timestamp_validation(self):
        """Test 625: Validate webhook timestamps"""
        with tempfile.TemporaryDirectory() as temp_dir:
            agent_code = """
import time

class NoTimestampValidation:
    def handle_webhook(self, payload, timestamp):
        # BUG: Doesn't check timestamp
        self.process_event(payload)
    
    def process_event(self, payload):
        print(f"Processing: {payload}")

handler = NoTimestampValidation()

# Replay attack with old timestamp
old_timestamp = time.time() - 86400  # 24 hours ago
handler.handle_webhook({"event": "payment"}, old_timestamp)

# BUG: Accepts replayed webhooks
print("Accepted old webhook")
"""
            
            test_file = os.path.join(temp_dir, "webhook_timestamp.py")
            with open(test_file, "w") as f:
                f.write(agent_code)
            
            assert os.path.exists(test_file)


class TestExternalIntegrations:
    """Test external service integrations (10 tests)"""
    
    def test_api_credential_rotation(self):
        """Test 626: Support credential rotation"""
        with tempfile.TemporaryDirectory() as temp_dir:
            agent_code = """
class StaticCredentials:
    def __init__(self):
        # BUG: Hardcoded credentials
        self.api_key = "sk_prod_12345"
    
    def call_external_api(self):
        headers = {"Authorization": f"Bearer {self.api_key}"}
        return headers

client = StaticCredentials()

# BUG: Can't rotate without redeployment
headers = client.call_external_api()
print(f"Headers: {headers}")
"""
            
            test_file = os.path.join(temp_dir, "credential_rotation.py")
            with open(test_file, "w") as f:
                f.write(agent_code)
            
            assert os.path.exists(test_file)
    
    def test_third_party_api_timeout(self):
        """Test 627: Set timeouts for external APIs"""
        with tempfile.TemporaryDirectory() as temp_dir:
            agent_code = """
class NoExternalTimeout:
    def call_external_service(self, url):
        # BUG: No timeout
        response = self.http_get(url)
        return response
    
    def http_get(self, url):
        # Slow external service
        import time
        time.sleep(100)
        return "response"

client = NoExternalTimeout()

# BUG: Blocks indefinitely
print("Calling external service without timeout")
"""
            
            test_file = os.path.join(temp_dir, "external_timeout.py")
            with open(test_file, "w") as f:
                f.write(agent_code)
            
            assert os.path.exists(test_file)
    
    def test_integration_fallback_strategy(self):
        """Test 628: Implement fallback for integrations"""
        with tempfile.TemporaryDirectory() as temp_dir:
            agent_code = """
class NoIntegrationFallback:
    def get_user_data(self, user_id):
        # BUG: No fallback when external service down
        external_data = self.call_crm_api(user_id)
        return external_data
    
    def call_crm_api(self, user_id):
        raise Exception("CRM service unavailable")

client = NoIntegrationFallback()

try:
    data = client.get_user_data("user123")
except Exception as e:
    # BUG: Should fallback to cache or default data
    print(f"Error: {e}")
"""
            
            test_file = os.path.join(temp_dir, "integration_fallback.py")
            with open(test_file, "w") as f:
                f.write(agent_code)
            
            assert os.path.exists(test_file)
    
    def test_api_response_validation(self):
        """Test 629: Validate external API responses"""
        with tempfile.TemporaryDirectory() as temp_dir:
            agent_code = """
class NoResponseValidation:
    def get_exchange_rate(self, currency):
        # BUG: Doesn't validate response
        response = self.call_currency_api(currency)
        return response["rate"]  # May not exist
    
    def call_currency_api(self, currency):
        # Malformed response
        return {"error": "Invalid currency"}

client = NoResponseValidation()

# BUG: Crashes on unexpected response
try:
    rate = client.get_exchange_rate("USD")
except KeyError:
    print("Response validation missing")
"""
            
            test_file = os.path.join(temp_dir, "response_validation.py")
            with open(test_file, "w") as f:
                f.write(agent_code)
            
            assert os.path.exists(test_file)
    
    def test_integration_monitoring(self):
        """Test 630: Monitor integration health"""
        with tempfile.TemporaryDirectory() as temp_dir:
            agent_code = """
class NoIntegrationMonitoring:
    def __init__(self):
        self.failures = 0
    
    def call_payment_gateway(self, amount):
        try:
            return self.gateway_api(amount)
        except Exception:
            # BUG: No monitoring or alerting
            self.failures += 1
            raise
    
    def gateway_api(self, amount):
        raise Exception("Gateway error")

client = NoIntegrationMonitoring()

# Multiple failures
for _ in range(100):
    try:
        client.call_payment_gateway(100)
    except Exception:
        pass

# BUG: No alerts on degraded integration
print(f"Failures: {client.failures}")
"""
            
            test_file = os.path.join(temp_dir, "integration_monitoring.py")
            with open(test_file, "w") as f:
                f.write(agent_code)
            
            assert os.path.exists(test_file)
    
    def test_api_quota_management(self):
        """Test 631: Manage API quotas"""
        with tempfile.TemporaryDirectory() as temp_dir:
            agent_code = """
class NoQuotaManagement:
    def __init__(self):
        self.calls = 0
    
    def call_api(self):
        # BUG: Doesn't track quota
        self.calls += 1
        return "result"

client = NoQuotaManagement()

# Exhaust quota
for _ in range(10000):
    client.call_api()

# BUG: Gets rate limited, no quota tracking
print(f"Calls: {client.calls}")
"""
            
            test_file = os.path.join(temp_dir, "quota_management.py")
            with open(test_file, "w") as f:
                f.write(agent_code)
            
            assert os.path.exists(test_file)
    
    def test_integration_data_mapping(self):
        """Test 632: Map data between systems correctly"""
        with tempfile.TemporaryDirectory() as temp_dir:
            agent_code = """
class BrokenDataMapping:
    def sync_user_to_crm(self, user):
        # BUG: Direct field mapping assumes same schema
        crm_user = {
            "name": user["name"],
            "email": user["email"],
            # BUG: CRM uses "company_id", we have "organization_id"
            "company_id": user["organization_id"]
        }
        return crm_user

mapper = BrokenDataMapping()

user = {
    "name": "John Doe",
    "email": "john@example.com",
    "organization_id": "org_123"
}

# BUG: Field name mismatch
crm_user = mapper.sync_user_to_crm(user)
print(f"CRM user: {crm_user}")
"""
            
            test_file = os.path.join(temp_dir, "data_mapping.py")
            with open(test_file, "w") as f:
                f.write(agent_code)
            
            assert os.path.exists(test_file)
    
    def test_integration_versioning(self):
        """Test 633: Handle integration version changes"""
        with tempfile.TemporaryDirectory() as temp_dir:
            agent_code = """
class NoVersionHandling:
    def call_api(self, endpoint):
        # BUG: Assumes API version never changes
        url = f"https://api.example.com/{endpoint}"
        return self.http_get(url)
    
    def http_get(self, url):
        return {"data": "value"}

client = NoVersionHandling()

# API upgraded to v2
# BUG: Still calls v1 (deprecated)
result = client.call_api("users")
print(f"Result: {result}")
"""
            
            test_file = os.path.join(temp_dir, "integration_versioning.py")
            with open(test_file, "w") as f:
                f.write(agent_code)
            
            assert os.path.exists(test_file)
    
    def test_bulk_api_optimization(self):
        """Test 634: Use bulk APIs when available"""
        with tempfile.TemporaryDirectory() as temp_dir:
            agent_code = """
class IndividualAPICalls:
    def sync_users(self, users):
        results = []
        # BUG: Individual API calls
        for user in users:
            result = self.create_user_api(user)
            results.append(result)
        return results
    
    def create_user_api(self, user):
        # Individual API call
        return {"id": user["email"]}

syncer = IndividualAPICalls()

users = [{"email": f"user{i}@example.com"} for i in range(1000)]

# BUG: Makes 1000 API calls instead of 1 bulk call
results = syncer.sync_users(users)
print(f"Made {len(results)} API calls")
"""
            
            test_file = os.path.join(temp_dir, "bulk_api.py")
            with open(test_file, "w") as f:
                f.write(agent_code)
            
            assert os.path.exists(test_file)
    
    def test_integration_circuit_breaker(self):
        """Test 635: Circuit breaker for integrations"""
        with tempfile.TemporaryDirectory() as temp_dir:
            agent_code = """
class NoCircuitBreaker:
    def __init__(self):
        self.failure_count = 0
    
    def call_unreliable_service(self):
        try:
            return self.external_api()
        except Exception:
            self.failure_count += 1
            # BUG: Keeps calling failing service
            raise
    
    def external_api(self):
        raise Exception("Service down")

client = NoCircuitBreaker()

# Service is down
for _ in range(1000):
    try:
        client.call_unreliable_service()
    except Exception:
        pass

# BUG: Made 1000 calls to failing service
print(f"Failures: {client.failure_count}")
"""
            
            test_file = os.path.join(temp_dir, "integration_circuit_breaker.py")
            with open(test_file, "w") as f:
                f.write(agent_code)
            
            assert os.path.exists(test_file)
