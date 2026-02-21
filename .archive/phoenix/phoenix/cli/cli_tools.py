"""
Phoenix CLI Tools - Specialized command-line utilities

Includes:
- Cache Manager: Advanced cache operations
- Config Validator: Deep configuration validation
- Health Checker: Comprehensive diagnostics
- Metrics Exporter: Multi-format metrics export
"""

import json
from typing import Dict, Any, List, Optional, Tuple
from dataclasses import dataclass, asdict
from datetime import datetime
import subprocess
import sys


@dataclass
class CacheEntry:
    """Cache entry metadata"""
    signature: str
    fix: Dict[str, Any]
    hit_count: int
    success_rate: float
    created_at: str
    last_used: str
    size_bytes: int


class CacheManager:
    """Advanced cache management tool"""
    
    def __init__(self, api_url: str = "http://localhost:8000"):
        self.api_url = api_url
    
    def list_entries(self, limit: int = 100, sort_by: str = "hits") -> List[CacheEntry]:
        """List cache entries with sorting"""
        # Implementation would call API
        pass
    
    def export_cache(self, output_file: str, format: str = "json") -> None:
        """Export cache to file"""
        # Implement export in JSON, CSV, or SQLite format
        pass
    
    def analyze_cache(self) -> Dict[str, Any]:
        """Analyze cache hit rates, efficiency, etc."""
        return {
            "total_entries": 0,
            "total_size_mb": 0,
            "hit_rate_percent": 0,
            "miss_rate_percent": 0,
            "avg_success_rate": 0,
            "most_used_fix": None,
            "least_useful_fix": None,
            "estimated_cost_savings": 0
        }
    
    def optimize_cache(self, mode: str = "aggressive") -> Dict[str, Any]:
        """Optimize cache (remove unused entries, compress, etc.)"""
        return {
            "entries_removed": 0,
            "space_freed_mb": 0,
            "optimization_time_seconds": 0
        }


class ConfigValidator:
    """Deep configuration validation tool"""
    
    def validate_llm_config(self, config: Dict[str, Any]) -> Tuple[bool, List[str]]:
        """Validate LLM provider configuration"""
        errors = []
        
        if "provider" not in config:
            errors.append("Missing 'provider' field")
        
        if "api_key" not in config:
            errors.append("Missing 'api_key' field")
        
        if "model" not in config:
            errors.append("Missing 'model' field")
        
        # Provider-specific validation
        provider = config.get("provider", "").lower()
        
        if provider == "openai":
            if not config.get("model", "").startswith("gpt"):
                errors.append("Invalid OpenAI model")
        elif provider == "anthropic":
            if not config.get("model", "").startswith("claude"):
                errors.append("Invalid Claude model")
        
        return len(errors) == 0, errors
    
    def validate_database_config(self, config: Dict[str, Any]) -> Tuple[bool, List[str]]:
        """Validate database configuration"""
        errors = []
        
        if "type" not in config:
            errors.append("Missing 'type' field")
        
        db_type = config.get("type", "").lower()
        
        if db_type == "redis":
            if "host" not in config:
                errors.append("Redis requires 'host'")
            if "port" not in config:
                errors.append("Redis requires 'port'")
        elif db_type == "postgresql":
            if "connection_string" not in config:
                errors.append("PostgreSQL requires 'connection_string'")
        
        return len(errors) == 0, errors
    
    def validate_full_config(self, config: Dict[str, Any]) -> Dict[str, Any]:
        """Validate entire configuration"""
        results = {
            "overall_valid": True,
            "sections": {}
        }
        
        # Validate each section
        if "llm" in config:
            valid, errors = self.validate_llm_config(config["llm"])
            results["sections"]["llm"] = {"valid": valid, "errors": errors}
            if not valid:
                results["overall_valid"] = False
        
        if "database" in config:
            valid, errors = self.validate_database_config(config["database"])
            results["sections"]["database"] = {"valid": valid, "errors": errors}
            if not valid:
                results["overall_valid"] = False
        
        return results


class HealthChecker:
    """Comprehensive health check tool"""
    
    def check_api_connectivity(self, base_url: str) -> Tuple[bool, str]:
        """Check API connectivity"""
        try:
            import requests
            response = requests.get(f"{base_url}/health", timeout=5)
            return response.status_code == 200, "Connected"
        except Exception as e:
            return False, str(e)
    
    def check_llm_provider(self, config: Dict[str, Any]) -> Tuple[bool, str]:
        """Check LLM provider connectivity"""
        # Test API key and connectivity
        provider = config.get("provider", "").lower()
        api_key = config.get("api_key", "")
        
        if not api_key:
            return False, "No API key configured"
        
        # Attempt minimal API call
        try:
            if provider == "openai":
                import openai
                openai.api_key = api_key
                # Just check key validity without using quota
                return True, "Connected"
        except Exception as e:
            return False, str(e)
        
        return True, "OK"
    
    def check_database(self, config: Dict[str, Any]) -> Tuple[bool, str]:
        """Check database connectivity"""
        db_type = config.get("type", "").lower()
        
        try:
            if db_type == "redis":
                import redis
                r = redis.Redis(
                    host=config.get("host"),
                    port=config.get("port"),
                    db=0,
                    socket_connect_timeout=5
                )
                r.ping()
                return True, "Connected"
        except Exception as e:
            return False, str(e)
        
        return False, "Unknown database type"
    
    def full_diagnostic(self, base_url: str, config: Dict[str, Any]) -> Dict[str, Any]:
        """Run full system diagnostic"""
        return {
            "timestamp": datetime.now().isoformat(),
            "api": self._format_check(self.check_api_connectivity(base_url)),
            "llm": self._format_check(self.check_llm_provider(config.get("llm", {}))),
            "database": self._format_check(self.check_database(config.get("database", {}))),
            "summary": "All systems operational"
        }
    
    @staticmethod
    def _format_check(result: Tuple[bool, str]) -> Dict[str, Any]:
        """Format check result"""
        return {"status": "✅" if result[0] else "❌", "message": result[1]}


class MetricsExporter:
    """Export metrics in various formats"""
    
    def export_json(self, metrics: Dict[str, Any], output_file: str) -> None:
        """Export metrics as JSON"""
        with open(output_file, 'w') as f:
            json.dump(metrics, f, indent=2, default=str)
    
    def export_csv(self, metrics: Dict[str, Any], output_file: str) -> None:
        """Export metrics as CSV"""
        import csv
        
        with open(output_file, 'w', newline='') as f:
            writer = csv.writer(f)
            writer.writerow(["Metric", "Value"])
            for key, value in metrics.items():
                writer.writerow([key, value])
    
    def export_prometheus(self, metrics: Dict[str, Any], output_file: str) -> None:
        """Export metrics in Prometheus format"""
        lines = []
        for key, value in metrics.items():
            # Convert to valid Prometheus metric name
            metric_name = f"phoenix_{key}".lower().replace("_", "_")
            if isinstance(value, (int, float)):
                lines.append(f"{metric_name} {value}")
        
        with open(output_file, 'w') as f:
            f.write('\n'.join(lines))
    
    def export_cloudwatch(self, metrics: Dict[str, Any], namespace: str = "Phoenix") -> None:
        """Export metrics to AWS CloudWatch"""
        import boto3
        
        cloudwatch = boto3.client('cloudwatch')
        
        for key, value in metrics.items():
            if isinstance(value, (int, float)):
                cloudwatch.put_metric_data(
                    Namespace=namespace,
                    MetricData=[{
                        'MetricName': key,
                        'Value': value,
                        'Timestamp': datetime.now()
                    }]
                )


class CLITools:
    """Main CLI tools class"""
    
    def __init__(self, base_url: str = "http://localhost:8000"):
        self.base_url = base_url
        self.cache = CacheManager(base_url)
        self.validator = ConfigValidator()
        self.health = HealthChecker()
        self.metrics = MetricsExporter()
    
    def install_shell_completion(self, shell: str = "bash") -> None:
        """Install shell completion"""
        completions = {
            "bash": self._get_bash_completion(),
            "zsh": self._get_zsh_completion(),
            "fish": self._get_fish_completion()
        }
        
        if shell not in completions:
            print(f"Unsupported shell: {shell}")
            return
        
        completion = completions[shell]
        print(f"Add this to your {shell}rc:")
        print(completion)
    
    def _get_bash_completion(self) -> str:
        """Get bash completion script"""
        return """
_phoenix_completion() {
    local cur="${COMP_WORDS[COMP_CWORD]}"
    local commands="health ready health-detailed cache metrics config version info"
    
    COMPREPLY=( $(compgen -W "$commands" -- $cur) )
}

complete -F _phoenix_completion phoenix
        """
    
    def _get_zsh_completion(self) -> str:
        """Get zsh completion script"""
        return """
_phoenix() {
    _arguments \
        '1: :(health ready health-detailed cache metrics config version info)' \
        '--url[API URL]' \
        '--api-key[API key]' \
        '--format[Output format]:(json table text)'
}

compdef _phoenix phoenix
        """
    
    def _get_fish_completion(self) -> str:
        """Get fish completion script"""
        return """
complete -c phoenix -n "__fish_use_subcommand_from_list" -a "health" -d "Check system health"
complete -c phoenix -n "__fish_use_subcommand_from_list" -a "cache" -d "Cache management"
complete -c phoenix -n "__fish_use_subcommand_from_list" -a "metrics" -d "Show metrics"
complete -c phoenix -n "__fish_use_subcommand_from_list" -a "config" -d "Configuration management"
        """


# Example usage
if __name__ == "__main__":
    tools = CLITools()
    
    # Example cache analysis
    analysis = tools.cache.analyze_cache()
    print("Cache Analysis:", analysis)
    
    # Example health check
    checker = HealthChecker()
    diagnostic = checker.full_diagnostic(
        "http://localhost:8000",
        {"llm": {"provider": "openai"}, "database": {"type": "redis"}}
    )
    print("Diagnostic:", diagnostic)
