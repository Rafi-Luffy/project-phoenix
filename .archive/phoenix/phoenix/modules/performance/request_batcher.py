"""
Request Batching System

Optimize throughput by batching multiple requests:
- Intelligent batching based on request type and size
- Automatic batch execution
- Fallback for timeout or size limits
- Cost optimization through batch processing
"""

import asyncio
from typing import Any, Dict, List, Optional, Callable, Coroutine
from dataclasses import dataclass
from datetime import datetime
from enum import Enum
import json


class BatchStrategy(Enum):
    """Batching strategies"""
    SIZE_BASED = "size"       # Batch when size limit reached
    TIME_BASED = "time"       # Batch when time limit reached
    HYBRID = "hybrid"          # Combine size and time limits
    ADAPTIVE = "adaptive"      # Adapt based on request patterns


@dataclass
class BatchedRequest:
    """Represents a request to be batched"""
    request_id: str
    payload: Any
    future: asyncio.Future
    created_at: datetime
    priority: int = 0
    estimated_size: int = 0


class RequestBatcher:
    """Batch multiple requests for efficient processing"""
    
    def __init__(
        self,
        processor: Callable[[List[Any]], Coroutine],
        strategy: BatchStrategy = BatchStrategy.HYBRID,
        max_batch_size: int = 100,
        max_batch_bytes: int = 1024 * 1024,  # 1MB
        batch_timeout_ms: int = 100,
        min_batch_size: int = 1
    ):
        self.processor = processor
        self.strategy = strategy
        self.max_batch_size = max_batch_size
        self.max_batch_bytes = max_batch_bytes
        self.batch_timeout_ms = batch_timeout_ms
        self.min_batch_size = min_batch_size
        
        self.queue: List[BatchedRequest] = []
        self.processing = False
        self.stats = {
            "total_requests": 0,
            "total_batches": 0,
            "avg_batch_size": 0,
            "total_cost_saved": 0.0
        }
        self._lock = asyncio.Lock()
        self._event = asyncio.Event()
    
    async def add_request(
        self,
        request_id: str,
        payload: Any,
        priority: int = 0
    ) -> Any:
        """Add request to batch queue"""
        future = asyncio.Future()
        
        # Estimate size
        try:
            estimated_size = len(json.dumps(payload))
        except:
            estimated_size = len(str(payload))
        
        request = BatchedRequest(
            request_id=request_id,
            payload=payload,
            future=future,
            created_at=datetime.now(),
            priority=priority,
            estimated_size=estimated_size
        )
        
        async with self._lock:
            self.queue.append(request)
            self.stats["total_requests"] += 1
            
            # Check if batch should be processed
            if self._should_process_batch():
                self._event.set()
        
        # Start processor if not running
        if not self.processing:
            asyncio.create_task(self._process_batches())
        
        return await future
    
    def _should_process_batch(self) -> bool:
        """Determine if batch should be processed"""
        if len(self.queue) < self.min_batch_size:
            return False
        
        if self.strategy == BatchStrategy.SIZE_BASED:
            return len(self.queue) >= self.max_batch_size
        
        elif self.strategy == BatchStrategy.TIME_BASED:
            if not self.queue:
                return False
            elapsed_ms = (datetime.now() - self.queue[0].created_at).total_seconds() * 1000
            return elapsed_ms >= self.batch_timeout_ms
        
        elif self.strategy == BatchStrategy.HYBRID:
            if len(self.queue) >= self.max_batch_size:
                return True
            if not self.queue:
                return False
            total_bytes = sum(r.estimated_size for r in self.queue)
            if total_bytes >= self.max_batch_bytes:
                return True
            elapsed_ms = (datetime.now() - self.queue[0].created_at).total_seconds() * 1000
            return elapsed_ms >= self.batch_timeout_ms
        
        elif self.strategy == BatchStrategy.ADAPTIVE:
            # Adaptive: if queue is growing, batch more aggressively
            if len(self.queue) >= self.max_batch_size * 0.5:
                return True
            if not self.queue:
                return False
            elapsed_ms = (datetime.now() - self.queue[0].created_at).total_seconds() * 1000
            return elapsed_ms >= self.batch_timeout_ms * 0.5
        
        return False
    
    async def _process_batches(self):
        """Process batches continuously"""
        self.processing = True
        
        try:
            while True:
                # Wait for batch trigger or timeout
                try:
                    await asyncio.wait_for(self._event.wait(), timeout=self.batch_timeout_ms / 1000)
                    self._event.clear()
                except asyncio.TimeoutError:
                    pass
                
                async with self._lock:
                    if self._should_process_batch():
                        await self._execute_batch()
                    elif not self.queue:
                        self.processing = False
                        break
        except Exception as e:
            print(f"Batch processor error: {e}")
            self.processing = False
    
    async def _execute_batch(self):
        """Execute a batch of requests"""
        if not self.queue:
            return
        
        # Sort by priority (higher priority first)
        self.queue.sort(key=lambda r: (-r.priority, r.created_at))
        
        # Take batch
        batch = self.queue[:self.max_batch_size]
        self.queue = self.queue[self.max_batch_size:]
        
        # Process batch
        payloads = [r.payload for r in batch]
        
        try:
            results = await self.processor(payloads)
            
            # Distribute results
            if isinstance(results, list):
                for request, result in zip(batch, results):
                    request.future.set_result(result)
            else:
                # Single result for all
                for request in batch:
                    request.future.set_result(results)
            
            # Update stats
            self.stats["total_batches"] += 1
            if self.stats["total_batches"] > 0:
                total_requests = self.stats["total_requests"]
                self.stats["avg_batch_size"] = total_requests / self.stats["total_batches"]
                # Estimate 30% cost savings through batching
                self.stats["total_cost_saved"] = total_requests * 0.30
        
        except Exception as e:
            # Set exception on all futures
            for request in batch:
                request.future.set_exception(e)
    
    async def flush(self) -> int:
        """Force process remaining requests"""
        async with self._lock:
            while self.queue:
                await self._execute_batch()
        
        return self.stats["total_requests"]
    
    def get_stats(self) -> Dict[str, Any]:
        """Get batching statistics"""
        return self.stats.copy()


class AdaptiveBatcher:
    """Adapts batching parameters based on system load"""
    
    def __init__(self, batcher: RequestBatcher):
        self.batcher = batcher
        self.load_history: List[int] = []
        self.max_history = 100
    
    async def adjust_parameters(self):
        """Adjust batching parameters based on load"""
        queue_size = len(self.batcher.queue)
        self.load_history.append(queue_size)
        
        if len(self.load_history) > self.max_history:
            self.load_history = self.load_history[-self.max_history:]
        
        avg_load = sum(self.load_history) / len(self.load_history)
        
        # Adjust timeout based on load
        if avg_load > self.batcher.max_batch_size * 0.75:
            # High load: reduce timeout
            self.batcher.batch_timeout_ms = max(10, self.batcher.batch_timeout_ms // 2)
        elif avg_load < self.batcher.max_batch_size * 0.25:
            # Low load: increase timeout
            self.batcher.batch_timeout_ms = min(500, self.batcher.batch_timeout_ms * 2)
    
    def get_load_metrics(self) -> Dict[str, float]:
        """Get current load metrics"""
        if not self.load_history:
            return {"current_load": 0, "avg_load": 0, "peak_load": 0}
        
        return {
            "current_load": self.load_history[-1],
            "avg_load": sum(self.load_history) / len(self.load_history),
            "peak_load": max(self.load_history),
            "min_load": min(self.load_history)
        }


class BatchCostAnalyzer:
    """Analyze cost savings from batching"""
    
    def __init__(self, cost_per_request: float = 0.001):
        self.cost_per_request = cost_per_request
        self.request_history: List[Dict[str, Any]] = []
    
    def record_batch(self, batch_size: int, cost_per_batch: float):
        """Record batch execution"""
        # Estimated cost without batching
        cost_without_batching = batch_size * self.cost_per_request
        savings = cost_without_batching - cost_per_batch
        savings_percent = (savings / cost_without_batching * 100) if cost_without_batching > 0 else 0
        
        self.request_history.append({
            "batch_size": batch_size,
            "cost_per_batch": cost_per_batch,
            "cost_without_batching": cost_without_batching,
            "savings": savings,
            "savings_percent": savings_percent,
            "timestamp": datetime.now()
        })
    
    def get_cost_summary(self) -> Dict[str, Any]:
        """Get cost savings summary"""
        if not self.request_history:
            return {"total_savings": 0, "avg_savings_percent": 0, "batches": 0}
        
        total_requests = sum(h["batch_size"] for h in self.request_history)
        total_savings = sum(h["savings"] for h in self.request_history)
        avg_savings_percent = sum(h["savings_percent"] for h in self.request_history) / len(self.request_history)
        
        return {
            "total_batches": len(self.request_history),
            "total_requests": total_requests,
            "total_savings_usd": total_savings,
            "avg_savings_percent": avg_savings_percent,
            "avg_batch_size": total_requests / len(self.request_history)
        }


if __name__ == "__main__":
    async def test_batching():
        # Define batch processor
        async def process_batch(payloads):
            # Simulate processing
            results = [{"processed": True, "input": p} for p in payloads]
            return results
        
        # Create batcher
        batcher = RequestBatcher(
            processor=process_batch,
            strategy=BatchStrategy.HYBRID,
            max_batch_size=10,
            batch_timeout_ms=100
        )
        
        # Add requests
        for i in range(25):
            result = await batcher.add_request(f"req-{i}", {"data": f"request-{i}"})
            print(f"Request {i} sent")
        
        # Flush remaining
        await batcher.flush()
        
        # Print stats
        print(f"Stats: {batcher.get_stats()}")
    
    asyncio.run(test_batching())
