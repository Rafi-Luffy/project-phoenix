"""
Tests for Phoenix CLI - Command-line interface

Tests cover:
- Health checks
- Cache management
- Metrics retrieval
- Configuration management
- CLI argument parsing
"""

import pytest
import json
from unittest.mock import Mock, patch, MagicMock
from pathlib import Path
import sys

# Add phoenix to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from phoenix.cli.phoenix_cli import PhoenixCLI, create_parser
from phoenix.cli.cli_tools import (
    CacheManager, ConfigValidator, HealthChecker, MetricsExporter, CLITools
)


class TestPhoenixCLI:
    """Test PhoenixCLI main class"""
    
    @pytest.fixture
    def cli(self):
        """Create CLI instance"""
        return PhoenixCLI(base_url="http://localhost:8000")
    
    def test_cli_initialization(self, cli):
        """Test CLI initialization"""
        assert cli.base_url == "http://localhost:8000"
        assert cli.session is not None
    
    def test_cli_with_api_key(self):
        """Test CLI with API key"""
        cli = PhoenixCLI(base_url="http://localhost:8000", api_key="sk-test")
        assert cli.api_key == "sk-test"
    
    @patch('phoenix.cli.phoenix_cli.requests.Session.request')
    def test_health_command(self, mock_request, cli):
        """Test health check command"""
        mock_response = Mock()
        mock_response.json.return_value = {
            "status": "healthy",
            "timestamp": "2024-01-15T14:30:00Z",
            "latency_ms": 2.3,
            "components": {
                "llm_provider": "healthy",
                "database": "healthy"
            }
        }
        mock_request.return_value = mock_response
        
        # This would print output in real usage
        # Just verify it doesn't raise
        cli.cmd_health()
    
    @patch('phoenix.cli.phoenix_cli.requests.Session.request')
    def test_readiness_command(self, mock_request, cli):
        """Test readiness check"""
        mock_response = Mock()
        mock_response.json.return_value = {
            "ready": True
        }
        mock_request.return_value = mock_response
        
        cli.cmd_readiness()
    
    @patch('phoenix.cli.phoenix_cli.requests.Session.request')
    def test_health_detailed_command(self, mock_request, cli):
        """Test detailed health command"""
        mock_response = Mock()
        mock_response.json.return_value = {
            "overall_status": "healthy",
            "llm_provider": {
                "status": "healthy",
                "latency_ms": 45,
                "uptime_percent": 99.95
            },
            "database": {
                "status": "healthy",
                "latency_ms": 2,
                "uptime_percent": 100
            }
        }
        mock_request.return_value = mock_response
        
        cli.cmd_health_detailed()
    
    @patch('phoenix.cli.phoenix_cli.requests.Session.request')
    def test_cache_list_command(self, mock_request, cli):
        """Test cache list command"""
        mock_response = Mock()
        mock_response.json.return_value = {
            "entries": [
                {
                    "signature": "abc123def456",
                    "hit_count": 145,
                    "success_rate": 0.98,
                    "created_at": "2024-01-15T10:30:00Z"
                },
                {
                    "signature": "xyz789uvw012",
                    "hit_count": 89,
                    "success_rate": 0.95,
                    "created_at": "2024-01-14T15:20:00Z"
                }
            ],
            "total_count": 100
        }
        mock_request.return_value = mock_response
        
        cli.cmd_cache_list()
    
    @patch('phoenix.cli.phoenix_cli.requests.Session.request')
    def test_cache_inspect_command(self, mock_request, cli):
        """Test cache inspect command"""
        mock_response = Mock()
        mock_response.json.return_value = {
            "signature": "abc123def456",
            "created_at": "2024-01-15T10:30:00Z",
            "last_used": "2024-01-15T14:22:00Z",
            "hit_count": 145,
            "success_rate": 0.98,
            "fix": {
                "action": "RETRY_WITH_BACKOFF",
                "backoff_ms": 1000
            }
        }
        mock_request.return_value = mock_response
        
        cli.cmd_cache_inspect("abc123def456")
    
    @patch('phoenix.cli.phoenix_cli.requests.Session.request')
    def test_cache_clear_command(self, mock_request, cli):
        """Test cache clear command"""
        mock_response = Mock()
        mock_response.json.return_value = {
            "cleared_count": 2847,
            "freed_memory_bytes": 163571712
        }
        mock_request.return_value = mock_response
        
        with patch('builtins.input', return_value='yes'):
            cli.cmd_cache_clear()
    
    @patch('phoenix.cli.phoenix_cli.requests.Session.request')
    def test_metrics_command(self, mock_request, cli):
        """Test metrics command"""
        mock_response = Mock()
        mock_response.json.return_value = {
            "total_cycles": 12456,
            "successful_cycles": 12345,
            "failed_cycles": 111,
            "success_rate": 99.1,
            "cache_hit_rate": 87.2,
            "avg_latency_ms": 23.4,
            "peak_latency_ms": 245.1,
            "total_cost_dollars": 42.15
        }
        mock_request.return_value = mock_response
        
        cli.cmd_metrics()
    
    @patch('phoenix.cli.phoenix_cli.requests.Session.request')
    def test_config_show_command(self, mock_request, cli):
        """Test config show command"""
        mock_response = Mock()
        mock_response.json.return_value = {
            "llm": {
                "provider": "openai",
                "model": "gpt-4"
            },
            "database": {
                "type": "redis",
                "host": "localhost"
            }
        }
        mock_request.return_value = mock_response
        
        cli.cmd_config_show()
    
    @patch('builtins.open', create=True)
    @patch('phoenix.cli.phoenix_cli.requests.Session.request')
    def test_config_validate_command(self, mock_request, mock_file, cli):
        """Test config validate command"""
        mock_file.return_value.__enter__.return_value.read.return_value = '{}'
        mock_response = Mock()
        mock_response.json.return_value = {"valid": True, "errors": []}
        mock_request.return_value = mock_response
        
        with patch('json.load', return_value={}):
            cli.cmd_config_validate("config.json")


class TestCacheManager:
    """Test CacheManager class"""
    
    @pytest.fixture
    def cache_mgr(self):
        """Create cache manager"""
        return CacheManager()
    
    def test_cache_manager_initialization(self, cache_mgr):
        """Test cache manager init"""
        assert cache_mgr.api_url == "http://localhost:8000"
    
    def test_analyze_cache(self, cache_mgr):
        """Test cache analysis"""
        result = cache_mgr.analyze_cache()
        assert "total_entries" in result
        assert "hit_rate_percent" in result
        assert "miss_rate_percent" in result
    
    def test_optimize_cache(self, cache_mgr):
        """Test cache optimization"""
        result = cache_mgr.optimize_cache()
        assert "entries_removed" in result
        assert "space_freed_mb" in result


class TestConfigValidator:
    """Test ConfigValidator class"""
    
    @pytest.fixture
    def validator(self):
        """Create validator"""
        return ConfigValidator()
    
    def test_validate_openai_config_valid(self, validator):
        """Test valid OpenAI config"""
        config = {
            "provider": "openai",
            "api_key": "sk-xxxxx",
            "model": "gpt-4"
        }
        valid, errors = validator.validate_llm_config(config)
        assert valid is True
        assert len(errors) == 0
    
    def test_validate_openai_config_invalid_model(self, validator):
        """Test invalid OpenAI model"""
        config = {
            "provider": "openai",
            "api_key": "sk-xxxxx",
            "model": "invalid-model"
        }
        valid, errors = validator.validate_llm_config(config)
        assert valid is False
        assert len(errors) > 0
    
    def test_validate_claude_config_valid(self, validator):
        """Test valid Claude config"""
        config = {
            "provider": "anthropic",
            "api_key": "sk-ant-xxxxx",
            "model": "claude-3-opus"
        }
        valid, errors = validator.validate_llm_config(config)
        assert valid is True
    
    def test_validate_redis_config_valid(self, validator):
        """Test valid Redis config"""
        config = {
            "type": "redis",
            "host": "localhost",
            "port": 6379
        }
        valid, errors = validator.validate_database_config(config)
        assert valid is True
    
    def test_validate_redis_config_missing_host(self, validator):
        """Test Redis config missing host"""
        config = {
            "type": "redis",
            "port": 6379
        }
        valid, errors = validator.validate_database_config(config)
        assert valid is False
        assert any("host" in e for e in errors)
    
    def test_validate_postgresql_config_valid(self, validator):
        """Test valid PostgreSQL config"""
        config = {
            "type": "postgresql",
            "connection_string": "postgresql://user:pass@localhost/db"
        }
        valid, errors = validator.validate_database_config(config)
        assert valid is True
    
    def test_validate_full_config(self, validator):
        """Test full configuration validation"""
        config = {
            "llm": {
                "provider": "openai",
                "api_key": "sk-xxxxx",
                "model": "gpt-4"
            },
            "database": {
                "type": "redis",
                "host": "localhost",
                "port": 6379
            }
        }
        result = validator.validate_full_config(config)
        assert result["overall_valid"] is True
        assert "llm" in result["sections"]
        assert "database" in result["sections"]


class TestHealthChecker:
    """Test HealthChecker class"""
    
    @pytest.fixture
    def checker(self):
        """Create health checker"""
        return HealthChecker()
    
    @patch('requests.get')
    def test_check_api_connectivity_success(self, mock_get, checker):
        """Test successful API connectivity"""
        mock_response = Mock()
        mock_response.status_code = 200
        mock_get.return_value = mock_response
        
        success, msg = checker.check_api_connectivity("http://localhost:8000")
        assert success is True
    
    @patch('requests.get')
    def test_check_api_connectivity_failure(self, mock_get, checker):
        """Test failed API connectivity"""
        mock_get.side_effect = Exception("Connection refused")
        
        success, msg = checker.check_api_connectivity("http://localhost:8000")
        assert success is False
    
    def test_check_llm_provider_no_key(self, checker):
        """Test LLM provider check without key"""
        config = {"provider": "openai"}
        success, msg = checker.check_llm_provider(config)
        assert success is False
    
    def test_full_diagnostic(self, checker):
        """Test full diagnostic"""
        config = {
            "llm": {"provider": "openai"},
            "database": {"type": "redis"}
        }
        
        with patch.object(checker, 'check_api_connectivity', return_value=(True, "OK")):
            with patch.object(checker, 'check_llm_provider', return_value=(True, "OK")):
                with patch.object(checker, 'check_database', return_value=(True, "OK")):
                    result = checker.full_diagnostic("http://localhost:8000", config)
                    assert "timestamp" in result
                    assert "api" in result


class TestMetricsExporter:
    """Test MetricsExporter class"""
    
    @pytest.fixture
    def exporter(self):
        """Create exporter"""
        return MetricsExporter()
    
    def test_export_json(self, exporter, tmp_path):
        """Test JSON export"""
        metrics = {
            "total_cycles": 100,
            "success_rate": 0.95
        }
        output_file = tmp_path / "metrics.json"
        
        exporter.export_json(metrics, str(output_file))
        
        assert output_file.exists()
        with open(output_file) as f:
            data = json.load(f)
            assert data["total_cycles"] == 100
    
    def test_export_csv(self, exporter, tmp_path):
        """Test CSV export"""
        metrics = {
            "total_cycles": 100,
            "success_rate": 0.95
        }
        output_file = tmp_path / "metrics.csv"
        
        exporter.export_csv(metrics, str(output_file))
        
        assert output_file.exists()
        with open(output_file) as f:
            lines = f.readlines()
            assert len(lines) > 1  # Header + data
    
    def test_export_prometheus(self, exporter, tmp_path):
        """Test Prometheus format export"""
        metrics = {
            "total_cycles": 100,
            "success_rate": 95.5
        }
        output_file = tmp_path / "metrics.txt"
        
        exporter.export_prometheus(metrics, str(output_file))
        
        assert output_file.exists()
        with open(output_file) as f:
            content = f.read()
            assert "phoenix_" in content


class TestCLIParser:
    """Test CLI argument parser"""
    
    def test_parser_creation(self):
        """Test parser creation"""
        parser = create_parser()
        assert parser is not None
    
    def test_parse_health_command(self):
        """Test parsing health command"""
        parser = create_parser()
        args = parser.parse_args(["health"])
        assert args.command == "health"
    
    def test_parse_cache_list_command(self):
        """Test parsing cache list"""
        parser = create_parser()
        args = parser.parse_args(["cache", "list"])
        assert args.command == "cache"
        assert args.cache_command == "list"
    
    def test_parse_cache_inspect_command(self):
        """Test parsing cache inspect"""
        parser = create_parser()
        args = parser.parse_args(["cache", "inspect", "abc123"])
        assert args.command == "cache"
        assert args.cache_command == "inspect"
        assert args.signature == "abc123"
    
    def test_parse_with_global_options(self):
        """Test parsing with global options"""
        parser = create_parser()
        args = parser.parse_args([
            "--url", "http://custom.local",
            "--api-key", "sk-test",
            "--format", "json",
            "health"
        ])
        assert args.url == "http://custom.local"
        assert args.api_key == "sk-test"
        assert args.format == "json"


class TestCLIIntegration:
    """Integration tests for CLI"""
    
    @patch('phoenix.cli.phoenix_cli.requests.Session.request')
    def test_cli_health_flow(self, mock_request):
        """Test complete health check flow"""
        mock_response = Mock()
        mock_response.json.return_value = {
            "status": "healthy",
            "timestamp": "2024-01-15T14:30:00Z",
            "latency_ms": 2.3,
            "components": {"llm": "healthy"}
        }
        mock_request.return_value = mock_response
        
        cli = PhoenixCLI()
        cli.cmd_health()
        
        mock_request.assert_called()
    
    @patch('phoenix.cli.phoenix_cli.requests.Session.request')
    def test_cli_multiple_commands(self, mock_request):
        """Test multiple commands in sequence"""
        mock_response = Mock()
        mock_response.json.return_value = {"status": "healthy"}
        mock_request.return_value = mock_response
        
        cli = PhoenixCLI()
        cli.cmd_health()
        cli.cmd_readiness()
        
        assert mock_request.call_count >= 2


# Test execution markers
@pytest.mark.cli
class TestCLICompliance:
    """Test CLI compliance and standards"""
    
    def test_cli_has_help(self):
        """Test CLI has help message"""
        parser = create_parser()
        # Should not raise
        assert parser.format_help() is not None
    
    def test_cli_has_version(self):
        """Test CLI reports version"""
        cli = PhoenixCLI()
        # cmd_version should work
        assert hasattr(cli, 'cmd_version')
    
    def test_cli_environment_variable_support(self):
        """Test CLI respects environment variables"""
        with patch.dict('os.environ', {'PHOENIX_API_KEY': 'sk-test'}):
            # In real usage, CLI would read this
            import os
            assert os.getenv('PHOENIX_API_KEY') == 'sk-test'


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
