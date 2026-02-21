import threading, time
from concurrent.futures import ThreadPoolExecutor, as_completed
from dataclasses import dataclass, field
from enum import Enum
from typing import Dict, Any, Optional, Callable, List, Tuple

class LoadPattern(Enum):
    CONSTANT = "constant"
    RAMP_UP = "ramp_up"
    SPIKE = "spike"
    WAVE = "wave"
    RANDOM = "random"

@dataclass
class LoadResult:
    request_id: str
    thread_id: int
    started_at: float
    completed_at: float
    success: bool
    response_time_ms: float
    status_code: Optional[int] = None
    error: Optional[str] = None
    def to_dict(self): return vars(self)

@dataclass
class LoadPhase:
    phase_num: int
    duration_seconds: float
    concurrent_users: int
    requests_per_user: int
    start_time: Optional[float] = None
    end_time: Optional[float] = None
    completed_requests: int = 0
    failed_requests: int = 0
    total_response_time_ms: float = 0.0
    def is_running(self): return self.start_time and time.time() - self.start_time < self.duration_seconds
    def avg_response_time_ms(self): return self.total_response_time_ms / self.completed_requests if self.completed_requests else 0.0
    def success_rate(self): return (self.completed_requests / (self.completed_requests + self.failed_requests) * 100) if (self.completed_requests + self.failed_requests) else 0.0
    def to_dict(self): return vars(self)

@dataclass
class LoadMetrics:
    total_requests: int = 0
    successful_requests: int = 0
    failed_requests: int = 0
    min_response_time_ms: float = float('inf')
    max_response_time_ms: float = 0.0
    avg_response_time_ms: float = 0.0
    p50_response_time_ms: float = 0.0
    p95_response_time_ms: float = 0.0
    p99_response_time_ms: float = 0.0
    throughput_requests_per_second: float = 0.0
    test_duration_seconds: float = 0.0
    def success_rate(self): return (self.successful_requests / self.total_requests * 100) if self.total_requests else 0.0
    def to_dict(self): return vars(self)

class LoadTester:
    def __init__(self):
        self.results: List[LoadResult] = []
        self.phases: List[LoadPhase] = []
        self.metrics = LoadMetrics()
        self.lock = threading.RLock()
        self.request_counter = 0
    def add_phase(self, duration_seconds: float, concurrent_users: int, requests_per_user: int) -> LoadPhase:
        with self.lock:
            phase = LoadPhase(phase_num=len(self.phases) + 1, duration_seconds=duration_seconds, concurrent_users=concurrent_users, requests_per_user=requests_per_user)
            self.phases.append(phase)
            return phase
    def run_load_test(self, test_function: Callable, pattern: LoadPattern = LoadPattern.CONSTANT) -> LoadMetrics:
        test_start = time.time()
        for phase in self.phases:
            self._run_phase(phase, test_function, pattern)
        test_duration = time.time() - test_start
        self._calculate_metrics(test_duration)
        return self.metrics
    def _run_phase(self, phase: LoadPhase, test_function: Callable, pattern: LoadPattern) -> None:
        phase.start_time = time.time()
        with ThreadPoolExecutor(max_workers=min(phase.concurrent_users, 10)) as executor:
            futures = []
            request_count = 0
            total_requests = min(phase.concurrent_users * phase.requests_per_user, 20)
            for i in range(total_requests):
                future = executor.submit(self._execute_request, test_function)
                futures.append(future)
                request_count += 1
                time.sleep(0.05)
            for future in as_completed(futures):
                try:
                    result = future.result(timeout=10)
                    if result:
                        self.results.append(result)
                        with self.lock:
                            phase.completed_requests += 1 if result.success else 0
                            phase.failed_requests += 0 if result.success else 1
                            phase.total_response_time_ms += result.response_time_ms
                except Exception:
                    with self.lock:
                        phase.failed_requests += 1
        phase.end_time = time.time()
    def _execute_request(self, test_function: Callable) -> Optional[LoadResult]:
        with self.lock:
            self.request_counter += 1
            request_id = str(self.request_counter)
        thread_id = threading.get_ident()
        started_at = time.time()
        try:
            success, response_time_ms, error = test_function(int(request_id))
            result = LoadResult(request_id=request_id, thread_id=thread_id, started_at=started_at, completed_at=time.time(), success=success, response_time_ms=response_time_ms, error=error)
            return result
        except Exception as e:
            return LoadResult(request_id=request_id, thread_id=thread_id, started_at=started_at, completed_at=time.time(), success=False, response_time_ms=time.time() - started_at, error=str(e))
    def _calculate_metrics(self, test_duration: float) -> None:
        with self.lock:
            if not self.results:
                return
            self.metrics.total_requests = len(self.results)
            self.metrics.successful_requests = sum(1 for r in self.results if r.success)
            self.metrics.failed_requests = sum(1 for r in self.results if not r.success)
            self.metrics.test_duration_seconds = test_duration
            response_times = sorted([r.response_time_ms for r in self.results])
            if response_times:
                self.metrics.min_response_time_ms = min(response_times)
                self.metrics.max_response_time_ms = max(response_times)
                self.metrics.avg_response_time_ms = sum(response_times) / len(response_times)
                self.metrics.p50_response_time_ms = response_times[int(len(response_times) * 0.50)]
                self.metrics.p95_response_time_ms = response_times[int(len(response_times) * 0.95)]
                self.metrics.p99_response_time_ms = response_times[int(len(response_times) * 0.99)]
            if test_duration > 0:
                self.metrics.throughput_requests_per_second = self.metrics.total_requests / test_duration
    def get_phase_results(self, phase_num: int) -> Dict[str, Any]:
        with self.lock:
            return self.phases[phase_num].to_dict() if 0 <= phase_num < len(self.phases) else {}
    def get_results_summary(self) -> Dict[str, Any]:
        with self.lock:
            return {"total_phases": len(self.phases), "phase_results": [p.to_dict() for p in self.phases], "metrics": self.metrics.to_dict()}
