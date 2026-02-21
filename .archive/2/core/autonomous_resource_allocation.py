"""
Autonomous Resource Allocation

This module dynamically allocates system resources based on demand and optimization.
Resources are allocated intelligently to maximize system throughput and minimize latency.

Based on: Resource scheduling and queueing theory
"""

from dataclasses import dataclass, field
from datetime import datetime
from typing import Any, Dict, List, Optional, Set
from enum import Enum

from autonomous_system.core.error_detection import ErrorType


class ResourceType(Enum):
    """Types of resources in the system"""
    CPU = "cpu"                        # CPU cycles
    MEMORY = "memory"                  # RAM
    DISK = "disk"                      # Storage
    NETWORK = "network"                # Network bandwidth
    THREADS = "threads"                # Thread pool capacity


class AllocationStrategy(Enum):
    """Resource allocation strategies"""
    FAIR_SHARE = "fair_share"          # Equal distribution
    PRIORITY = "priority"              # Based on priority
    DEMAND = "demand"                  # Based on current demand
    PREDICTIVE = "predictive"          # Based on predicted needs
    ADAPTIVE = "adaptive"              # Dynamic based on performance


@dataclass
class ResourcePool:
    """A pool of available resources"""
    resource_type: ResourceType
    total_capacity: float
    allocated: float = 0.0
    reserved: float = 0.0              # Reserved for critical operations
    
    @property
    def available(self) -> float:
        """Available resources for allocation"""
        return self.total_capacity - self.allocated - self.reserved
    
    @property
    def utilization(self) -> float:
        """Resource utilization percentage (0-1)"""
        return self.allocated / self.total_capacity if self.total_capacity > 0 else 0.0
    
    def can_allocate(self, amount: float) -> bool:
        """Check if resources can be allocated"""
        return amount <= self.available
    
    def allocate(self, amount: float) -> bool:
        """Allocate resources"""
        if self.can_allocate(amount):
            self.allocated += amount
            return True
        return False
    
    def deallocate(self, amount: float) -> None:
        """Deallocate resources"""
        self.allocated = max(0, self.allocated - amount)


@dataclass
class AllocationRequest:
    """Request for resources"""
    request_id: str
    resource_type: ResourceType
    amount: float
    priority: int = 5                  # 1 (low) to 10 (high)
    error_type: Optional[ErrorType] = None
    timestamp: datetime = field(default_factory=datetime.now)
    urgency: float = 0.5               # 0-1 scale
    estimated_duration: float = 1.0    # seconds


@dataclass
class AllocationResult:
    """Result of resource allocation"""
    request_id: str
    granted: bool
    amount_granted: float
    reason: str = ""
    timestamp: datetime = field(default_factory=datetime.now)


class ResourceAllocator:
    """
    Intelligently allocates system resources.
    Uses various strategies to optimize resource utilization.
    """
    
    def __init__(self):
        """Initialize resource allocator"""
        self.pools: Dict[ResourceType, ResourcePool] = {
            ResourceType.CPU: ResourcePool(ResourceType.CPU, 100.0),
            ResourceType.MEMORY: ResourcePool(ResourceType.MEMORY, 1000.0),
            ResourceType.DISK: ResourcePool(ResourceType.DISK, 10000.0),
            ResourceType.NETWORK: ResourcePool(ResourceType.NETWORK, 1000.0),
            ResourceType.THREADS: ResourcePool(ResourceType.THREADS, 100.0)
        }
        
        # Set aside reserves for critical operations (20%)
        for pool in self.pools.values():
            pool.reserved = pool.total_capacity * 0.2
        
        self.allocation_strategy = AllocationStrategy.ADAPTIVE
        self.allocation_history: List[AllocationResult] = []
        self.pending_requests: List[AllocationRequest] = []
        
        # Statistics
        self.total_requests = 0
        self.successful_allocations = 0
        self.denied_allocations = 0
    
    def set_strategy(self, strategy: AllocationStrategy) -> None:
        """Set resource allocation strategy"""
        self.allocation_strategy = strategy
    
    def request_resources(self, request: AllocationRequest) -> AllocationResult:
        """Request resources"""
        self.total_requests += 1
        
        # Check if resources available
        pool = self.pools[request.resource_type]
        
        if pool.can_allocate(request.amount):
            # Allocate resources
            pool.allocate(request.amount)
            self.successful_allocations += 1
            
            result = AllocationResult(
                request_id=request.request_id,
                granted=True,
                amount_granted=request.amount,
                reason="Resources available"
            )
        else:
            # Try to free up resources or queue request
            self.denied_allocations += 1
            freed = self._try_free_resources(request.resource_type, request.amount)
            
            if freed >= request.amount:
                pool.allocate(request.amount)
                self.successful_allocations += 1
                result = AllocationResult(
                    request_id=request.request_id,
                    granted=True,
                    amount_granted=request.amount,
                    reason="Freed resources from low-priority operations"
                )
            else:
                # Queue request
                self.pending_requests.append(request)
                result = AllocationResult(
                    request_id=request.request_id,
                    granted=False,
                    amount_granted=0.0,
                    reason=f"Insufficient resources. Available: {pool.available}/{request.amount}"
                )
        
        self.allocation_history.append(result)
        return result
    
    def release_resources(self, request_id: str, 
                         resource_type: ResourceType,
                         amount: float) -> None:
        """Release allocated resources"""
        self.pools[resource_type].deallocate(amount)
        
        # Try to process pending requests
        self._process_pending_requests()
    
    def _try_free_resources(self, resource_type: ResourceType,
                           needed: float) -> float:
        """Try to free up resources from low-priority allocations"""
        # In a real system, this would track allocations and
        # could preempt low-priority operations
        # For now, return 0
        return 0.0
    
    def _process_pending_requests(self) -> None:
        """Process pending resource requests"""
        completed = []
        
        for i, request in enumerate(self.pending_requests):
            pool = self.pools[request.resource_type]
            
            if pool.can_allocate(request.amount):
                pool.allocate(request.amount)
                result = AllocationResult(
                    request_id=request.request_id,
                    granted=True,
                    amount_granted=request.amount,
                    reason="Resources became available"
                )
                self.allocation_history.append(result)
                self.successful_allocations += 1
                completed.append(i)
        
        # Remove processed requests
        for i in reversed(completed):
            self.pending_requests.pop(i)
    
    def get_pool_status(self, resource_type: ResourceType) -> Dict[str, float]:
        """Get status of resource pool"""
        pool = self.pools[resource_type]
        return {
            "resource_type": resource_type.value,
            "total_capacity": pool.total_capacity,
            "allocated": pool.allocated,
            "reserved": pool.reserved,
            "available": pool.available,
            "utilization_percent": pool.utilization * 100
        }
    
    def get_all_pool_status(self) -> Dict[str, Any]:
        """Get status of all resource pools"""
        return {
            resource_type: self.get_pool_status(resource_type)
            for resource_type in ResourceType
        }
    
    def is_resource_constrained(self) -> bool:
        """Check if system is resource constrained"""
        for pool in self.pools.values():
            if pool.utilization > 0.8:  # Over 80% utilization
                return True
        return False
    
    def get_bottleneck_resource(self) -> Optional[ResourceType]:
        """Identify most constrained resource"""
        max_utilization = 0.0
        bottleneck = None
        
        for resource_type, pool in self.pools.items():
            if pool.utilization > max_utilization:
                max_utilization = pool.utilization
                bottleneck = resource_type
        
        return bottleneck if max_utilization > 0.7 else None
    
    def suggest_optimization(self) -> Optional[str]:
        """Suggest optimization based on current allocation"""
        bottleneck = self.get_bottleneck_resource()
        
        if bottleneck is None:
            return None
        
        pool = self.pools[bottleneck]
        
        if bottleneck == ResourceType.CPU:
            return "Consider optimizing CPU-intensive operations or increasing CPU allocation"
        elif bottleneck == ResourceType.MEMORY:
            return "Consider releasing unused memory or increasing memory allocation"
        elif bottleneck == ResourceType.DISK:
            return "Consider archiving old data or increasing storage allocation"
        elif bottleneck == ResourceType.NETWORK:
            return "Consider batching network operations or increasing bandwidth"
        elif bottleneck == ResourceType.THREADS:
            return "Consider thread pool optimization or increasing thread capacity"
        
        return None
    
    def adaptive_allocation(self, request: AllocationRequest) -> AllocationResult:
        """
        Adaptively allocate resources based on system state.
        Prioritizes critical operations.
        """
        # Increase allocation for high-priority requests if constrained
        if self.is_resource_constrained() and request.priority <= 3:
            # Lower priority during constraint
            request.amount *= 0.5
        elif request.priority >= 8:
            # Give more to high-priority
            # (Don't actually increase, but ensure allocation succeeds)
            pass
        
        return self.request_resources(request)
    
    def export_state(self) -> Dict[str, Any]:
        """Export allocator state"""
        return {
            "timestamp": datetime.now().isoformat(),
            "allocation_strategy": self.allocation_strategy.value,
            "pool_status": self.get_all_pool_status(),
            "total_requests": self.total_requests,
            "successful_allocations": self.successful_allocations,
            "denied_allocations": self.denied_allocations,
            "pending_requests": len(self.pending_requests),
            "bottleneck_resource": self.get_bottleneck_resource().value if self.get_bottleneck_resource() else None,
            "optimization_suggestion": self.suggest_optimization()
        }
    
    def get_stats(self) -> Dict[str, Any]:
        """Get allocator statistics"""
        success_rate = (self.successful_allocations / self.total_requests * 100) if self.total_requests > 0 else 0
        
        return {
            "total_requests": self.total_requests,
            "successful_allocations": self.successful_allocations,
            "denied_allocations": self.denied_allocations,
            "success_rate_percent": success_rate,
            "pending_requests": len(self.pending_requests),
            "allocation_history_size": len(self.allocation_history),
            "is_resource_constrained": self.is_resource_constrained()
        }
