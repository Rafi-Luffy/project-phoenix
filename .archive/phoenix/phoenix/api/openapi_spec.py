"""
Phoenix API OpenAPI/Swagger Specification

This module generates the complete OpenAPI 3.0 specification for the Phoenix
autonomous healing system API, including all endpoints, schemas, and operations.
"""

import json
from dataclasses import dataclass, asdict
from typing import Dict, List, Any, Optional
from enum import Enum


class HealthStatus(str, Enum):
    HEALTHY = "healthy"
    DEGRADED = "degraded"
    UNHEALTHY = "unhealthy"


class FixStatus(str, Enum):
    PENDING = "pending"
    APPLIED = "applied"
    FAILED = "failed"
    REVERTED = "reverted"


@dataclass
class HealthCheckResponse:
    """Health check response schema"""
    status: HealthStatus
    timestamp: str
    components: Dict[str, str]
    latency_ms: int


@dataclass
class HealingCycleRequest:
    """Healing cycle request schema"""
    failure_signature: str
    failure_context: Dict[str, Any]
    priority: str = "normal"  # low, normal, high, critical
    auto_apply: bool = True
    max_retries: int = 3


@dataclass
class FixResult:
    """Fix result schema"""
    fix_id: str
    status: FixStatus
    confidence_score: float
    execution_time_ms: float
    error_message: Optional[str] = None


@dataclass
class HealingCycleResponse:
    """Healing cycle response schema"""
    cycle_id: str
    failure_signature: str
    success: bool
    fix_result: FixResult
    timestamp: str
    cached: bool


@dataclass
class MetricsResponse:
    """Metrics response schema"""
    total_cycles: int
    successful_cycles: int
    failed_cycles: int
    success_rate: float
    cache_hit_rate: float
    avg_latency_ms: float
    peak_latency_ms: float
    total_cost_dollars: float


@dataclass
class ConfigSection:
    """Configuration section schema"""
    section_name: str
    settings: Dict[str, Any]
    required_fields: List[str]
    optional_fields: List[str]


@dataclass
class CacheEntry:
    """Cache entry schema"""
    signature: str
    fix: Dict[str, Any]
    created_at: str
    last_used: str
    hit_count: int
    success_rate: float


class PhoenixOpenAPI:
    """Generate OpenAPI 3.0 specification for Phoenix API"""
    
    def __init__(self):
        self.spec = {
            "openapi": "3.0.0",
            "info": self._get_info(),
            "servers": self._get_servers(),
            "paths": self._get_paths(),
            "components": self._get_components(),
            "tags": self._get_tags(),
            "x-logo": {
                "url": "https://example.com/phoenix-logo.png",
                "altText": "Phoenix Logo"
            }
        }
    
    def _get_info(self) -> Dict[str, Any]:
        """API information"""
        return {
            "title": "Phoenix Autonomous Healing API",
            "description": "API for the Phoenix autonomous healing system. Enables programmatic control of the healing orchestrator, metrics collection, configuration management, and cache management.",
            "version": "2.4.0",
            "contact": {
                "name": "Phoenix Team",
                "email": "support@phoenix.local",
                "url": "https://phoenix.local/support"
            },
            "license": {
                "name": "Apache 2.0",
                "url": "https://www.apache.org/licenses/LICENSE-2.0.html"
            },
            "x-capabilities": [
                "Autonomous failure healing",
                "Real-time metrics collection",
                "Cache management",
                "Configuration management",
                "Health monitoring",
                "Cost tracking"
            ]
        }
    
    def _get_servers(self) -> List[Dict[str, Any]]:
        """API server configurations"""
        return [
            {
                "url": "http://localhost:8000",
                "description": "Development server"
            },
            {
                "url": "https://api.phoenix.local",
                "description": "Production server",
                "variables": {
                    "version": {
                        "default": "v1",
                        "enum": ["v1", "v2"]
                    }
                }
            }
        ]
    
    def _get_paths(self) -> Dict[str, Any]:
        """API paths and endpoints"""
        return {
            "/health": self._endpoint_health(),
            "/ready": self._endpoint_ready(),
            "/healing/cycle": self._endpoint_healing_cycle(),
            "/healing/cycles/{cycle_id}": self._endpoint_healing_cycle_detail(),
            "/metrics": self._endpoint_metrics(),
            "/metrics/summary": self._endpoint_metrics_summary(),
            "/config": self._endpoint_config(),
            "/config/validate": self._endpoint_config_validate(),
            "/cache": self._endpoint_cache(),
            "/cache/{signature}": self._endpoint_cache_entry(),
            "/cache/clear": self._endpoint_cache_clear(),
            "/health/detailed": self._endpoint_health_detailed()
        }
    
    def _endpoint_health(self) -> Dict[str, Any]:
        """GET /health endpoint"""
        return {
            "get": {
                "summary": "Health Check",
                "description": "Check if Phoenix is healthy and ready to serve requests. Returns basic health status.",
                "operationId": "getHealth",
                "tags": ["Health"],
                "responses": {
                    "200": {
                        "description": "System is healthy",
                        "content": {
                            "application/json": {
                                "schema": {"$ref": "#/components/schemas/HealthCheckResponse"}
                            }
                        }
                    },
                    "503": {
                        "description": "System is unhealthy",
                        "content": {
                            "application/json": {
                                "schema": {"$ref": "#/components/schemas/ErrorResponse"}
                            }
                        }
                    }
                },
                "x-code-samples": [
                    {
                        "lang": "curl",
                        "source": "curl -X GET http://localhost:8000/health"
                    },
                    {
                        "lang": "python",
                        "source": "import requests\nresponse = requests.get('http://localhost:8000/health')\nprint(response.json())"
                    }
                ]
            }
        }
    
    def _endpoint_ready(self) -> Dict[str, Any]:
        """GET /ready endpoint"""
        return {
            "get": {
                "summary": "Readiness Check",
                "description": "Check if Phoenix is ready to accept healing requests. Verifies all required components are available.",
                "operationId": "getReady",
                "tags": ["Health"],
                "responses": {
                    "200": {
                        "description": "System is ready",
                        "content": {
                            "application/json": {
                                "schema": {"$ref": "#/components/schemas/ReadinessResponse"}
                            }
                        }
                    },
                    "503": {
                        "description": "System is not ready",
                        "content": {
                            "application/json": {
                                "schema": {"$ref": "#/components/schemas/ErrorResponse"}
                            }
                        }
                    }
                }
            }
        }
    
    def _endpoint_healing_cycle(self) -> Dict[str, Any]:
        """POST /healing/cycle endpoint"""
        return {
            "post": {
                "summary": "Start Healing Cycle",
                "description": "Trigger a healing cycle for a detected failure. Phoenix will analyze the failure, generate a fix, validate it, and optionally apply it.",
                "operationId": "startHealingCycle",
                "tags": ["Healing"],
                "requestBody": {
                    "required": True,
                    "content": {
                        "application/json": {
                            "schema": {"$ref": "#/components/schemas/HealingCycleRequest"}
                        }
                    }
                },
                "responses": {
                    "200": {
                        "description": "Healing cycle completed",
                        "content": {
                            "application/json": {
                                "schema": {"$ref": "#/components/schemas/HealingCycleResponse"}
                            }
                        }
                    },
                    "400": {
                        "description": "Invalid request",
                        "content": {
                            "application/json": {
                                "schema": {"$ref": "#/components/schemas/ErrorResponse"}
                            }
                        }
                    },
                    "503": {
                        "description": "Service unavailable",
                        "content": {
                            "application/json": {
                                "schema": {"$ref": "#/components/schemas/ErrorResponse"}
                            }
                        }
                    }
                },
                "x-code-samples": [
                    {
                        "lang": "python",
                        "source": """import requests

payload = {
    "failure_signature": "timeout_error",
    "failure_context": {
        "endpoint": "/api/users",
        "error": "Connection timeout",
        "duration_seconds": 30
    },
    "priority": "high",
    "auto_apply": True
}

response = requests.post(
    'http://localhost:8000/healing/cycle',
    json=payload
)
print(response.json())"""
                    }
                ]
            }
        }
    
    def _endpoint_healing_cycle_detail(self) -> Dict[str, Any]:
        """GET /healing/cycles/{cycle_id} endpoint"""
        return {
            "get": {
                "summary": "Get Healing Cycle Details",
                "description": "Retrieve detailed information about a specific healing cycle execution.",
                "operationId": "getHealingCycleDetail",
                "tags": ["Healing"],
                "parameters": [
                    {
                        "name": "cycle_id",
                        "in": "path",
                        "required": True,
                        "schema": {"type": "string"},
                        "description": "Healing cycle ID"
                    }
                ],
                "responses": {
                    "200": {
                        "description": "Healing cycle details",
                        "content": {
                            "application/json": {
                                "schema": {"$ref": "#/components/schemas/HealingCycleResponse"}
                            }
                        }
                    },
                    "404": {
                        "description": "Cycle not found",
                        "content": {
                            "application/json": {
                                "schema": {"$ref": "#/components/schemas/ErrorResponse"}
                            }
                        }
                    }
                }
            }
        }
    
    def _endpoint_metrics(self) -> Dict[str, Any]:
        """GET /metrics endpoint"""
        return {
            "get": {
                "summary": "Get Metrics",
                "description": "Retrieve detailed metrics about healing operations, cache performance, and system health.",
                "operationId": "getMetrics",
                "tags": ["Metrics"],
                "parameters": [
                    {
                        "name": "since",
                        "in": "query",
                        "schema": {"type": "string", "format": "date-time"},
                        "description": "Get metrics since this timestamp (ISO 8601)"
                    },
                    {
                        "name": "until",
                        "in": "query",
                        "schema": {"type": "string", "format": "date-time"},
                        "description": "Get metrics until this timestamp (ISO 8601)"
                    }
                ],
                "responses": {
                    "200": {
                        "description": "Metrics data",
                        "content": {
                            "application/json": {
                                "schema": {"$ref": "#/components/schemas/MetricsResponse"}
                            }
                        }
                    }
                }
            }
        }
    
    def _endpoint_metrics_summary(self) -> Dict[str, Any]:
        """GET /metrics/summary endpoint"""
        return {
            "get": {
                "summary": "Get Metrics Summary",
                "description": "Retrieve a summary of metrics in human-readable format.",
                "operationId": "getMetricsSummary",
                "tags": ["Metrics"],
                "responses": {
                    "200": {
                        "description": "Metrics summary",
                        "content": {
                            "text/plain": {
                                "schema": {"type": "string"}
                            }
                        }
                    }
                }
            }
        }
    
    def _endpoint_config(self) -> Dict[str, Any]:
        """GET /config endpoint"""
        return {
            "get": {
                "summary": "Get Configuration",
                "description": "Retrieve current Phoenix configuration (sensitive data redacted).",
                "operationId": "getConfig",
                "tags": ["Configuration"],
                "responses": {
                    "200": {
                        "description": "Current configuration",
                        "content": {
                            "application/json": {
                                "schema": {"$ref": "#/components/schemas/ConfigResponse"}
                            }
                        }
                    }
                }
            },
            "put": {
                "summary": "Update Configuration",
                "description": "Update Phoenix configuration. Changes take effect immediately.",
                "operationId": "updateConfig",
                "tags": ["Configuration"],
                "requestBody": {
                    "required": True,
                    "content": {
                        "application/json": {
                            "schema": {"$ref": "#/components/schemas/ConfigUpdateRequest"}
                        }
                    }
                },
                "responses": {
                    "200": {
                        "description": "Configuration updated",
                        "content": {
                            "application/json": {
                                "schema": {"$ref": "#/components/schemas/ConfigResponse"}
                            }
                        }
                    },
                    "400": {
                        "description": "Invalid configuration",
                        "content": {
                            "application/json": {
                                "schema": {"$ref": "#/components/schemas/ErrorResponse"}
                            }
                        }
                    }
                }
            }
        }
    
    def _endpoint_config_validate(self) -> Dict[str, Any]:
        """POST /config/validate endpoint"""
        return {
            "post": {
                "summary": "Validate Configuration",
                "description": "Validate a configuration without applying it.",
                "operationId": "validateConfig",
                "tags": ["Configuration"],
                "requestBody": {
                    "required": True,
                    "content": {
                        "application/json": {
                            "schema": {"$ref": "#/components/schemas/ConfigUpdateRequest"}
                        }
                    }
                },
                "responses": {
                    "200": {
                        "description": "Configuration is valid",
                        "content": {
                            "application/json": {
                                "schema": {"$ref": "#/components/schemas/ValidationResponse"}
                            }
                        }
                    },
                    "400": {
                        "description": "Configuration is invalid",
                        "content": {
                            "application/json": {
                                "schema": {"$ref": "#/components/schemas/ValidationErrorResponse"}
                            }
                        }
                    }
                }
            }
        }
    
    def _endpoint_cache(self) -> Dict[str, Any]:
        """GET /cache endpoint"""
        return {
            "get": {
                "summary": "List Cache Entries",
                "description": "List all cached fixes with statistics.",
                "operationId": "listCacheEntries",
                "tags": ["Cache"],
                "parameters": [
                    {
                        "name": "limit",
                        "in": "query",
                        "schema": {"type": "integer", "default": 100},
                        "description": "Maximum entries to return"
                    },
                    {
                        "name": "offset",
                        "in": "query",
                        "schema": {"type": "integer", "default": 0},
                        "description": "Offset for pagination"
                    }
                ],
                "responses": {
                    "200": {
                        "description": "Cache entries",
                        "content": {
                            "application/json": {
                                "schema": {"$ref": "#/components/schemas/CacheListResponse"}
                            }
                        }
                    }
                }
            }
        }
    
    def _endpoint_cache_entry(self) -> Dict[str, Any]:
        """GET /cache/{signature} endpoint"""
        return {
            "get": {
                "summary": "Get Cache Entry",
                "description": "Retrieve a specific cache entry by failure signature.",
                "operationId": "getCacheEntry",
                "tags": ["Cache"],
                "parameters": [
                    {
                        "name": "signature",
                        "in": "path",
                        "required": True,
                        "schema": {"type": "string"},
                        "description": "Failure signature"
                    }
                ],
                "responses": {
                    "200": {
                        "description": "Cache entry",
                        "content": {
                            "application/json": {
                                "schema": {"$ref": "#/components/schemas/CacheEntry"}
                            }
                        }
                    },
                    "404": {
                        "description": "Cache entry not found",
                        "content": {
                            "application/json": {
                                "schema": {"$ref": "#/components/schemas/ErrorResponse"}
                            }
                        }
                    }
                }
            },
            "delete": {
                "summary": "Delete Cache Entry",
                "description": "Remove a specific entry from the cache.",
                "operationId": "deleteCacheEntry",
                "tags": ["Cache"],
                "parameters": [
                    {
                        "name": "signature",
                        "in": "path",
                        "required": True,
                        "schema": {"type": "string"},
                        "description": "Failure signature"
                    }
                ],
                "responses": {
                    "204": {
                        "description": "Cache entry deleted"
                    },
                    "404": {
                        "description": "Cache entry not found",
                        "content": {
                            "application/json": {
                                "schema": {"$ref": "#/components/schemas/ErrorResponse"}
                            }
                        }
                    }
                }
            }
        }
    
    def _endpoint_cache_clear(self) -> Dict[str, Any]:
        """POST /cache/clear endpoint"""
        return {
            "post": {
                "summary": "Clear Cache",
                "description": "Remove all entries from the cache.",
                "operationId": "clearCache",
                "tags": ["Cache"],
                "responses": {
                    "200": {
                        "description": "Cache cleared",
                        "content": {
                            "application/json": {
                                "schema": {"$ref": "#/components/schemas/CacheClearResponse"}
                            }
                        }
                    }
                }
            }
        }
    
    def _endpoint_health_detailed(self) -> Dict[str, Any]:
        """GET /health/detailed endpoint"""
        return {
            "get": {
                "summary": "Detailed Health Status",
                "description": "Get comprehensive health information for all system components.",
                "operationId": "getHealthDetailed",
                "tags": ["Health"],
                "responses": {
                    "200": {
                        "description": "Detailed health status",
                        "content": {
                            "application/json": {
                                "schema": {"$ref": "#/components/schemas/DetailedHealthResponse"}
                            }
                        }
                    }
                }
            }
        }
    
    def _get_components(self) -> Dict[str, Any]:
        """API components (schemas, security schemes)"""
        return {
            "schemas": self._get_schemas(),
            "securitySchemes": self._get_security_schemes()
        }
    
    def _get_schemas(self) -> Dict[str, Any]:
        """API schemas"""
        return {
            "HealthCheckResponse": {
                "type": "object",
                "required": ["status", "timestamp", "components"],
                "properties": {
                    "status": {
                        "type": "string",
                        "enum": ["healthy", "degraded", "unhealthy"]
                    },
                    "timestamp": {"type": "string", "format": "date-time"},
                    "components": {
                        "type": "object",
                        "additionalProperties": {"type": "string"}
                    },
                    "latency_ms": {"type": "integer"}
                }
            },
            "ReadinessResponse": {
                "type": "object",
                "properties": {
                    "ready": {"type": "boolean"},
                    "missing_components": {
                        "type": "array",
                        "items": {"type": "string"}
                    }
                }
            },
            "HealingCycleRequest": {
                "type": "object",
                "required": ["failure_signature", "failure_context"],
                "properties": {
                    "failure_signature": {"type": "string"},
                    "failure_context": {"type": "object"},
                    "priority": {"type": "string", "enum": ["low", "normal", "high", "critical"]},
                    "auto_apply": {"type": "boolean"},
                    "max_retries": {"type": "integer", "minimum": 0}
                }
            },
            "FixResult": {
                "type": "object",
                "properties": {
                    "fix_id": {"type": "string"},
                    "status": {"type": "string", "enum": ["pending", "applied", "failed", "reverted"]},
                    "confidence_score": {"type": "number", "minimum": 0, "maximum": 1},
                    "execution_time_ms": {"type": "number"},
                    "error_message": {"type": "string"}
                }
            },
            "HealingCycleResponse": {
                "type": "object",
                "properties": {
                    "cycle_id": {"type": "string"},
                    "failure_signature": {"type": "string"},
                    "success": {"type": "boolean"},
                    "fix_result": {"$ref": "#/components/schemas/FixResult"},
                    "timestamp": {"type": "string", "format": "date-time"},
                    "cached": {"type": "boolean"}
                }
            },
            "MetricsResponse": {
                "type": "object",
                "properties": {
                    "total_cycles": {"type": "integer"},
                    "successful_cycles": {"type": "integer"},
                    "failed_cycles": {"type": "integer"},
                    "success_rate": {"type": "number"},
                    "cache_hit_rate": {"type": "number"},
                    "avg_latency_ms": {"type": "number"},
                    "peak_latency_ms": {"type": "number"},
                    "total_cost_dollars": {"type": "number"}
                }
            },
            "ConfigResponse": {
                "type": "object",
                "properties": {
                    "llm": {"type": "object"},
                    "healing": {"type": "object"},
                    "cache": {"type": "object"},
                    "modules": {"type": "object"}
                }
            },
            "ConfigUpdateRequest": {
                "type": "object",
                "properties": {
                    "llm": {"type": "object"},
                    "healing": {"type": "object"},
                    "cache": {"type": "object"},
                    "modules": {"type": "object"}
                }
            },
            "ValidationResponse": {
                "type": "object",
                "properties": {
                    "valid": {"type": "boolean"},
                    "errors": {
                        "type": "array",
                        "items": {"type": "string"}
                    }
                }
            },
            "ValidationErrorResponse": {
                "type": "object",
                "properties": {
                    "valid": {"type": "boolean"},
                    "errors": {
                        "type": "array",
                        "items": {"type": "object"}
                    }
                }
            },
            "CacheEntry": {
                "type": "object",
                "properties": {
                    "signature": {"type": "string"},
                    "fix": {"type": "object"},
                    "created_at": {"type": "string", "format": "date-time"},
                    "last_used": {"type": "string", "format": "date-time"},
                    "hit_count": {"type": "integer"},
                    "success_rate": {"type": "number"}
                }
            },
            "CacheListResponse": {
                "type": "object",
                "properties": {
                    "entries": {
                        "type": "array",
                        "items": {"$ref": "#/components/schemas/CacheEntry"}
                    },
                    "total_count": {"type": "integer"},
                    "limit": {"type": "integer"},
                    "offset": {"type": "integer"}
                }
            },
            "CacheClearResponse": {
                "type": "object",
                "properties": {
                    "cleared_count": {"type": "integer"},
                    "freed_memory_bytes": {"type": "integer"}
                }
            },
            "DetailedHealthResponse": {
                "type": "object",
                "properties": {
                    "overall_status": {"type": "string"},
                    "llm_provider": {"$ref": "#/components/schemas/ComponentHealth"},
                    "database": {"$ref": "#/components/schemas/ComponentHealth"},
                    "cache": {"$ref": "#/components/schemas/ComponentHealth"},
                    "metrics": {"$ref": "#/components/schemas/ComponentHealth"}
                }
            },
            "ComponentHealth": {
                "type": "object",
                "properties": {
                    "status": {"type": "string"},
                    "latency_ms": {"type": "number"},
                    "error_count": {"type": "integer"},
                    "last_error": {"type": "string"},
                    "uptime_percent": {"type": "number"}
                }
            },
            "ErrorResponse": {
                "type": "object",
                "properties": {
                    "error": {"type": "string"},
                    "message": {"type": "string"},
                    "details": {"type": "object"},
                    "timestamp": {"type": "string", "format": "date-time"}
                }
            }
        }
    
    def _get_security_schemes(self) -> Dict[str, Any]:
        """Security schemes"""
        return {
            "api_key": {
                "type": "apiKey",
                "in": "header",
                "name": "X-API-Key",
                "description": "API key for authentication"
            },
            "bearer": {
                "type": "http",
                "scheme": "bearer",
                "bearerFormat": "JWT",
                "description": "JWT token for authentication"
            }
        }
    
    def _get_tags(self) -> List[Dict[str, Any]]:
        """API tags for grouping endpoints"""
        return [
            {
                "name": "Health",
                "description": "Health and readiness checks"
            },
            {
                "name": "Healing",
                "description": "Healing cycle operations"
            },
            {
                "name": "Metrics",
                "description": "Metrics and statistics"
            },
            {
                "name": "Configuration",
                "description": "Configuration management"
            },
            {
                "name": "Cache",
                "description": "Cache management"
            }
        ]
    
    def get_spec(self) -> Dict[str, Any]:
        """Get complete OpenAPI specification"""
        return self.spec
    
    def get_spec_json(self) -> str:
        """Get specification as JSON string"""
        return json.dumps(self.spec, indent=2)
    
    def get_spec_yaml(self) -> str:
        """Get specification as YAML string"""
        try:
            import yaml
            return yaml.dump(self.spec, default_flow_style=False, sort_keys=False)
        except ImportError:
            return "PyYAML not installed. Install with: pip install pyyaml"


def generate_openapi_spec() -> Dict[str, Any]:
    """Generate and return Phoenix OpenAPI specification"""
    api = PhoenixOpenAPI()
    return api.get_spec()


if __name__ == "__main__":
    api = PhoenixOpenAPI()
    spec = api.get_spec_json()
    print(spec)
    
    # Save to file
    with open("phoenix_openapi.json", "w") as f:
        f.write(spec)
    print("\n✅ OpenAPI specification saved to phoenix_openapi.json")
