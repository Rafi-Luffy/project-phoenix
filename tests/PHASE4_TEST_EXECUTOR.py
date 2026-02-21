#!/usr/bin/env python3
"""
Phase 4 Test Executor - Comprehensive test suite runner
Executes all 58 tests and generates detailed reports
"""

import sys
import os
from pathlib import Path
from datetime import datetime
from uuid import UUID
import json
import traceback
from typing import Dict, List, Tuple

sys.path.insert(0, str(Path(__file__).parent))

def run_tests() -> Dict:
    """Execute all test files and collect results"""
    
    test_dir = Path(__file__).parent / "phoenix" / "tests"
    test_files = sorted([f for f in test_dir.glob("test_*.py") if f.is_file()])
    
    results = {
        "timestamp": datetime.now().isoformat(),
        "total_tests": 0,
        "passed": 0,
        "failed": 0,
        "errors": 0,
        "skipped": 0,
        "test_details": [],
        "failed_tests": [],
        "error_tests": []
    }
    
    print("\n" + "="*80)
    print("PHASE 4 TEST EXECUTION - COMPREHENSIVE TEST SUITE")
    print("="*80 + "\n")
    
    for test_file in test_files:
        test_name = test_file.stem
        try:
            # Import the test module
            module_name = f"phoenix.tests.{test_name}"
            test_module = __import__(module_name, fromlist=[''])
            
            # Find all test classes
            test_classes = [
                getattr(test_module, name) 
                for name in dir(test_module) 
                if name.startswith('Test') and isinstance(getattr(test_module, name), type)
            ]
            
            file_passed = 0
            file_failed = 0
            file_errors = 0
            
            for test_class in test_classes:
                # Find all test methods
                test_methods = [
                    method for method in dir(test_class) 
                    if method.startswith('test_') and callable(getattr(test_class, method))
                ]
                
                for method_name in test_methods:
                    test_id = f"{test_name}::{test_class.__name__}::{method_name}"
                    try:
                        # Instantiate and run test
                        instance = test_class()
                        method = getattr(instance, method_name)
                        method()
                        
                        results["passed"] += 1
                        file_passed += 1
                        status = "✓ PASS"
                        
                    except Exception as e:
                        error_msg = f"{type(e).__name__}: {str(e)[:100]}"
                        results["failed"] += 1
                        file_failed += 1
                        results["failed_tests"].append({"test": test_id, "error": error_msg})
                        status = "✗ FAIL"
                    
                    results["test_details"].append({
                        "test": test_id,
                        "status": "passed" if status.startswith("✓") else "failed"
                    })
            
            # File summary
            total_file_tests = file_passed + file_failed
            if total_file_tests > 0:
                file_status = f"({file_passed}/{total_file_tests})"
                symbol = "✓" if file_failed == 0 else "✗"
                print(f"{symbol} {test_name}: {file_status}")
            else:
                print(f"  {test_name}: NO TESTS FOUND")
                
            results["total_tests"] += file_passed + file_failed
                        
        except ImportError as e:
            results["errors"] += 1
            results["error_tests"].append({"test": test_name, "error": str(e)[:100]})
            print(f"✗ {test_name}: IMPORT ERROR - {str(e)[:60]}")
        except Exception as e:
            results["errors"] += 1
            results["error_tests"].append({"test": test_name, "error": str(e)[:100]})
            print(f"✗ {test_name}: ERROR - {str(e)[:60]}")
    
    # Calculate statistics
    if results["total_tests"] > 0:
        pass_rate = (results["passed"] / results["total_tests"]) * 100
    else:
        pass_rate = 0.0
    
    # Print summary
    print("\n" + "="*80)
    print("PHASE 4 TEST EXECUTION - RESULTS SUMMARY")
    print("="*80 + "\n")
    
    print(f"Test Execution Date: {results['timestamp']}")
    print(f"Total Tests Executed: {results['total_tests']}\n")
    print("Results:")
    print(f"  Passed:     {results['passed']}")
    print(f"  Failed:     {results['failed']}")
    print(f"  Errors:     {results['errors']}")
    print(f"  Skipped:    {results['skipped']}\n")
    print(f"Pass Rate: {pass_rate:.1f}%\n")
    
    if results["failed_tests"]:
        print("Failed Tests (first 10):")
        for i, failed in enumerate(results["failed_tests"][:10]):
            print(f"  {i+1}. {failed['test']}")
            print(f"     Error: {failed['error']}")
    
    if results["error_tests"]:
        print("\nTests with Import Errors (first 10):")
        for i, error in enumerate(results["error_tests"][:10]):
            print(f"  {i+1}. {error['test']}: {error['error']}")
    
    print("\n" + "="*80 + "\n")
    
    # Save results
    results_file = Path(__file__).parent / "PHASE4_TEST_RESULTS.json"
    with open(results_file, 'w') as f:
        json.dump(results, f, indent=2, default=str)
    
    print(f"Results saved to: {results_file}")
    
    return results


if __name__ == "__main__":
    results = run_tests()
    exit(0 if results["failed"] == 0 and results["errors"] == 0 else 1)
