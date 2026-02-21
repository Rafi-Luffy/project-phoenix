#!/usr/bin/env python
"""
Phoenix CLI - Command-line interface for Phoenix autonomous healing system

Provides tools for:
- Cache management (list, clear, inspect)
- Configuration validation and updates
- Health checks and diagnostics
- Metrics viewing
- System information
"""

import argparse
import json
import sys
from typing import Dict, Any, List, Optional
from datetime import datetime
from tabulate import tabulate
import requests
from pathlib import Path


class PhoenixCLI:
    """Command-line interface for Phoenix"""
    
    def __init__(self, base_url: str = "http://localhost:8000", api_key: Optional[str] = None):
        """Initialize CLI with base URL and API key"""
        self.base_url = base_url.rstrip('/')
        self.api_key = api_key or ""
        self.session = self._create_session()
    
    def _create_session(self) -> requests.Session:
        """Create requests session with headers"""
        session = requests.Session()
        if self.api_key:
            session.headers.update({"X-API-Key": self.api_key})
        session.headers.update({"Accept": "application/json"})
        return session
    
    def _make_request(self, method: str, endpoint: str, **kwargs) -> Dict[str, Any]:
        """Make HTTP request to Phoenix API"""
        url = f"{self.base_url}{endpoint}"
        try:
            response = self.session.request(method, url, timeout=10, **kwargs)
            response.raise_for_status()
            return response.json()
        except requests.exceptions.ConnectionError:
            print(f"❌ Error: Cannot connect to Phoenix at {self.base_url}")
            print("   Is the server running? Try: python -m phoenix.main")
            sys.exit(1)
        except requests.exceptions.HTTPError as e:
            print(f"❌ Error: {e.response.status_code} - {e.response.text}")
            sys.exit(1)
    
    # ======================================================================
    # Health Commands
    # ======================================================================
    
    def cmd_health(self) -> None:
        """Check system health"""
        print("🏥 Checking Phoenix health...\n")
        data = self._make_request("GET", "/health")
        
        status_emoji = "✅" if data["status"] == "healthy" else "⚠️"
        print(f"{status_emoji} Status: {data['status'].upper()}")
        print(f"⏱️  Timestamp: {data.get('timestamp', 'N/A')}")
        print(f"⚡ Latency: {data.get('latency_ms', 'N/A')}ms\n")
        
        if "components" in data:
            print("Components:")
            for component, status in data["components"].items():
                emoji = "✅" if status == "healthy" else "❌"
                print(f"  {emoji} {component}: {status}")
    
    def cmd_readiness(self) -> None:
        """Check readiness for requests"""
        print("🚀 Checking Phoenix readiness...\n")
        data = self._make_request("GET", "/ready")
        
        if data.get("ready"):
            print("✅ Phoenix is READY for requests!\n")
        else:
            print("⚠️  Phoenix is NOT READY\n")
            if data.get("missing_components"):
                print("Missing components:")
                for component in data["missing_components"]:
                    print(f"  ❌ {component}")
    
    def cmd_health_detailed(self) -> None:
        """Get detailed health information"""
        print("🔍 Detailed Health Status\n")
        data = self._make_request("GET", "/health/detailed")
        
        print(f"Overall Status: {data.get('overall_status', 'unknown').upper()}\n")
        
        for component in ["llm_provider", "database", "cache", "metrics"]:
            if component in data:
                health = data[component]
                status_emoji = "✅" if health["status"] == "healthy" else "❌"
                print(f"{status_emoji} {component.replace('_', ' ').title()}")
                print(f"   Status: {health.get('status', 'unknown')}")
                print(f"   Latency: {health.get('latency_ms', 'N/A')}ms")
                print(f"   Uptime: {health.get('uptime_percent', 'N/A')}%")
                print()
    
    # ======================================================================
    # Cache Commands
    # ======================================================================
    
    def cmd_cache_list(self, limit: int = 20) -> None:
        """List cached fixes"""
        print(f"📦 Cache Entries (showing {limit} most recent)\n")
        data = self._make_request("GET", f"/cache?limit={limit}")
        
        if not data.get("entries"):
            print("Cache is empty")
            return
        
        table_data = []
        for entry in data["entries"]:
            table_data.append([
                entry["signature"][:30],
                entry["hit_count"],
                f"{entry['success_rate']:.0%}",
                entry["created_at"][:10]
            ])
        
        print(tabulate(table_data, headers=["Signature", "Hits", "Success", "Created"], tablefmt="grid"))
        print(f"\nTotal: {data['total_count']} entries")
        print(f"Cache size: {len(data['entries'])} loaded")
    
    def cmd_cache_inspect(self, signature: str) -> None:
        """Inspect cache entry"""
        print(f"🔎 Inspecting cache entry: {signature}\n")
        data = self._make_request("GET", f"/cache/{signature}")
        
        print(f"Signature: {data['signature']}")
        print(f"Created: {data['created_at']}")
        print(f"Last Used: {data['last_used']}")
        print(f"Hit Count: {data['hit_count']}")
        print(f"Success Rate: {data['success_rate']:.0%}\n")
        print("Fix:")
        print(json.dumps(data['fix'], indent=2))
    
    def cmd_cache_delete(self, signature: str) -> None:
        """Delete cache entry"""
        print(f"🗑️  Deleting cache entry: {signature}")
        self._make_request("DELETE", f"/cache/{signature}")
        print("✅ Entry deleted")
    
    def cmd_cache_clear(self) -> None:
        """Clear entire cache"""
        confirm = input("⚠️  Clear entire cache? (yes/no): ")
        if confirm.lower() != "yes":
            print("❌ Cancelled")
            return
        
        print("🗑️  Clearing cache...")
        data = self._make_request("POST", "/cache/clear")
        print(f"✅ Cleared {data.get('cleared_count', 0)} entries")
        print(f"   Freed {data.get('freed_memory_bytes', 0) / 1024 / 1024:.2f} MB")
    
    # ======================================================================
    # Metrics Commands
    # ======================================================================
    
    def cmd_metrics(self) -> None:
        """Show system metrics"""
        print("📊 System Metrics\n")
        data = self._make_request("GET", "/metrics")
        
        table_data = [
            ["Total Cycles", data.get("total_cycles", 0)],
            ["Successful", data.get("successful_cycles", 0)],
            ["Failed", data.get("failed_cycles", 0)],
            ["Success Rate", f"{data.get('success_rate', 0):.1f}%"],
            ["Cache Hit Rate", f"{data.get('cache_hit_rate', 0):.1f}%"],
            ["Avg Latency", f"{data.get('avg_latency_ms', 0):.0f}ms"],
            ["Peak Latency", f"{data.get('peak_latency_ms', 0):.0f}ms"],
            ["Total Cost", f"${data.get('total_cost_dollars', 0):.2f}"]
        ]
        
        print(tabulate(table_data, headers=["Metric", "Value"], tablefmt="simple"))
    
    def cmd_metrics_summary(self) -> None:
        """Show metrics summary (text format)"""
        print("📋 Metrics Summary\n")
        data = self._make_request("GET", "/metrics/summary")
        print(data)
    
    # ======================================================================
    # Configuration Commands
    # ======================================================================
    
    def cmd_config_show(self) -> None:
        """Show current configuration"""
        print("⚙️  Current Configuration\n")
        data = self._make_request("GET", "/config")
        print(json.dumps(data, indent=2, default=str))
    
    def cmd_config_validate(self, config_file: str) -> None:
        """Validate configuration file"""
        print(f"✓ Validating {config_file}...\n")
        
        with open(config_file) as f:
            if config_file.endswith('.json'):
                config = json.load(f)
            elif config_file.endswith('.yaml'):
                import yaml
                config = yaml.safe_load(f)
            else:
                print("❌ Unsupported file format. Use .json or .yaml")
                return
        
        data = self._make_request("POST", "/config/validate", json=config)
        
        if data.get("valid"):
            print("✅ Configuration is VALID\n")
        else:
            print("❌ Configuration has ERRORS:\n")
            for error in data.get("errors", []):
                print(f"  • {error}")
    
    def cmd_config_update(self, config_file: str) -> None:
        """Update configuration"""
        print(f"Updating configuration from {config_file}...\n")
        
        with open(config_file) as f:
            if config_file.endswith('.json'):
                config = json.load(f)
            else:
                import yaml
                config = yaml.safe_load(f)
        
        # Validate first
        result = self._make_request("POST", "/config/validate", json=config)
        if not result.get("valid"):
            print("❌ Configuration validation failed:")
            for error in result.get("errors", []):
                print(f"  • {error}")
            return
        
        # Update
        data = self._make_request("PUT", "/config", json=config)
        print("✅ Configuration updated successfully")
        print("\nNew configuration:")
        print(json.dumps(data, indent=2, default=str))
    
    # ======================================================================
    # System Commands
    # ======================================================================
    
    def cmd_version(self) -> None:
        """Show Phoenix version"""
        print("🚀 Phoenix Autonomous Healing System")
        print("   Version: 2.4.0")
        print("   Status: Production-Ready")
        print("   Tests: 1,141 passing")
    
    def cmd_info(self) -> None:
        """Show system information"""
        print("ℹ️  Phoenix Information\n")
        print("Version: 2.4.0")
        print("Python: 3.11+")
        print("API: REST with OpenAPI 3.0")
        print("Database: Redis (configurable)")
        print("LLM: OpenAI, Claude, Gemini (30+ providers)")
        print("\n📚 Documentation:")
        print("  • API Docs: http://localhost:8000/docs")
        print("  • OpenAPI: http://localhost:8000/openapi.json")
        print("  • Guide: https://docs.phoenix.local")


def create_parser() -> argparse.ArgumentParser:
    """Create CLI argument parser"""
    parser = argparse.ArgumentParser(
        description="Phoenix - Autonomous Healing System CLI",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  phoenix health                     Check system health
  phoenix metrics                    Show system metrics
  phoenix cache list                 List cached fixes
  phoenix cache clear                Clear entire cache
  phoenix config show                Show current configuration
  phoenix config validate config.yaml   Validate config file
        """
    )
    
    parser.add_argument(
        "--url",
        default="http://localhost:8000",
        help="Phoenix API URL (default: http://localhost:8000)"
    )
    parser.add_argument(
        "--api-key",
        help="API key for authentication"
    )
    parser.add_argument(
        "--format",
        choices=["json", "table", "text"],
        default="table",
        help="Output format"
    )
    
    subparsers = parser.add_subparsers(dest="command", help="Command to run")
    
    # Health commands
    subparsers.add_parser("health", help="Check system health")
    subparsers.add_parser("ready", help="Check readiness")
    subparsers.add_parser("health-detailed", help="Get detailed health info")
    
    # Cache commands
    cache_parser = subparsers.add_parser("cache", help="Cache management")
    cache_subparsers = cache_parser.add_subparsers(dest="cache_command")
    cache_subparsers.add_parser("list", help="List cached fixes")
    inspect_parser = cache_subparsers.add_parser("inspect", help="Inspect cache entry")
    inspect_parser.add_argument("signature", help="Fix signature")
    delete_parser = cache_subparsers.add_parser("delete", help="Delete cache entry")
    delete_parser.add_argument("signature", help="Fix signature")
    cache_subparsers.add_parser("clear", help="Clear entire cache")
    
    # Metrics commands
    metrics_parser = subparsers.add_parser("metrics", help="Show metrics")
    metrics_subparsers = metrics_parser.add_subparsers(dest="metrics_command")
    metrics_subparsers.add_parser("show", help="Show detailed metrics")
    metrics_subparsers.add_parser("summary", help="Show summary")
    
    # Config commands
    config_parser = subparsers.add_parser("config", help="Configuration management")
    config_subparsers = config_parser.add_subparsers(dest="config_command")
    config_subparsers.add_parser("show", help="Show current configuration")
    validate_parser = config_subparsers.add_parser("validate", help="Validate config file")
    validate_parser.add_argument("file", help="Config file path")
    update_parser = config_subparsers.add_parser("update", help="Update configuration")
    update_parser.add_argument("file", help="Config file path")
    
    # System commands
    subparsers.add_parser("version", help="Show version")
    subparsers.add_parser("info", help="Show system information")
    
    return parser


def main():
    """Main CLI entry point"""
    parser = create_parser()
    args = parser.parse_args()
    
    if not args.command:
        parser.print_help()
        sys.exit(1)
    
    # Initialize CLI
    cli = PhoenixCLI(base_url=args.url, api_key=args.api_key)
    
    # Route commands
    try:
        if args.command == "health":
            cli.cmd_health()
        elif args.command == "ready":
            cli.cmd_readiness()
        elif args.command == "health-detailed":
            cli.cmd_health_detailed()
        elif args.command == "cache":
            if args.cache_command == "list":
                cli.cmd_cache_list()
            elif args.cache_command == "inspect":
                cli.cmd_cache_inspect(args.signature)
            elif args.cache_command == "delete":
                cli.cmd_cache_delete(args.signature)
            elif args.cache_command == "clear":
                cli.cmd_cache_clear()
            else:
                print("Cache command required")
        elif args.command == "metrics":
            if args.metrics_command == "summary":
                cli.cmd_metrics_summary()
            else:
                cli.cmd_metrics()
        elif args.command == "config":
            if args.config_command == "show":
                cli.cmd_config_show()
            elif args.config_command == "validate":
                cli.cmd_config_validate(args.file)
            elif args.config_command == "update":
                cli.cmd_config_update(args.file)
            else:
                print("Config command required")
        elif args.command == "version":
            cli.cmd_version()
        elif args.command == "info":
            cli.cmd_info()
        else:
            print(f"Unknown command: {args.command}")
            sys.exit(1)
    except KeyboardInterrupt:
        print("\n❌ Cancelled")
        sys.exit(1)
    except Exception as e:
        print(f"❌ Error: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()
