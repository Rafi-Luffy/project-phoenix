"""
Advanced Integration Test Runner
Executes all end-to-end scenarios and generates comprehensive report
"""
import pytest
import sys
import json
from pathlib import Path
from datetime import datetime
import subprocess


def run_comprehensive_test_suite():
    """Run all test suites with detailed reporting"""
    
    print("=" * 80)
    print("PHOENIX COMPREHENSIVE TEST SUITE")
    print("=" * 80)
    print(f"Started: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("=" * 80)
    
    test_suites = [
        ("End-to-End Simple Scenarios", "tests/test_end_to_end.py::TestEndToEndSimpleScenarios"),
        ("End-to-End Complex Scenarios", "tests/test_end_to_end.py::TestEndToEndComplexScenarios"),
        ("End-to-End Edge Cases", "tests/test_end_to_end.py::TestEndToEndEdgeCases"),
        ("End-to-End Real-World", "tests/test_end_to_end.py::TestEndToEndRealWorldScenarios"),
        ("End-to-End Concurrency", "tests/test_end_to_end.py::TestEndToEndConcurrencyScenarios"),
        ("End-to-End Security", "tests/test_end_to_end.py::TestEndToEndSecurityScenarios"),
        ("End-to-End Performance", "tests/test_end_to_end.py::TestEndToEndPerformanceScenarios"),
        ("End-to-End Data Validation", "tests/test_end_to_end.py::TestEndToEndDataValidation"),
        ("End-to-End Modern Tech", "tests/test_end_to_end.py::TestEndToEndModernTechScenarios"),
        ("Stress Testing", "tests/test_stress_chaos.py::TestStressLoadScenarios"),
        ("Chaos Engineering", "tests/test_stress_chaos.py::TestChaosEngineeringScenarios"),
        ("Extreme Boundaries", "tests/test_stress_chaos.py::TestExtremeBoundaryConditions"),
        ("Complex State Management", "tests/test_stress_chaos.py::TestComplexStateManagement"),
        ("Production Scenarios", "tests/test_stress_chaos.py::TestRealisticProductionScenarios"),
    ]
    
    results = {}
    total_passed = 0
    total_failed = 0
    total_time = 0
    
    for suite_name, suite_path in test_suites:
        print(f"\n{'=' * 80}")
        print(f"Running: {suite_name}")
        print(f"{'=' * 80}")
        
        # Run pytest with JSON report
        cmd = [
            "pytest",
            suite_path,
            "-v",
            "--tb=short",
            "--color=yes"
        ]
        
        result = subprocess.run(
            cmd,
            capture_output=True,
            text=True
        )
        
        # Parse output
        output_lines = result.stdout.split('\n')
        passed = failed = 0
        
        for line in output_lines:
            if " passed" in line:
                try:
                    passed = int(line.split()[0])
                except:
                    pass
            if " failed" in line:
                try:
                    failed = int(line.split()[0])
                except:
                    pass
        
        results[suite_name] = {
            "passed": passed,
            "failed": failed,
            "status": "PASSED" if failed == 0 and passed > 0 else "FAILED" if failed > 0 else "SKIPPED"
        }
        
        total_passed += passed
        total_failed += failed
        
        # Print summary
        status_icon = "" if results[suite_name]["status"] == "PASSED" else "" if results[suite_name]["status"] == "FAILED" else ""
        print(f"{status_icon} {suite_name}: {passed} passed, {failed} failed")
    
    # Final summary
    print(f"\n{'=' * 80}")
    print("FINAL SUMMARY")
    print(f"{'=' * 80}")
    print(f"Total Test Suites: {len(test_suites)}")
    print(f"Total Tests Passed: {total_passed}")
    print(f"Total Tests Failed: {total_failed}")
    print(f"Overall Pass Rate: {(total_passed / (total_passed + total_failed) * 100):.1f}%")
    print(f"Completed: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print(f"{'=' * 80}\n")
    
    # Generate JSON report
    report = {
        "timestamp": datetime.now().isoformat(),
        "summary": {
            "total_suites": len(test_suites),
            "total_passed": total_passed,
            "total_failed": total_failed,
            "pass_rate": (total_passed / (total_passed + total_failed) * 100) if total_passed + total_failed > 0 else 0
        },
        "suites": results
    }
    
    report_path = Path("test_report.json")
    with open(report_path, 'w') as f:
        json.dump(report, f, indent=2)
    
    print(f" Detailed report saved to: {report_path}")
    
    return total_failed == 0


if __name__ == "__main__":
    success = run_comprehensive_test_suite()
    sys.exit(0 if success else 1)
