# API Endpoint Integration Tests for Project Phoenix

import pytest
import json
from httpx import AsyncClient
from datetime import datetime, timedelta
import logging

logger = logging.getLogger(__name__)

# ===== Health Check Endpoints =====

@pytest.mark.asyncio
class TestHealthEndpoints:
    """Test health check and status endpoints"""
    
    async def test_health_check(self, client: AsyncClient):
        """Test /health endpoint"""
        response = await client.get("/api/health")
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "healthy"
        assert "timestamp" in data
        assert "version" in data
    
    async def test_readiness_check(self, client: AsyncClient):
        """Test /ready endpoint"""
        response = await client.get("/api/ready")
        assert response.status_code == 200
        data = response.json()
        assert data["ready"] is True
        assert "database" in data
        assert "cache" in data
    
    async def test_metrics_endpoint(self, client: AsyncClient):
        """Test /metrics endpoint"""
        response = await client.get("/metrics")
        assert response.status_code == 200
        # Prometheus format check
        assert "# HELP" in response.text or "# TYPE" in response.text

# ===== System Endpoints =====

@pytest.mark.asyncio
@pytest.mark.database
class TestSystemEndpoints:
    """Test /api/systems endpoints"""
    
    async def test_create_system(self, client: AsyncClient):
        """Test POST /api/systems"""
        system_data = {
            "name": "test-system-1",
            "description": "Test system",
            "environment": "test",
            "threshold": 0.85,
            "is_active": True
        }
        response = await client.post("/api/systems", json=system_data)
        assert response.status_code == 201
        data = response.json()
        assert data["name"] == "test-system-1"
        assert "id" in data
        assert data["is_active"] is True
    
    async def test_list_systems(self, client: AsyncClient, sample_system):
        """Test GET /api/systems"""
        response = await client.get("/api/systems")
        assert response.status_code == 200
        data = response.json()
        assert isinstance(data, list)
        assert len(data) > 0
        assert any(s["name"] == "test-system" for s in data)
    
    async def test_get_system(self, client: AsyncClient, sample_system):
        """Test GET /api/systems/{system_id}"""
        response = await client.get(f"/api/systems/{sample_system.id}")
        assert response.status_code == 200
        data = response.json()
        assert data["id"] == sample_system.id
        assert data["name"] == "test-system"
    
    async def test_update_system(self, client: AsyncClient, sample_system):
        """Test PATCH /api/systems/{system_id}"""
        update_data = {
            "description": "Updated description",
            "threshold": 0.9
        }
        response = await client.patch(
            f"/api/systems/{sample_system.id}",
            json=update_data
        )
        assert response.status_code == 200
        data = response.json()
        assert data["description"] == "Updated description"
        assert data["threshold"] == 0.9
    
    async def test_delete_system(self, client: AsyncClient, sample_system):
        """Test DELETE /api/systems/{system_id}"""
        response = await client.delete(f"/api/systems/{sample_system.id}")
        assert response.status_code == 204
        
        # Verify deletion
        response = await client.get(f"/api/systems/{sample_system.id}")
        assert response.status_code == 404
    
    async def test_get_nonexistent_system(self, client: AsyncClient):
        """Test GET for non-existent system"""
        response = await client.get("/api/systems/99999")
        assert response.status_code == 404
        data = response.json()
        assert "detail" in data

# ===== Event Endpoints =====

@pytest.mark.asyncio
@pytest.mark.database
class TestEventEndpoints:
    """Test /api/events endpoints"""
    
    async def test_create_event(self, client: AsyncClient, sample_system):
        """Test POST /api/events"""
        event_data = {
            "system_id": sample_system.id,
            "event_type": "anomaly",
            "severity": "critical",
            "data": {"metric": "cpu", "value": 98}
        }
        response = await client.post("/api/events", json=event_data)
        assert response.status_code == 201
        data = response.json()
        assert data["event_type"] == "anomaly"
        assert data["severity"] == "critical"
        assert "id" in data
        assert "timestamp" in data
    
    async def test_list_events(self, client: AsyncClient, sample_event):
        """Test GET /api/events"""
        response = await client.get("/api/events")
        assert response.status_code == 200
        data = response.json()
        assert isinstance(data, list)
        assert len(data) > 0
    
    async def test_list_events_with_filters(self, client: AsyncClient, sample_event, sample_system):
        """Test GET /api/events with filters"""
        response = await client.get(
            f"/api/events?system_id={sample_system.id}&severity=high"
        )
        assert response.status_code == 200
        data = response.json()
        assert isinstance(data, list)
    
    async def test_get_event(self, client: AsyncClient, sample_event):
        """Test GET /api/events/{event_id}"""
        response = await client.get(f"/api/events/{sample_event.id}")
        assert response.status_code == 200
        data = response.json()
        assert data["id"] == sample_event.id
        assert data["event_type"] == "anomaly"
    
    async def test_mark_event_processed(self, client: AsyncClient, sample_event):
        """Test PATCH /api/events/{event_id}/process"""
        response = await client.patch(f"/api/events/{sample_event.id}/process")
        assert response.status_code == 200
        data = response.json()
        assert data["is_processed"] is True

# ===== Policy Endpoints =====

@pytest.mark.asyncio
@pytest.mark.database
class TestPolicyEndpoints:
    """Test /api/policies endpoints"""
    
    async def test_create_policy(self, client: AsyncClient, sample_system):
        """Test POST /api/policies"""
        policy_data = {
            "name": "cpu-threshold-policy",
            "description": "Alert on high CPU",
            "system_id": sample_system.id,
            "rules": {"metric": "cpu", "threshold": 80}
        }
        response = await client.post("/api/policies", json=policy_data)
        assert response.status_code == 201
        data = response.json()
        assert data["name"] == "cpu-threshold-policy"
        assert "id" in data
    
    async def test_list_policies(self, client: AsyncClient, sample_policy):
        """Test GET /api/policies"""
        response = await client.get("/api/policies")
        assert response.status_code == 200
        data = response.json()
        assert isinstance(data, list)
    
    async def test_get_policy(self, client: AsyncClient, sample_policy):
        """Test GET /api/policies/{policy_id}"""
        response = await client.get(f"/api/policies/{sample_policy.id}")
        assert response.status_code == 200
        data = response.json()
        assert data["id"] == sample_policy.id
    
    async def test_update_policy(self, client: AsyncClient, sample_policy):
        """Test PATCH /api/policies/{policy_id}"""
        update_data = {
            "description": "Updated policy description"
        }
        response = await client.patch(
            f"/api/policies/{sample_policy.id}",
            json=update_data
        )
        assert response.status_code == 200

# ===== Metrics Endpoints =====

@pytest.mark.asyncio
@pytest.mark.database
class TestMetricsEndpoints:
    """Test /api/metrics endpoints"""
    
    async def test_create_metric(self, client: AsyncClient, sample_system):
        """Test POST /api/metrics"""
        metric_data = {
            "system_id": sample_system.id,
            "metric_name": "memory_usage",
            "metric_value": 64.2,
            "unit": "percent"
        }
        response = await client.post("/api/metrics", json=metric_data)
        assert response.status_code == 201
        data = response.json()
        assert data["metric_name"] == "memory_usage"
        assert data["metric_value"] == 64.2
    
    async def test_list_metrics(self, client: AsyncClient, sample_metric):
        """Test GET /api/metrics"""
        response = await client.get("/api/metrics")
        assert response.status_code == 200
        data = response.json()
        assert isinstance(data, list)
    
    async def test_get_metric_by_system(self, client: AsyncClient, sample_metric, sample_system):
        """Test GET /api/metrics?system_id={system_id}"""
        response = await client.get(f"/api/metrics?system_id={sample_system.id}")
        assert response.status_code == 200
        data = response.json()
        assert isinstance(data, list)
    
    async def test_get_metric_time_range(self, client: AsyncClient, sample_metric, sample_system):
        """Test GET /api/metrics with time range"""
        start_time = (datetime.utcnow() - timedelta(hours=1)).isoformat()
        end_time = datetime.utcnow().isoformat()
        response = await client.get(
            f"/api/metrics?system_id={sample_system.id}&start_time={start_time}&end_time={end_time}"
        )
        assert response.status_code == 200

# ===== Correction Endpoints =====

@pytest.mark.asyncio
@pytest.mark.database
class TestCorrectionEndpoints:
    """Test /api/corrections endpoints"""
    
    async def test_create_correction(self, client: AsyncClient, sample_event):
        """Test POST /api/corrections"""
        correction_data = {
            "event_id": sample_event.id,
            "action": "scale_up",
            "parameters": {"replicas": 5}
        }
        response = await client.post("/api/corrections", json=correction_data)
        assert response.status_code == 201
        data = response.json()
        assert data["action"] == "scale_up"
        assert "id" in data
    
    async def test_list_corrections(self, client: AsyncClient):
        """Test GET /api/corrections"""
        response = await client.get("/api/corrections")
        assert response.status_code == 200
        assert isinstance(response.json(), list)

# ===== Error Handling =====

@pytest.mark.asyncio
class TestErrorHandling:
    """Test error handling and validation"""
    
    async def test_invalid_json(self, client: AsyncClient):
        """Test invalid JSON payload"""
        response = await client.post(
            "/api/systems",
            content=b"invalid json",
            headers={"Content-Type": "application/json"}
        )
        assert response.status_code == 422
    
    async def test_missing_required_field(self, client: AsyncClient):
        """Test missing required field"""
        system_data = {
            "description": "Missing name field"
        }
        response = await client.post("/api/systems", json=system_data)
        assert response.status_code == 422
        data = response.json()
        assert "detail" in data
    
    async def test_invalid_field_type(self, client: AsyncClient):
        """Test invalid field type"""
        system_data = {
            "name": "test",
            "threshold": "not-a-number"  # Should be float
        }
        response = await client.post("/api/systems", json=system_data)
        assert response.status_code == 422
    
    async def test_unauthorized_access(self, client: AsyncClient):
        """Test unauthorized access (if auth is implemented)"""
        # This test depends on auth implementation
        # Placeholder for future auth tests
        pass
    
    async def test_rate_limiting(self, client: AsyncClient):
        """Test rate limiting (if implemented)"""
        # Make multiple requests
        for _ in range(10):
            response = await client.get("/api/health")
            if response.status_code == 429:  # Too Many Requests
                break
        # This test depends on rate limiting implementation

# ===== Pagination Tests =====

@pytest.mark.asyncio
@pytest.mark.database
class TestPagination:
    """Test pagination functionality"""
    
    async def test_list_with_pagination(self, client: AsyncClient, sample_system):
        """Test GET with pagination parameters"""
        # Create multiple events
        for i in range(15):
            event_data = {
                "system_id": sample_system.id,
                "event_type": "test",
                "severity": "low",
                "data": {"value": i}
            }
            await client.post("/api/events", json=event_data)
        
        # Test pagination
        response = await client.get("/api/events?skip=0&limit=10")
        assert response.status_code == 200
        data = response.json()
        assert len(data) <= 10
    
    async def test_default_pagination(self, client: AsyncClient, sample_event):
        """Test default pagination limits"""
        response = await client.get("/api/events")
        assert response.status_code == 200
        data = response.json()
        # Check default limit is reasonable (not all records)
        assert len(data) <= 100
