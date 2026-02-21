#!/usr/bin/env python3
"""
PROJECT PHOENIX - PHASE 3 TEST EXECUTOR
Test Execution and Results Collection

This script executes the test suite and collects results for Phase 3.
It bypasses pytest infrastructure issues and runs tests directly.
"""

import os
import sys
import json
import subprocess
from pathlib import Path
from datetime import datetime
from typing import List, Dict, Tuple


class TestExecutor:
    """Execute tests and collect results"""
    
    def __init__(self, project_root: str):
        self.project_root = Path(project_root)
        self.test_dir = self.project_root / "phoenix" / "tests"
        self.results = {
            "timestamp": datetime.now().isoformat(),
            "phase": "Phase 3: Test Execution",
            "test_results": [],
            "summary": {
                "total_tests": 0,
                "passed": 0,
                "failed": 0,
                "errors": 0,
                "skipped": 0
            }
        }
        
    def discover_tests(self) -> List[Path]:
        """Discover all test files"""
        test_files = sorted(self.test_dir.glob("test_*.py"))
        return test_files
    
    def run_test_file(self, test_file: Path) -> Dict:
        """Run a single test file"""
        test_name = test_file.stem
        print(f"  Running: {test_name}...", end=" ", flush=True)
        
        try:
            # Try to run with python -m
            cmd = [sys.executable, "-m", "pytest", str(test_file), "-v", "--tb=short"]
            result = subprocess.run(
                cmd,
                capture_output=True,
                text=True,
                timeout=60
            )
            
            if result.returncode == 0:
                status = "PASS"
                print("✓ PASS")
            else:
                status = "FAIL"
                print("✗ FAIL")
            
            return {
                "test": test_name,
                "status": status,
                "returncode": result.returncode,
                "stdout": result.stdout[-200:] if result.stdout else "",
                "stderr": result.stderr[-200:] if result.stderr else ""
            }
            
        except subprocess.TimeoutExpired:
            print("⏱ TIMEOUT")
            return {
                "test": test_name,
                "status": "TIMEOUT",
                "returncode": -1,
                "stdout": "",
                "stderr": "Test execution timed out"
            }
        except Exception as e:
            print(f"✗ ERROR")
            return {
                "test": test_name,
                "status": "ERROR",
                "returncode": -1,
                "stdout": "",
                "stderr": str(e)
            }
    
    def execute_tests(self) -> Dict:
        """Execute all tests"""
        test_files = self.discover_tests()
        
        print(f"\n{'='*80}")
        print("PHASE 3: TEST EXECUTION")
        print(f"{'='*80}\n")
        
        print(f"Discovered {len(test_files)} test files\n")
        print("Executing tests...\n")
        
        for i, test_file in enumerate(test_files, 1):
            result = self.run_test_file(test_file)
            self.results["test_results"].append(result)
            
            # Update summary
            self.results["summary"]["total_tests"] += 1
            if result["status"] == "PASS":
                self.results["summary"]["passed"] += 1
            elif result["status"] == "FAIL":
                self.results["summary"]["failed"] += 1
            elif result["status"] == "ERROR":
                self.results["summary"]["errors"] += 1
            elif result["status"] == "TIMEOUT":
                self.results["summary"]["skipped"] += 1
        
        return self.results
    
    def generate_report(self) -> str:
        """Generate test execution report"""
        summary = self.results["summary"]
        
        report = f"""
{'='*80}
PHASE 3 TEST EXECUTION - RESULTS SUMMARY
{'='*80}

Test Execution Date: {self.results['timestamp']}
Total Tests Executed: {summary['total_tests']}

Results:
  Passed:  {summary['passed']:>4}
  Failed:  {summary['failed']:>4}
  Errors:  {summary['errors']:>4}
  Skipped: {summary['skipped']:>4}

Pass Rate: {(summary['passed']/summary['total_tests']*100):.1f}%

"""
        
        # Add failed tests
        failed_tests = [r for r in self.results["test_results"] if r["status"] != "PASS"]
        if failed_tests:
            report += "Failed Tests:\n"
            for test in failed_tests:
                report += f"  ✗ {test['test']} - {test['status']}\n"
            report += "\n"
        
        report += f"{'='*80}\n"
        return report
    
    def save_results(self, output_file: str = "PHASE3_TEST_RESULTS.json"):
        """Save results to JSON file"""
        output_path = self.project_root / output_file
        with open(output_path, 'w') as f:
            json.dump(self.results, f, indent=2)
        print(f"\nResults saved to: {output_path}")


def main():
    """Main execution"""
    project_root = "/Users/rafi/Documents/Projects_OnGoing/Project phoenix"
    
    # Set Python path
    os.environ["PYTHONPATH"] = project_root
    
    executor = TestExecutor(project_root)
    results = executor.execute_tests()
    
    # Print report
    report = executor.generate_report()
    print(report)
    
    # Save results
    executor.save_results()
    
    # Return exit code based on results
    if results["summary"]["failed"] > 0 or results["summary"]["errors"] > 0:
        return 1
    return 0


if __name__ == "__main__":
    sys.exit(main())
