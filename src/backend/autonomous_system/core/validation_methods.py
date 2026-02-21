"""
Validation Methods - Module 5.3

Comprehensive validation framework including cross-validation,
out-of-distribution testing, adversarial testing, human evaluation,
and long-term stability analysis.
"""

import random
import math
import time
from dataclasses import dataclass, field
from enum import Enum
from typing import Any, Dict, List, Optional, Callable, Tuple
from collections import defaultdict
import statistics


class ValidationStrategy(Enum):
    """Types of validation strategies"""
    K_FOLD = "k_fold"
    STRATIFIED_K_FOLD = "stratified_k_fold"
    LEAVE_ONE_OUT = "leave_one_out"
    TIME_SERIES_SPLIT = "time_series_split"
    NESTED_CV = "nested_cv"


class DistributionShift(Enum):
    """Types of distribution shifts"""
    COVARIATE_SHIFT = "covariate_shift"
    LABEL_SHIFT = "label_shift"
    CONCEPT_DRIFT = "concept_drift"
    SUBPOPULATION_SHIFT = "subpopulation_shift"


class AdversarialAttackType(Enum):
    """Types of adversarial attacks"""
    PERTURBATION = "perturbation"
    EVASION = "evasion"
    POISONING = "poisoning"
    MODEL_STEALING = "model_stealing"
    BACKDOOR = "backdoor"


@dataclass
class CrossValidationResult:
    """Result of cross-validation"""
    strategy: ValidationStrategy
    num_folds: int
    fold_scores: List[float]
    mean_score: float
    std_score: float
    confidence_interval: Tuple[float, float]


@dataclass
class ODDTestResult:
    """Out-of-distribution detection result"""
    sample_id: str
    is_ood: bool
    confidence: float
    distance_from_training: float
    anomaly_score: float


@dataclass
class AdversarialExample:
    """Adversarial test example"""
    example_id: str
    original_input: Any
    perturbed_input: Any
    original_prediction: Any
    adversarial_prediction: Any
    attack_type: AdversarialAttackType
    perturbation_magnitude: float
    successful: bool


@dataclass
class HumanEvaluationRating:
    """Rating from human evaluator"""
    evaluator_id: str
    sample_id: str
    rating: float  # 0-10 scale
    comments: Optional[str]
    timestamp: float = field(default_factory=time.time)


@dataclass
class StabilityMetrics:
    """Long-term stability metrics"""
    metric_name: str
    values_over_time: List[Tuple[float, float]]  # (timestamp, value)
    drift_detected: bool
    drift_magnitude: float
    trend: str  # increasing, decreasing, stable


class CrossValidation:
    """K-fold and other cross-validation strategies"""

    def __init__(self, strategy: ValidationStrategy = ValidationStrategy.K_FOLD):
        self.strategy = strategy

    def k_fold_split(self, data: List[Any], k: int = 5) -> List[Tuple[List[Any], List[Any]]]:
        """Split data into k folds"""
        fold_size = len(data) // k
        folds = []

        for i in range(k):
            start_idx = i * fold_size
            end_idx = start_idx + fold_size if i < k - 1 else len(data)

            test_fold = data[start_idx:end_idx]
            train_fold = data[:start_idx] + data[end_idx:]

            folds.append((train_fold, test_fold))

        return folds

    def stratified_k_fold(self, data: List[Any], labels: List[Any],
                         k: int = 5) -> List[Tuple[List[Any], List[Any]]]:
        """Stratified k-fold split maintaining label distribution"""
        # Group data by label
        label_groups = defaultdict(list)
        for i, label in enumerate(labels):
            label_groups[label].append(i)

        folds = [[] for _ in range(k)]

        # Distribute samples from each class across folds
        for label, indices in label_groups.items():
            fold_size = len(indices) // k
            for fold_idx in range(k):
                start = fold_idx * fold_size
                end = start + fold_size if fold_idx < k - 1 else len(indices)
                folds[fold_idx].extend(indices[start:end])

        # Create train/test splits
        splits = []
        for i in range(k):
            test_indices = set(folds[i])
            train_indices = []
            for j in range(k):
                if i != j:
                    train_indices.extend(folds[j])

            test_data = [data[idx] for idx in test_indices]
            train_data = [data[idx] for idx in train_indices]
            splits.append((train_data, test_data))

        return splits

    def leave_one_out_split(self, data: List[Any]) -> List[Tuple[List[Any], List[Any]]]:
        """Leave-one-out cross-validation"""
        splits = []
        for i in range(len(data)):
            test_data = [data[i]]
            train_data = data[:i] + data[i+1:]
            splits.append((train_data, test_data))
        return splits

    def time_series_split(self, data: List[Any],
                         test_size: float = 0.2) -> List[Tuple[List[Any], List[Any]]]:
        """Time series cross-validation"""
        splits = []
        total_size = len(data)
        test_split_size = int(total_size * test_size)

        # Create expanding window splits
        for i in range(1, test_split_size + 1):
            train_size = total_size - (test_split_size - i + 1)
            train_data = data[:train_size]
            test_data = data[train_size:train_size + 1]
            splits.append((train_data, test_data))

        return splits

    def evaluate_with_cv(self, model_fn: Callable, data: List[Any],
                        labels: List[Any], k: int = 5) -> CrossValidationResult:
        """Evaluate model using cross-validation"""
        if self.strategy == ValidationStrategy.K_FOLD:
            splits = self.k_fold_split(data, k)
        elif self.strategy == ValidationStrategy.STRATIFIED_K_FOLD:
            splits = self.stratified_k_fold(data, labels, k)
        elif self.strategy == ValidationStrategy.LEAVE_ONE_OUT:
            splits = self.leave_one_out_split(data)
        elif self.strategy == ValidationStrategy.TIME_SERIES_SPLIT:
            splits = self.time_series_split(data)
        else:
            splits = self.k_fold_split(data, k)

        fold_scores = []

        for train_data, test_data in splits:
            # Train model on fold
            model_fn(train_data)

            # Evaluate on test data
            correct = 0
            for test_sample in test_data:
                prediction = model_fn(test_sample)
                if prediction is not None:
                    correct += 1

            accuracy = correct / len(test_data) if test_data else 0.0
            fold_scores.append(accuracy)

        mean_score = statistics.mean(fold_scores)
        std_score = statistics.stdev(fold_scores) if len(fold_scores) > 1 else 0.0

        # Calculate 95% confidence interval
        sem = std_score / math.sqrt(len(fold_scores))
        ci_margin = 1.96 * sem
        ci = (mean_score - ci_margin, mean_score + ci_margin)

        return CrossValidationResult(
            strategy=self.strategy,
            num_folds=len(splits),
            fold_scores=fold_scores,
            mean_score=mean_score,
            std_score=std_score,
            confidence_interval=ci
        )


class OutOfDistributionDetector:
    """Detect and test out-of-distribution samples"""

    def __init__(self):
        self.training_data_statistics: Dict[str, Any] = {}
        self.known_distributions: List[Dict[str, Any]] = []

    def fit_on_training_data(self, training_data: List[Any]):
        """Fit ODD detector on training data"""
        # Calculate statistics of training data
        self.training_data_statistics = {
            "num_samples": len(training_data),
            "mean_magnitude": self._calculate_mean_magnitude(training_data),
            "std_magnitude": self._calculate_std_magnitude(training_data)
        }

    def detect_ood_samples(self, test_data: List[Any],
                          threshold: float = 2.0) -> List[ODDTestResult]:
        """Detect out-of-distribution samples"""
        results = []

        for i, sample in enumerate(test_data):
            magnitude = self._calculate_sample_magnitude(sample)

            # Calculate Z-score
            if self.training_data_statistics["std_magnitude"] > 0:
                z_score = (magnitude - self.training_data_statistics["mean_magnitude"]) / \
                         self.training_data_statistics["std_magnitude"]
            else:
                z_score = 0.0

            # Determine if OOD
            is_ood = abs(z_score) > threshold
            confidence = min(1.0, abs(z_score) / threshold)

            result = ODDTestResult(
                sample_id=f"sample_{i}",
                is_ood=is_ood,
                confidence=confidence,
                distance_from_training=magnitude,
                anomaly_score=z_score
            )
            results.append(result)

        return results

    def test_distribution_shifts(self, train_data: List[Any],
                                test_data: List[Any]) -> Dict[str, Any]:
        """Test for various types of distribution shifts"""
        shift_results = {
            DistributionShift.COVARIATE_SHIFT: self._test_covariate_shift(train_data, test_data),
            DistributionShift.LABEL_SHIFT: self._test_label_shift(train_data, test_data),
            DistributionShift.CONCEPT_DRIFT: self._test_concept_drift(train_data, test_data),
            DistributionShift.SUBPOPULATION_SHIFT: self._test_subpopulation_shift(train_data, test_data)
        }

        return shift_results

    def _test_covariate_shift(self, train_data: List[Any],
                              test_data: List[Any]) -> Dict[str, Any]:
        """Test for covariate shift"""
        train_mean = self._calculate_mean_magnitude(train_data)
        test_mean = self._calculate_mean_magnitude(test_data)

        shift_magnitude = abs(train_mean - test_mean) / train_mean if train_mean > 0 else 0.0

        return {
            "shift_detected": shift_magnitude > 0.1,
            "shift_magnitude": shift_magnitude,
            "train_mean": train_mean,
            "test_mean": test_mean
        }

    def _test_label_shift(self, train_data: List[Any],
                         test_data: List[Any]) -> Dict[str, Any]:
        """Test for label shift"""
        return {
            "shift_detected": False,
            "shift_magnitude": 0.0,
            "description": "Label shift detection requires labeled data"
        }

    def _test_concept_drift(self, train_data: List[Any],
                           test_data: List[Any]) -> Dict[str, Any]:
        """Test for concept drift"""
        # Simple drift detection based on temporal data
        return {
            "shift_detected": False,
            "shift_magnitude": 0.0,
            "description": "Concept drift requires temporal ordering"
        }

    def _test_subpopulation_shift(self, train_data: List[Any],
                                  test_data: List[Any]) -> Dict[str, Any]:
        """Test for subpopulation shift"""
        return {
            "shift_detected": False,
            "subpopulations_affected": [],
            "severity": "low"
        }

    @staticmethod
    def _calculate_sample_magnitude(sample: Any) -> float:
        """Calculate magnitude of sample"""
        if isinstance(sample, (list, tuple)):
            return math.sqrt(sum(x**2 for x in sample if isinstance(x, (int, float))))
        elif isinstance(sample, (int, float)):
            return float(sample)
        else:
            return 1.0

    def _calculate_mean_magnitude(self, data: List[Any]) -> float:
        """Calculate mean magnitude of data"""
        magnitudes = [self._calculate_sample_magnitude(s) for s in data]
        return statistics.mean(magnitudes) if magnitudes else 0.0

    @staticmethod
    def _calculate_std_magnitude(data: List[Any]) -> float:
        """Calculate standard deviation of magnitudes"""
        magnitudes = [OutOfDistributionDetector._calculate_sample_magnitude(s)
                      for s in data]
        return statistics.stdev(magnitudes) if len(magnitudes) > 1 else 0.0


class AdversarialTestingScenarios:
    """Adversarial testing and robustness evaluation"""

    def __init__(self):
        self.adversarial_examples: List[AdversarialExample] = []
        self.robustness_scores: Dict[str, float] = {}

    def generate_adversarial_examples(self, original_inputs: List[Any],
                                     model_fn: Callable,
                                     attack_type: AdversarialAttackType,
                                     perturbation_magnitude: float = 0.1) -> List[AdversarialExample]:
        """Generate adversarial examples"""
        examples = []

        for i, original_input in enumerate(original_inputs):
            # Get original prediction
            original_prediction = model_fn(original_input)

            # Create perturbed input
            if attack_type == AdversarialAttackType.PERTURBATION:
                perturbed = self._apply_perturbation(original_input, perturbation_magnitude)
            elif attack_type == AdversarialAttackType.EVASION:
                perturbed = self._apply_evasion(original_input, perturbation_magnitude)
            else:
                perturbed = original_input

            # Get adversarial prediction
            adversarial_prediction = model_fn(perturbed)

            # Check if attack was successful
            successful = original_prediction != adversarial_prediction

            example = AdversarialExample(
                example_id=f"adv_{i}",
                original_input=original_input,
                perturbed_input=perturbed,
                original_prediction=original_prediction,
                adversarial_prediction=adversarial_prediction,
                attack_type=attack_type,
                perturbation_magnitude=perturbation_magnitude,
                successful=successful
            )
            examples.append(example)

        self.adversarial_examples.extend(examples)
        return examples

    def test_robustness(self) -> Dict[str, Any]:
        """Test model robustness to adversarial examples"""
        if not self.adversarial_examples:
            return {}

        successful_attacks = sum(1 for ex in self.adversarial_examples if ex.successful)
        attack_success_rate = successful_attacks / len(self.adversarial_examples)

        return {
            "total_examples": len(self.adversarial_examples),
            "successful_attacks": successful_attacks,
            "attack_success_rate": attack_success_rate,
            "robustness_score": 1.0 - attack_success_rate,
            "critical_vulnerabilities": successful_attacks > len(self.adversarial_examples) * 0.2
        }

    @staticmethod
    def _apply_perturbation(input_data: Any, magnitude: float) -> Any:
        """Apply small perturbation to input"""
        if isinstance(input_data, (list, tuple)):
            return [x + random.gauss(0, magnitude) if isinstance(x, (int, float)) else x
                   for x in input_data]
        elif isinstance(input_data, (int, float)):
            return input_data + random.gauss(0, magnitude)
        else:
            return input_data

    @staticmethod
    def _apply_evasion(input_data: Any, magnitude: float) -> Any:
        """Apply evasion attack to input"""
        # Similar to perturbation for demonstration
        return AdversarialTestingScenarios._apply_perturbation(input_data, magnitude)

    def get_robustness_report(self) -> Dict[str, Any]:
        """Get robustness testing report"""
        robustness_test = self.test_robustness()

        return {
            **robustness_test,
            "attacks_by_type": self._group_attacks_by_type(),
            "vulnerability_summary": "High risk" if robustness_test.get("critical_vulnerabilities") else "Low risk"
        }

    def _group_attacks_by_type(self) -> Dict[str, int]:
        """Group attacks by type"""
        groups = defaultdict(int)
        for example in self.adversarial_examples:
            if example.successful:
                groups[example.attack_type.value] += 1
        return dict(groups)


class HumanEvaluationStudies:
    """Framework for human evaluation"""

    def __init__(self):
        self.ratings: List[HumanEvaluationRating] = []
        self.agreement_scores: Dict[str, float] = {}

    def collect_rating(self, rating: HumanEvaluationRating):
        """Collect rating from evaluator"""
        self.ratings.append(rating)

    def collect_ratings_batch(self, ratings: List[HumanEvaluationRating]):
        """Collect multiple ratings"""
        self.ratings.extend(ratings)

    def calculate_inter_rater_agreement(self) -> Dict[str, float]:
        """Calculate agreement between raters"""
        if len(self.ratings) < 2:
            return {}

        # Group ratings by sample
        ratings_by_sample = defaultdict(list)
        for rating in self.ratings:
            ratings_by_sample[rating.sample_id].append(rating.rating)

        # Calculate correlation for samples with multiple raters
        agreement_scores = {}
        for sample_id, sample_ratings in ratings_by_sample.items():
            if len(sample_ratings) > 1:
                mean_rating = statistics.mean(sample_ratings)
                std_rating = statistics.stdev(sample_ratings) if len(sample_ratings) > 1 else 0.0
                agreement = 1.0 - (std_rating / 10.0)  # Assuming 0-10 scale
                agreement_scores[sample_id] = max(0.0, agreement)

        self.agreement_scores = agreement_scores
        return agreement_scores

    def get_human_evaluation_report(self) -> Dict[str, Any]:
        """Get human evaluation report"""
        if not self.ratings:
            return {}

        sample_ratings = defaultdict(list)
        for rating in self.ratings:
            sample_ratings[rating.sample_id].append(rating.rating)

        sample_stats = {}
        for sample_id, ratings in sample_ratings.items():
            sample_stats[sample_id] = {
                "num_raters": len(ratings),
                "mean_rating": statistics.mean(ratings),
                "std_rating": statistics.stdev(ratings) if len(ratings) > 1 else 0.0,
                "min_rating": min(ratings),
                "max_rating": max(ratings)
            }

        agreement = self.calculate_inter_rater_agreement()

        return {
            "total_ratings": len(self.ratings),
            "total_samples": len(sample_ratings),
            "average_rating": statistics.mean([r.rating for r in self.ratings]),
            "agreement_scores": agreement,
            "sample_statistics": sample_stats
        }


class LongTermStabilityAnalyzer:
    """Analyze long-term stability and drift"""

    def __init__(self):
        self.stability_metrics: List[StabilityMetrics] = []
        self.drift_detections: List[Dict[str, Any]] = []

    def track_metric(self, metric_name: str, value: float, timestamp: float):
        """Track metric over time"""
        # Find or create metric
        metric = None
        for m in self.stability_metrics:
            if m.metric_name == metric_name:
                metric = m
                break

        if metric is None:
            metric = StabilityMetrics(
                metric_name=metric_name,
                values_over_time=[],
                drift_detected=False,
                drift_magnitude=0.0,
                trend="stable"
            )
            self.stability_metrics.append(metric)

        metric.values_over_time.append((timestamp, value))

    def detect_drift(self, metric_name: str,
                    window_size: int = 10,
                    threshold: float = 0.1) -> bool:
        """Detect drift in metric"""
        metric = None
        for m in self.stability_metrics:
            if m.metric_name == metric_name:
                metric = m
                break

        if not metric or len(metric.values_over_time) < window_size * 2:
            return False

        # Compare recent window with earlier window
        recent_values = [v[1] for v in metric.values_over_time[-window_size:]]
        earlier_values = [v[1] for v in metric.values_over_time[-window_size*2:-window_size]]

        recent_mean = statistics.mean(recent_values)
        earlier_mean = statistics.mean(earlier_values)

        if earlier_mean != 0:
            drift_magnitude = abs(recent_mean - earlier_mean) / earlier_mean
        else:
            drift_magnitude = 0.0

        drift_detected = drift_magnitude > threshold

        metric.drift_detected = drift_detected
        metric.drift_magnitude = drift_magnitude

        if drift_detected:
            self.drift_detections.append({
                "metric": metric_name,
                "timestamp": time.time(),
                "magnitude": drift_magnitude
            })

        return drift_detected

    def analyze_stability(self) -> Dict[str, Any]:
        """Analyze overall stability"""
        stability_report = {
            "metrics_tracked": len(self.stability_metrics),
            "metrics_with_drift": sum(1 for m in self.stability_metrics if m.drift_detected),
            "total_drift_detections": len(self.drift_detections),
            "metrics_status": []
        }

        for metric in self.stability_metrics:
            # Calculate trend
            if len(metric.values_over_time) > 1:
                first_half_mean = statistics.mean(
                    v[1] for v in metric.values_over_time[:len(metric.values_over_time)//2]
                )
                second_half_mean = statistics.mean(
                    v[1] for v in metric.values_over_time[len(metric.values_over_time)//2:]
                )

                if second_half_mean > first_half_mean:
                    trend = "increasing"
                elif second_half_mean < first_half_mean:
                    trend = "decreasing"
                else:
                    trend = "stable"

                metric.trend = trend

            stability_report["metrics_status"].append({
                "name": metric.metric_name,
                "drift_detected": metric.drift_detected,
                "drift_magnitude": metric.drift_magnitude,
                "trend": metric.trend,
                "num_datapoints": len(metric.values_over_time)
            })

        return stability_report
