"""
Metrics Framework - Module 5.1

Performance measurement system, A/B testing infrastructure,
statistical significance testing, benchmark dataset creation,
and automated evaluation pipeline.
"""

import json
import time
import statistics
import threading
from dataclasses import dataclass, field
from enum import Enum
from typing import Any, Dict, List, Optional, Tuple, Callable
from datetime import datetime, timedelta
from collections import defaultdict
import math


class MetricType(Enum):
    """Types of metrics to track"""
    ACCURACY = "accuracy"
    LATENCY = "latency"
    THROUGHPUT = "throughput"
    ERROR_RATE = "error_rate"
    RESOURCE_USAGE = "resource_usage"
    AVAILABILITY = "availability"
    SUCCESS_RATE = "success_rate"
    CUSTOM = "custom"


class VariantType(Enum):
    """Types of variants in A/B testing"""
    CONTROL = "control"
    TREATMENT = "treatment"
    VARIANT_A = "variant_a"
    VARIANT_B = "variant_b"


@dataclass
class MetricSample:
    """Single measurement sample"""
    metric_type: MetricType
    value: float
    timestamp: float = field(default_factory=time.time)
    metadata: Dict[str, Any] = field(default_factory=dict)
    sample_id: str = ""


@dataclass
class MetricSnapshot:
    """Aggregate metrics at point in time"""
    timestamp: float
    metrics: Dict[MetricType, float]
    additional_data: Dict[str, Any] = field(default_factory=dict)


@dataclass
class ExperimentConfig:
    """Configuration for A/B testing experiment"""
    experiment_id: str
    name: str
    control_variant: str
    treatment_variant: str
    start_time: float = field(default_factory=time.time)
    end_time: Optional[float] = None
    sample_size_required: int = 100
    significance_level: float = 0.05  # 5% alpha
    min_detectable_effect: float = 0.1  # 10% difference
    metrics_to_track: List[MetricType] = field(default_factory=list)


@dataclass
class BenchmarkDataset:
    """Dataset for benchmarking"""
    dataset_id: str
    name: str
    task_type: str
    samples: List[Dict[str, Any]] = field(default_factory=list)
    expected_outputs: List[Any] = field(default_factory=list)
    difficulty_level: str = "medium"  # easy, medium, hard
    created_at: float = field(default_factory=time.time)


class MetricsCollector:
    """Collects and aggregates metrics"""

    def __init__(self):
        self.metrics: Dict[MetricType, List[MetricSample]] = defaultdict(list)
        self.snapshots: List[MetricSnapshot] = []
        self.lock = threading.RLock()

    def record_metric(self, sample: MetricSample):
        """Record metric sample"""
        with self.lock:
            self.metrics[sample.metric_type].append(sample)

    def record_metrics_batch(self, samples: List[MetricSample]):
        """Record multiple metric samples"""
        with self.lock:
            for sample in samples:
                self.metrics[sample.metric_type].append(sample)

    def get_metric_statistics(self, metric_type: MetricType) -> Dict[str, float]:
        """Get statistics for metric type"""
        with self.lock:
            samples = self.metrics[metric_type]
            if not samples:
                return {}

            values = [s.value for s in samples]
            return {
                "count": len(values),
                "mean": statistics.mean(values),
                "median": statistics.median(values),
                "stdev": statistics.stdev(values) if len(values) > 1 else 0.0,
                "min": min(values),
                "max": max(values),
                "p95": self._percentile(values, 0.95),
                "p99": self._percentile(values, 0.99)
            }

    def take_snapshot(self) -> MetricSnapshot:
        """Take snapshot of current metrics"""
        with self.lock:
            snapshot_metrics = {}

            for metric_type in MetricType:
                stats = self.get_metric_statistics(metric_type)
                if stats:
                    snapshot_metrics[metric_type] = stats.get("mean", 0.0)

            snapshot = MetricSnapshot(
                timestamp=time.time(),
                metrics=snapshot_metrics
            )
            self.snapshots.append(snapshot)
            return snapshot

    @staticmethod
    def _percentile(data: List[float], percentile: float) -> float:
        """Calculate percentile of data"""
        sorted_data = sorted(data)
        index = int((percentile * len(sorted_data)))
        return sorted_data[min(index, len(sorted_data) - 1)]

    def clear_old_metrics(self, age_seconds: float = 3600):
        """Clear metrics older than specified seconds"""
        with self.lock:
            cutoff_time = time.time() - age_seconds

            for metric_type in self.metrics:
                self.metrics[metric_type] = [
                    s for s in self.metrics[metric_type]
                    if s.timestamp > cutoff_time
                ]


class ABTestingFramework:
    """Framework for A/B testing"""

    def __init__(self):
        self.experiments: Dict[str, ExperimentConfig] = {}
        self.experiment_results: Dict[str, Dict[str, Any]] = {}
        self.variant_metrics: Dict[str, Dict[str, List[float]]] = defaultdict(
            lambda: defaultdict(list)
        )
        self.lock = threading.RLock()

    def create_experiment(self, config: ExperimentConfig) -> bool:
        """Create new A/B test experiment"""
        with self.lock:
            if config.experiment_id in self.experiments:
                return False

            self.experiments[config.experiment_id] = config
            self.experiment_results[config.experiment_id] = {
                "status": "running",
                "control_metrics": {},
                "treatment_metrics": {},
                "statistical_test": None,
                "result": None,
                "winner": None
            }
            return True

    def record_variant_metric(self, experiment_id: str, variant: str,
                             metric_type: MetricType, value: float):
        """Record metric for variant"""
        with self.lock:
            key = f"{experiment_id}_{variant}_{metric_type.value}"
            self.variant_metrics[key].append(value)

    def check_statistical_significance(self, experiment_id: str) -> Optional[Dict[str, Any]]:
        """Check if results are statistically significant"""
        with self.lock:
            if experiment_id not in self.experiments:
                return None

            config = self.experiments[experiment_id]
            results = self.experiment_results[experiment_id]

            # Collect metrics for both variants
            control_values = []
            treatment_values = []

            for metric_type in config.metrics_to_track:
                control_key = f"{experiment_id}_{config.control_variant}_{metric_type.value}"
                treatment_key = f"{experiment_id}_{config.treatment_variant}_{metric_type.value}"

                control_values.extend(self.variant_metrics.get(control_key, []))
                treatment_values.extend(self.variant_metrics.get(treatment_key, []))

            if not control_values or not treatment_values:
                return None

            # Perform t-test
            control_mean = statistics.mean(control_values)
            treatment_mean = statistics.mean(treatment_values)

            control_std = (statistics.stdev(control_values)
                          if len(control_values) > 1 else 0.0)
            treatment_std = (statistics.stdev(treatment_values)
                            if len(treatment_values) > 1 else 0.0)

            # Calculate effect size and p-value
            effect_size = abs(treatment_mean - control_mean) / control_mean if control_mean != 0 else 0.0

            # Simplified t-test (for demonstration)
            t_statistic = self._calculate_t_statistic(
                control_values,
                treatment_values,
                control_std,
                treatment_std
            )

            # Check significance
            significant = effect_size >= config.min_detectable_effect

            results["control_metrics"] = {
                "mean": control_mean,
                "stdev": control_std,
                "samples": len(control_values)
            }
            results["treatment_metrics"] = {
                "mean": treatment_mean,
                "stdev": treatment_std,
                "samples": len(treatment_values)
            }
            results["effect_size"] = effect_size
            results["t_statistic"] = t_statistic
            results["significant"] = significant

            if significant:
                results["winner"] = (config.treatment_variant
                                    if treatment_mean > control_mean
                                    else config.control_variant)

            return results

    def end_experiment(self, experiment_id: str) -> Optional[Dict[str, Any]]:
        """End experiment and finalize results"""
        with self.lock:
            if experiment_id not in self.experiments:
                return None

            config = self.experiments[experiment_id]
            config.end_time = time.time()

            self.experiment_results[experiment_id]["status"] = "completed"

            return self.check_statistical_significance(experiment_id)

    @staticmethod
    def _calculate_t_statistic(group1: List[float], group2: List[float],
                              std1: float, std2: float) -> float:
        """Calculate t-statistic for two groups"""
        mean1 = statistics.mean(group1)
        mean2 = statistics.mean(group2)

        n1 = len(group1)
        n2 = len(group2)

        if std1 == 0 and std2 == 0:
            return 0.0

        pooled_std = math.sqrt(
            ((n1 - 1) * std1**2 + (n2 - 1) * std2**2) / (n1 + n2 - 2)
        )

        se = pooled_std * math.sqrt(1/n1 + 1/n2)

        if se == 0:
            return 0.0

        return (mean1 - mean2) / se

    def get_experiment_status(self, experiment_id: str) -> Optional[Dict[str, Any]]:
        """Get current status of experiment"""
        with self.lock:
            if experiment_id not in self.experiments:
                return None

            return self.experiment_results[experiment_id]


class BenchmarkingSystem:
    """System for creating and running benchmarks"""

    def __init__(self):
        self.datasets: Dict[str, BenchmarkDataset] = {}
        self.benchmark_results: Dict[str, Dict[str, Any]] = {}
        self.lock = threading.RLock()

    def create_benchmark_dataset(self, dataset: BenchmarkDataset) -> bool:
        """Create benchmark dataset"""
        with self.lock:
            if dataset.dataset_id in self.datasets:
                return False

            self.datasets[dataset.dataset_id] = dataset
            return True

    def run_benchmark(self, dataset_id: str,
                     evaluation_function: Callable) -> Optional[Dict[str, Any]]:
        """Run benchmark on dataset"""
        with self.lock:
            if dataset_id not in self.datasets:
                return None

            dataset = self.datasets[dataset_id]
            results = {
                "dataset_id": dataset_id,
                "timestamp": time.time(),
                "predictions": [],
                "metrics": {}
            }

            correct = 0
            total_time = 0

            for i, sample in enumerate(dataset.samples):
                start = time.time()
                prediction = evaluation_function(sample)
                elapsed = time.time() - start

                results["predictions"].append(prediction)
                total_time += elapsed

                if i < len(dataset.expected_outputs):
                    if prediction == dataset.expected_outputs[i]:
                        correct += 1

            # Calculate metrics
            total = len(dataset.samples)
            results["metrics"] = {
                "accuracy": correct / total if total > 0 else 0.0,
                "total_samples": total,
                "correct_predictions": correct,
                "total_time": total_time,
                "average_time_per_sample": total_time / total if total > 0 else 0.0
            }

            self.benchmark_results[dataset_id] = results
            return results

    def compare_benchmarks(self, dataset_id: str,
                          results_list: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Compare multiple benchmark runs"""
        if not results_list:
            return {}

        accuracies = [r["metrics"]["accuracy"] for r in results_list]
        times = [r["metrics"]["average_time_per_sample"] for r in results_list]

        return {
            "dataset_id": dataset_id,
            "num_runs": len(results_list),
            "accuracy_mean": statistics.mean(accuracies),
            "accuracy_stdev": (statistics.stdev(accuracies)
                              if len(accuracies) > 1 else 0.0),
            "time_mean": statistics.mean(times),
            "time_stdev": statistics.stdev(times) if len(times) > 1 else 0.0,
            "best_accuracy": max(accuracies),
            "worst_accuracy": min(accuracies)
        }

    def get_benchmark_report(self, dataset_id: str) -> Optional[Dict[str, Any]]:
        """Get benchmark report"""
        with self.lock:
            return self.benchmark_results.get(dataset_id)


class EvaluationPipeline:
    """Automated evaluation pipeline"""

    def __init__(self):
        self.metrics_collector = MetricsCollector()
        self.ab_testing = ABTestingFramework()
        self.benchmarking = BenchmarkingSystem()
        self.evaluation_stages: List[Dict[str, Any]] = []

    def add_evaluation_stage(self, stage_name: str,
                            evaluation_fn: Callable,
                            metrics: List[MetricType]):
        """Add stage to evaluation pipeline"""
        self.evaluation_stages.append({
            "name": stage_name,
            "function": evaluation_fn,
            "metrics": metrics,
            "results": []
        })

    def run_evaluation_pipeline(self, data: List[Any]) -> Dict[str, Any]:
        """Run complete evaluation pipeline"""
        pipeline_results = {
            "timestamp": time.time(),
            "stages": {}
        }

        for stage in self.evaluation_stages:
            stage_results = {
                "name": stage["name"],
                "metrics": {}
            }

            for item in data:
                stage["function"](item)

            for metric in stage["metrics"]:
                stats = self.metrics_collector.get_metric_statistics(metric)
                stage_results["metrics"][metric.value] = stats

            pipeline_results["stages"][stage["name"]] = stage_results

        return pipeline_results

    def get_overall_evaluation_report(self) -> Dict[str, Any]:
        """Get overall evaluation report"""
        return {
            "active_experiments": len(self.ab_testing.experiments),
            "completed_benchmarks": len(self.benchmarking.benchmark_results),
            "metrics_collected": len(self.metrics_collector.metrics),
            "evaluation_stages": len(self.evaluation_stages)
        }
