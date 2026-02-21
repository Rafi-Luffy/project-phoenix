"""
Metrics Exporter

Exports healing metrics in formats useful for visualization and monitoring.
I added this so we can push metrics to dashboards without changing the main orchestrator.

Optional - only use if you want to export metrics.
"""

import json
import os
from datetime import datetime
from typing import Dict, Any, Optional
from pathlib import Path

from phoenix.core.logging import get_logger

logger = get_logger(__name__)


class MetricsExporter:
    """
    Exports Phoenix healing metrics for external monitoring.
    
    Useful for Grafana, Datadog, Prometheus, or custom dashboards.
    Doesn't affect the main healing loop - completely optional.
    """
    
    def __init__(self, export_dir: str):
        """
        Initialize metrics exporter.
        
        Args:
            export_dir: Directory to export metrics to
        """
        self.export_dir = export_dir
        os.makedirs(export_dir, exist_ok=True)
        self.logger = get_logger(__name__)
    
    def export_healing_metrics(self, stats: Dict[str, Any]) -> str:
        """
        Export healing statistics to JSON file.
        
        Args:
            stats: Statistics dictionary from orchestrator
            
        Returns:
            Path to exported metrics file
        """
        timestamp = datetime.utcnow().strftime("%Y%m%d_%H%M%S")
        filename = f"phoenix_metrics_{timestamp}.json"
        filepath = os.path.join(self.export_dir, filename)
        
        # Add timestamp and version
        metrics = {
            "timestamp": datetime.utcnow().isoformat(),
            "version": "1.0",
            **stats
        }
        
        with open(filepath, "w") as f:
            json.dump(metrics, f, indent=2, default=str)
        
        self.logger.info("metrics_exported", filepath=filepath)
        return filepath
    
    def export_prometheus_format(self, stats: Dict[str, Any]) -> str:
        """
        Export metrics in Prometheus format for scraping.
        
        Args:
            stats: Statistics dictionary
            
        Returns:
            Prometheus-formatted metrics string
        """
        lines = [
            "# HELP phoenix_healing_cycles Total healing cycles run",
            "# TYPE phoenix_healing_cycles counter",
            f"phoenix_healing_cycles {stats.get('autonomous_healing_stats', {}).get('total_healing_cycles', 0)}",
            "",
            "# HELP phoenix_success_rate Success rate percentage",
            "# TYPE phoenix_success_rate gauge",
            f"phoenix_success_rate {stats.get('autonomous_healing_stats', {}).get('success_rate', 0)}",
            "",
            "# HELP phoenix_fixes_applied Total fixes applied",
            "# TYPE phoenix_fixes_applied counter",
            f"phoenix_fixes_applied {stats.get('fix_stats', {}).get('total_fixes', 0)}",
            "",
            "# HELP phoenix_fix_success_rate Fix success percentage",
            "# TYPE phoenix_fix_success_rate gauge",
            f"phoenix_fix_success_rate {stats.get('fix_stats', {}).get('success_rate', 0)}",
            "",
            "# HELP phoenix_failures_detected Total failures detected",
            "# TYPE phoenix_failures_detected counter",
            f"phoenix_failures_detected {stats.get('failure_stats', {}).get('total_failures', 0)}",
        ]
        
        return "\n".join(lines)
    
    def export_csv_for_excel(self, stats: Dict[str, Any]) -> str:
        """
        Export key metrics as CSV for spreadsheets.
        
        Args:
            stats: Statistics dictionary
            
        Returns:
            Path to exported CSV file
        """
        import csv
        
        timestamp = datetime.utcnow().strftime("%Y%m%d_%H%M%S")
        filename = f"phoenix_metrics_{timestamp}.csv"
        filepath = os.path.join(self.export_dir, filename)
        
        metrics_dict = self._flatten_metrics(stats)
        
        with open(filepath, "w", newline="") as f:
            writer = csv.writer(f)
            writer.writerow(["Metric", "Value"])
            for key, value in metrics_dict.items():
                writer.writerow([key, value])
        
        self.logger.info("csv_exported", filepath=filepath)
        return filepath
    
    def _flatten_metrics(self, stats: Dict[str, Any], prefix: str = "") -> Dict[str, Any]:
        """Flatten nested metrics dictionary."""
        flat = {}
        
        for key, value in stats.items():
            full_key = f"{prefix}_{key}" if prefix else key
            
            if isinstance(value, dict):
                flat.update(self._flatten_metrics(value, full_key))
            elif isinstance(value, (list, tuple)):
                flat[full_key] = len(value)
            else:
                flat[full_key] = value
        
        return flat
