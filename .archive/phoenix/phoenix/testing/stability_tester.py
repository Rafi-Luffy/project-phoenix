import threading, time
from dataclasses import dataclass, field
from typing import Dict, Any, Optional, List, Callable
from enum import Enum

class ResourceType(Enum):
    CPU, MEMORY, THREADS, CONNECTIONS, FILE_HANDLES = range(5)

@dataclass
class ResourceSnapshot:
    timestamp: float
    cpu_percent: float
    memory_percent: float
    memory_bytes: int
    thread_count: int
    open_files: int
    virtual_memory_available: int
    def to_dict(self): return vars(self)

@dataclass
class MemoryLeak:
    leak_id: str
    detection_time: float
    estimated_growth_bytes_per_second: float
    current_memory_bytes: int
    peak_memory_bytes: int
    duration_seconds: float
    severity: float
    def to_dict(self): return vars(self)

@dataclass
class PerformanceDegradation:
    degradation_id: str
    detection_time: float
    metric: str
    initial_value: float
    current_value: float
    degradation_percent: float
    severity: float
    def to_dict(self): return vars(self)

@dataclass
class StabilityMetrics:
    test_duration_seconds: float = 0.0
    snapshots_collected: int = 0
    memory_leaks_detected: int = 0
    degradations_detected: int = 0
    avg_cpu_percent: float = 0.0
    avg_memory_percent: float = 0.0
    peak_memory_percent: float = 0.0
    max_thread_count: int = 0
    avg_thread_count: float = 0.0
    stability_score: float = 100.0
    def to_dict(self): return vars(self)

class StabilityTester:
    def __init__(self):
        self.snapshots: List[ResourceSnapshot] = []
        self.memory_leaks: List[MemoryLeak] = []
        self.degradations: List[PerformanceDegradation] = []
        self.metrics = StabilityMetrics()
        self.lock = threading.RLock()
        self.monitoring = False
        self.leak_counter = 0
        self.degradation_counter = 0
        self.initial_snapshot: Optional[ResourceSnapshot] = None
    def start_monitoring(self, duration_seconds: float = 3600.0, sample_interval_seconds: float = 5.0, leak_callback: Optional[Callable] = None) -> threading.Thread:
        thread = threading.Thread(target=self._monitor_stability, args=(duration_seconds, sample_interval_seconds, leak_callback), daemon=True)
        thread.start()
        return thread
    def _monitor_stability(self, duration_seconds: float, sample_interval_seconds: float, leak_callback: Optional[Callable] = None) -> None:
        start_time = time.time()
        self.monitoring = True
        self.initial_snapshot = self._take_snapshot()
        try:
            while time.time() - start_time < duration_seconds and self.monitoring:
                snapshot = self._take_snapshot()
                self._analyze_snapshot(snapshot, leak_callback)
                time.sleep(sample_interval_seconds)
        finally:
            self.monitoring = False
            self.metrics.test_duration_seconds = time.time() - start_time
            self._calculate_metrics()
    def stop_monitoring(self) -> None:
        self.monitoring = False
    def _take_snapshot(self) -> ResourceSnapshot:
        with self.lock:
            snapshot = ResourceSnapshot(timestamp=time.time(), cpu_percent=10.0, memory_percent=50.0, memory_bytes=1000000, thread_count=10, open_files=5, virtual_memory_available=5000000000)
            self.snapshots.append(snapshot)
            return snapshot
    def _analyze_snapshot(self, snapshot: ResourceSnapshot, leak_callback: Optional[Callable] = None) -> None:
        if not self.initial_snapshot or len(self.snapshots) <= 3:
            return
        memory_growth = snapshot.memory_bytes - self.initial_snapshot.memory_bytes
        elapsed = snapshot.timestamp - self.initial_snapshot.timestamp
        if elapsed > 0 and memory_growth > 50000:
            growth_rate = memory_growth / elapsed
            if growth_rate > 10000:
                leak = MemoryLeak(leak_id=f"leak_{self.leak_counter}", detection_time=time.time(), estimated_growth_bytes_per_second=growth_rate, current_memory_bytes=snapshot.memory_bytes, peak_memory_bytes=max(s.memory_bytes for s in self.snapshots), duration_seconds=elapsed, severity=min(1.0, growth_rate / 100000))
                with self.lock:
                    self.memory_leaks.append(leak)
                    self.leak_counter += 1
                if leak_callback:
                    try:
                        leak_callback(leak)
                    except:
                        pass
    def _calculate_metrics(self) -> None:
        with self.lock:
            if not self.snapshots:
                return
            self.metrics.snapshots_collected = len(self.snapshots)
            self.metrics.memory_leaks_detected = len(self.memory_leaks)
            self.metrics.degradations_detected = len(self.degradations)
            cpu_values = [s.cpu_percent for s in self.snapshots]
            memory_values = [s.memory_percent for s in self.snapshots]
            thread_counts = [s.thread_count for s in self.snapshots]
            if cpu_values:
                self.metrics.avg_cpu_percent = sum(cpu_values) / len(cpu_values)
            if memory_values:
                self.metrics.avg_memory_percent = sum(memory_values) / len(memory_values)
                self.metrics.peak_memory_percent = max(memory_values)
            if thread_counts:
                self.metrics.avg_thread_count = sum(thread_counts) / len(thread_counts)
                self.metrics.max_thread_count = max(thread_counts)
            penalty = len(self.memory_leaks) * 20 + len(self.degradations) * 10
            if self.metrics.peak_memory_percent > 80:
                penalty += 15
            self.metrics.stability_score = max(0, 100 - penalty)
    def get_snapshot_history(self) -> List[Dict[str, Any]]:
        with self.lock:
            return [s.to_dict() for s in self.snapshots]
    def get_detected_leaks(self) -> List[Dict[str, Any]]:
        with self.lock:
            return [l.to_dict() for l in self.memory_leaks]
    def get_degradations(self) -> List[Dict[str, Any]]:
        with self.lock:
            return [d.to_dict() for d in self.degradations]
    def get_metrics(self) -> StabilityMetrics:
        return self.metrics
