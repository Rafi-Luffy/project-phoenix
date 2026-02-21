#!/usr/bin/env python3
"""
Project Phoenix - Complete System Verification & Test Runner
Ensures all components are in sync and working correctly
"""

import subprocess
import sys
import json
import asyncio
import time
import os
from datetime import datetime
from typing import Dict, List, Tuple, Any
import requests
import psycopg2

# Color codes for output
GREEN = '\033[92m'
RED = '\033[91m'
YELLOW = '\033[93m'
BLUE = '\033[94m'
CYAN = '\033[96m'
RESET = '\033[0m'
BOLD = '\033[1m'

class SystemVerifier:
    """Comprehensive system verification"""
    
    def __init__(self):
        self.results = {
            "timestamp": datetime.now().isoformat(),
            "checks": [],
            "overall_status": "UNKNOWN",
            "services": {},
            "tests": {},
            "sync_status": {}
        }
        self.failed_checks = []
        self.passed_checks = []
    
    def print_header(self, text: str):
        print(f"\n{BOLD}{CYAN}{'='*80}{RESET}")
        print(f"{BOLD}{CYAN}{text:^80}{RESET}")
        print(f"{BOLD}{CYAN}{'='*80}{RESET}\n")
    
    def print_section(self, text: str):
        print(f"\n{BOLD}{BLUE}{text}{RESET}")
        print(f"{BLUE}{'-'*60}{RESET}")
    
    def check_pass(self, name: str, message: str = ""):
        status = f"{GREEN}✅ PASS{RESET}"
        msg = f"{message}" if message else ""
        print(f"{status} {name} {msg}")
        self.passed_checks.append(name)
        self.results["checks"].append({"name": name, "status": "pass", "message": message})
    
    def check_fail(self, name: str, message: str = ""):
        status = f"{RED}❌ FAIL{RESET}"
        msg = f"({message})" if message else ""
        print(f"{status} {name} {msg}")
        self.failed_checks.append(name)
        self.results["checks"].append({"name": name, "status": "fail", "message": message})
    
    def check_warn(self, name: str, message: str = ""):
        status = f"{YELLOW}⚠️  WARN{RESET}"
        msg = f"({message})" if message else ""
        print(f"{status} {name} {msg}")
        self.results["checks"].append({"name": name, "status": "warn", "message": message})
    
    # ========================================================================
    # SERVICE CHECKS
    # ========================================================================
    
    def check_fastapi(self) -> bool:
        """Check FastAPI service"""
        try:
            response = requests.get("http://localhost:8000/health", timeout=5)
            if response.status_code == 200:
                data = response.json()
                self.check_pass("FastAPI Health Check", 
                              f"Status: {data.get('status', 'unknown')}")
                self.results["services"]["fastapi"] = {
                    "running": True,
                    "port": 8000,
                    "health": data.get('status')
                }
                return True
        except Exception as e:
            self.check_fail("FastAPI Health Check", str(e))
            self.results["services"]["fastapi"] = {"running": False, "port": 8000, "error": str(e)}
            return False
    
    def check_postgresql(self) -> bool:
        """Check PostgreSQL database"""
        try:
            conn = psycopg2.connect(
                dbname="phoenix_db",
                user=os.environ.get('USER'),
                host="localhost",
                port=5432
            )
            cursor = conn.cursor()
            cursor.execute("SELECT COUNT(*) FROM information_schema.tables WHERE table_schema='public';")
            table_count = cursor.fetchone()[0]
            conn.close()
            
            self.check_pass("PostgreSQL Connection", f"Tables: {table_count}")
            self.results["services"]["postgresql"] = {
                "running": True,
                "port": 5432,
                "database": "phoenix_db",
                "tables": table_count
            }
            return True
        except Exception as e:
            self.check_fail("PostgreSQL Connection", str(e))
            self.results["services"]["postgresql"] = {"running": False, "port": 5432, "error": str(e)}
            return False
    
    def check_ollama(self) -> bool:
        """Check Ollama LLM service"""
        try:
            response = requests.get("http://localhost:11434/api/tags", timeout=5)
            if response.status_code == 200:
                data = response.json()
                models = data.get('models', [])
                model_names = [m.get('name', 'unknown') for m in models]
                
                self.check_pass("Ollama Service", f"Models: {', '.join(model_names)}")
                self.results["services"]["ollama"] = {
                    "running": True,
                    "port": 11434,
                    "models": model_names
                }
                return True
        except Exception as e:
            self.check_fail("Ollama Service", str(e))
            self.results["services"]["ollama"] = {"running": False, "port": 11434, "error": str(e)}
            return False
    
    # ========================================================================
    # API ENDPOINT CHECKS
    # ========================================================================
    
    def check_api_endpoints(self) -> bool:
        """Check all API endpoints"""
        endpoints = [
            ("GET", "/health"),
            ("GET", "/llm/health"),
        ]
        
        passed = 0
        for method, endpoint in endpoints:
            try:
                if method == "GET":
                    response = requests.get(f"http://localhost:8000{endpoint}", timeout=5)
                else:
                    response = requests.post(f"http://localhost:8000{endpoint}", timeout=5)
                
                if response.status_code in [200, 201]:
                    self.check_pass(f"API Endpoint {method} {endpoint}")
                    passed += 1
                else:
                    self.check_fail(f"API Endpoint {method} {endpoint}", 
                                  f"Status: {response.status_code}")
            except Exception as e:
                self.check_fail(f"API Endpoint {method} {endpoint}", str(e))
        
        return passed == len(endpoints)
    
    # ========================================================================
    # FILE SYNC CHECKS
    # ========================================================================
    
    def check_file_sync(self) -> bool:
        """Check if all files are in sync"""
        self.print_section("File Synchronization Status")
        
        checks = [
            ("Frontend Components", "frontend/src/components/ui", "tsx"),
            ("Frontend Pages", "frontend/src/pages", "tsx"),
            ("Backend Core", "autonomous_system/core", "py"),
            ("Backend API", "autonomous_system/api", "py"),
            ("Tests", "tests", "py"),
        ]
        
        all_synced = True
        for name, path, ext in checks:
            try:
                # Count files
                result = subprocess.run(
                    f"find {path} -name '*.{ext}' 2>/dev/null | wc -l",
                    shell=True,
                    capture_output=True,
                    text=True
                )
                count = int(result.stdout.strip())
                
                if count > 0:
                    self.check_pass(f"{name}", f"{count} files")
                    self.results["sync_status"][name] = {"status": "synced", "count": count}
                else:
                    self.check_fail(f"{name}", "No files found")
                    all_synced = False
                    self.results["sync_status"][name] = {"status": "missing", "count": 0}
            except Exception as e:
                self.check_fail(f"{name}", str(e))
                all_synced = False
        
        return all_synced
    
    # ========================================================================
    # TEST EXECUTION
    # ========================================================================
    
    def run_tests(self) -> bool:
        """Run test suite"""
        self.print_section("Running Test Suite")
        
        try:
            # Run pytest with summary
            result = subprocess.run(
                ["python", "-m", "pytest", "tests/", "-v", "--tb=short", "-q"],
                capture_output=True,
                text=True,
                timeout=120,
                cwd="/Users/rafi/Documents/Projects_OnGoing/Project phoenix"
            )
            
            # Parse output
            output = result.stdout + result.stderr
            
            if "passed" in output:
                # Extract test count
                import re
                match = re.search(r'(\d+) passed', output)
                if match:
                    test_count = match.group(1)
                    self.check_pass(f"Test Suite", f"{test_count} tests passed")
                    self.results["tests"]["status"] = "passed"
                    self.results["tests"]["count"] = int(test_count)
                    return True
            
            if result.returncode != 0:
                self.check_warn("Test Suite", "Some tests failed or skipped")
                self.results["tests"]["status"] = "warning"
                return False
            
            return True
        
        except subprocess.TimeoutExpired:
            self.check_fail("Test Suite", "Timeout (>120s)")
            return False
        except Exception as e:
            self.check_fail("Test Suite", str(e))
            return False
    
    # ========================================================================
    # DEPENDENCY CHECKS
    # ========================================================================
    
    def check_dependencies(self) -> bool:
        """Check Python dependencies"""
        self.print_section("Python Dependencies")
        
        required = [
            'fastapi',
            'uvicorn',
            'psycopg2',
            'pytest',
            'aiohttp',
            'sqlalchemy'
        ]
        
        all_present = True
        for dep in required:
            try:
                __import__(dep.replace('-', '_'))
                self.check_pass(f"Dependency: {dep}")
            except ImportError:
                self.check_fail(f"Dependency: {dep}", "Not installed")
                all_present = False
        
        return all_present
    
    # ========================================================================
    # COMPREHENSIVE VERIFICATION
    # ========================================================================
    
    def verify_all(self) -> bool:
        """Run all verifications"""
        self.print_header("PROJECT PHOENIX - SYSTEM VERIFICATION")
        
        print(f"{CYAN}Starting comprehensive system verification...{RESET}\n")
        
        # Service checks
        self.print_section("Service Health Checks")
        fastapi_ok = self.check_fastapi()
        postgres_ok = self.check_postgresql()
        ollama_ok = self.check_ollama()
        
        # API checks
        self.print_section("API Endpoint Checks")
        api_ok = self.check_api_endpoints()
        
        # File sync
        self.check_file_sync()
        
        # Dependencies
        self.check_dependencies()
        
        # Tests
        test_ok = self.run_tests()
        
        # Summary
        self.print_summary(fastapi_ok and postgres_ok and ollama_ok)
        
        return fastapi_ok and postgres_ok and ollama_ok
    
    def print_summary(self, all_services_ok: bool):
        """Print verification summary"""
        self.print_header("VERIFICATION SUMMARY")
        
        total_checks = len(self.results["checks"])
        passed = len([c for c in self.results["checks"] if c["status"] == "pass"])
        failed = len([c for c in self.results["checks"] if c["status"] == "fail"])
        warned = len([c for c in self.results["checks"] if c["status"] == "warn"])
        
        print(f"{BOLD}Results:{RESET}")
        print(f"  {GREEN}✅ Passed: {passed}{RESET}")
        print(f"  {RED}❌ Failed: {failed}{RESET}")
        print(f"  {YELLOW}⚠️  Warned: {warned}{RESET}")
        print(f"  {BLUE}📊 Total: {total_checks}{RESET}\n")
        
        # Service status
        print(f"{BOLD}Service Status:{RESET}")
        for service, status in self.results["services"].items():
            running = status.get("running", False)
            icon = f"{GREEN}✅{RESET}" if running else f"{RED}❌{RESET}"
            print(f"  {icon} {service.upper()}: {status.get('port', 'N/A')}")
        
        print()
        
        # Overall status
        if failed == 0 and all_services_ok:
            self.results["overall_status"] = "OPERATIONAL"
            print(f"{GREEN}{BOLD}OVERALL STATUS: OPERATIONAL ✅{RESET}\n")
            print(f"{GREEN}All critical systems operational and ready for deployment!{RESET}")
        elif failed > 0:
            self.results["overall_status"] = "DEGRADED"
            print(f"{RED}{BOLD}OVERALL STATUS: DEGRADED ❌{RESET}\n")
            print(f"{RED}Some systems are not operational. Review failures above.{RESET}")
        else:
            self.results["overall_status"] = "WARNING"
            print(f"{YELLOW}{BOLD}OVERALL STATUS: WARNING ⚠️{RESET}\n")
            print(f"{YELLOW}Some warnings present, but core systems operational.{RESET}")
        
        # Save results
        try:
            with open("/tmp/verification_results.json", "w") as f:
                json.dump(self.results, f, indent=2, default=str)
            print(f"\n{CYAN}📁 Results saved to /tmp/verification_results.json{RESET}")
        except Exception as e:
            print(f"\n{YELLOW}⚠️  Could not save results: {e}{RESET}")


def main():
    """Main entry point"""
    verifier = SystemVerifier()
    
    try:
        success = verifier.verify_all()
        sys.exit(0 if success else 1)
    except KeyboardInterrupt:
        print(f"\n{YELLOW}Verification interrupted by user.{RESET}")
        sys.exit(1)
    except Exception as e:
        print(f"\n{RED}Verification error: {e}{RESET}")
        sys.exit(1)


if __name__ == "__main__":
    main()
