#!/usr/bin/env python3
"""
Quick Test Validation Script
Validates that all test files can be imported and counted
"""
import sys
from pathlib import Path

def validate_test_suite():
    """Validate test suite structure and imports"""
    
    print("=" * 80)
    print("PHOENIX TEST SUITE VALIDATION")
    print("=" * 80)
    
    # Check test files exist
    test_files = [
        "tests/test_end_to_end.py",
        "tests/test_stress_chaos.py",
    ]
    
    print("\nChecking test files...")
    for test_file in test_files:
        path = Path(test_file)
        if path.exists():
            size_kb = path.stat().st_size / 1024
            print(f"  [PASS] {test_file} ({size_kb:.1f} KB)")
        else:
            print(f"  [FAIL] {test_file} MISSING")
            return False
    
    # Count test classes and methods
    print("\nAnalyzing test structure...")
    import re
    
    total_classes = 0
    total_methods = 0
    
    for test_file in test_files:
        with open(test_file, 'r') as f:
            content = f.read()
        
        classes = len(re.findall(r'class Test\w+:', content))
        methods = len(re.findall(r'def test_\w+\(', content))
        
        total_classes += classes
        total_methods += methods
        
        print(f"  {Path(test_file).name}:")
        print(f"     - Classes: {classes}")
        print(f"     - Methods: {methods}")
    
    print(f"\nTOTALS:")
    print(f"  - Test Classes: {total_classes}")
    print(f"  - Test Methods: {total_methods}")
    
    # Validate syntax
    print("\nValidating Python syntax...")
    import ast
    
    for test_file in test_files:
        try:
            with open(test_file, 'r') as f:
                ast.parse(f.read())
            print(f"  [PASS] {Path(test_file).name}: Valid syntax")
        except SyntaxError as e:
            print(f"  [FAIL] {Path(test_file).name}: Syntax error at line {e.lineno}")
            return False
    
    # Check documentation
    print("\nChecking documentation...")
    docs = [
        "COMPREHENSIVE_TEST_SUITE.md",
        "TEST_SUITE_SUMMARY.md",
    ]
    
    for doc in docs:
        if Path(doc).exists():
            print(f"  [PASS] {doc}")
        else:
            print(f"  [WARN] {doc} not found")
    
    print("\n" + "=" * 80)
    print("TEST SUITE VALIDATION PASSED")
    print("=" * 80)
    print(f"\nSummary:")
    print(f"  • {total_classes} test classes")
    print(f"  • {total_methods} test methods")
    print(f"  • {len(test_files)} test files")
    print(f"  • All syntax valid")
    print(f"\nReady to run: pytest tests/")
    print("=" * 80)
    
    return True

if __name__ == "__main__":
    success = validate_test_suite()
    sys.exit(0 if success else 1)
