#!/usr/bin/env python3.11
"""
Run full test suite and feed all results to Ollama evolution system for learning
This makes the Ollama model learn and evolve from ALL 1500+ test patterns
"""

import sys
import os
import json
import subprocess
from pathlib import Path

# Add backend to path
sys.path.insert(0, '/Users/rafi/Documents/Projects_OnGoing/Project phoenix/src/backend')

from autonomous_system.core.ollama_evolution import OllamaEvolutionManager

def run_pytest_and_capture():
    """Run pytest and capture all results"""
    print("🧪 Running FULL test suite (1500+ tests)...")
    print("=" * 80)
    
    cmd = [
        sys.executable, '-m', 'pytest', 
        'tests/',
        '--tb=short',
        '--no-cov',
        '-v',
        '--json-report',
        '--json-report-file=/tmp/test_report.json'
    ]
    
    env = os.environ.copy()
    env['PYTHONPATH'] = '/Users/rafi/Documents/Projects_OnGoing/Project phoenix/src/backend'
    
    result = subprocess.run(
        cmd,
        cwd='/Users/rafi/Documents/Projects_OnGoing/Project phoenix',
        capture_output=True,
        text=True,
        env=env
    )
    
    return result.stdout, result.stderr

def extract_test_data_from_output(output):
    """Extract individual test results from pytest output"""
    tests = []
    for line in output.split('\n'):
        if 'PASSED' in line or 'FAILED' in line:
            # Parse test line
            parts = line.split()
            if len(parts) > 0:
                test_name = parts[0].replace('tests/', '').replace('.py', '')
                status = 'PASSED' if 'PASSED' in line else 'FAILED'
                duration = 0
                
                # Extract duration if available
                for i, part in enumerate(parts):
                    if 'ms' in part:
                        try:
                            duration = float(part.replace('ms', ''))
                        except:
                            pass
                
                tests.append({
                    'test_name': test_name,
                    'status': status,
                    'success': status == 'PASSED',
                    'duration_ms': duration
                })
    
    return tests

def feed_tests_to_ollama(manager, tests):
    """Feed all test results to Ollama evolution manager"""
    print(f"\n🧠 Feeding {len(tests)} test results to Ollama evolution system...")
    print("=" * 80)
    
    success_count = 0
    failed_count = 0
    patterns_learned = 0
    
    for i, test in enumerate(tests):
        try:
            # Record test case
            manager.record_test_case(
                test_id=test['test_name'],
                prompt=f"Test: {test['test_name']}",
                response=f"Status: {test['status']}",
                success=test['success'],
                duration_ms=test['duration_ms']
            )
            
            if test['success']:
                success_count += 1
            else:
                failed_count += 1
            
            # Show progress every 100 tests
            if (i + 1) % 100 == 0:
                print(f"   ✓ Processed {i + 1} tests...")
                summary = manager.get_learning_summary()
                patterns_learned = len(summary.get('patterns_learned', {}))
                print(f"     Patterns learned so far: {patterns_learned}")
        
        except Exception as e:
            print(f"   ⚠️  Error recording test {test['test_name']}: {e}")
    
    return success_count, failed_count, patterns_learned

def main():
    # Initialize Ollama evolution manager
    print("\n🚀 Initializing Ollama Evolution System...")
    manager = OllamaEvolutionManager()
    print("✅ Manager initialized")
    
    # Run tests
    print("\n📊 Running complete test suite...")
    stdout, stderr = run_pytest_and_capture()
    
    # Extract test data
    print("\n📝 Extracting test data...")
    tests = extract_test_data_from_output(stdout)
    
    if not tests:
        # Try to parse from stderr
        tests = extract_test_data_from_output(stderr)
    
    print(f"✅ Extracted {len(tests)} tests from output")
    
    if len(tests) == 0:
        print("⚠️  No tests could be parsed, showing sample output:")
        print(stdout[-1000:] if stdout else stderr[-1000:])
        return
    
    # Feed to Ollama
    success, failed, patterns = feed_tests_to_ollama(manager, tests)
    
    # Get final learning summary
    print("\n\n" + "=" * 80)
    print("📚 OLLAMA EVOLUTION LEARNING SUMMARY")
    print("=" * 80)
    
    summary = manager.get_learning_summary()
    
    print(f"\n✅ Tests Processed: {len(tests)}")
    print(f"   - Passed: {success}")
    print(f"   - Failed: {failed}")
    print(f"   - Success Rate: {(success / len(tests) * 100):.1f}%")
    
    print(f"\n🧠 Pattern Learning Results:")
    print(f"   - Total Patterns Learned: {len(summary.get('patterns_learned', {}))}")
    for pattern_type, data in summary.get('patterns_learned', {}).items():
        print(f"     • {pattern_type}: {data.get('count', 0)} instances")
    
    print(f"\n📈 Performance Metrics:")
    metrics = summary.get('performance_metrics', {})
    if metrics:
        avg_duration = sum(m['value'] for m in metrics) / len(metrics) if metrics else 0
        print(f"   - Average Test Duration: {avg_duration:.1f}ms")
        print(f"   - Total Metrics Recorded: {len(metrics)}")
    
    # Get top patterns
    print(f"\n🏆 Top Learned Patterns:")
    top_patterns = manager.get_top_patterns(top_n=5)
    for i, pattern in enumerate(top_patterns, 1):
        print(f"   {i}. {pattern['prompt']}")
        print(f"      Confidence: {pattern.get('confidence_score', 0):.1f}%")
        print(f"      Occurrences: {len(pattern.get('examples', []))}")
    
    # Export learning data
    print(f"\n💾 Exporting learning data...")
    learning_file = manager.export_learning_data()
    print(f"✅ Learning data exported to: {learning_file}")
    
    # Create fine-tuning dataset
    print(f"\n🔧 Creating fine-tuning dataset...")
    dataset_file = manager.create_fine_tuning_dataset()
    print(f"✅ Fine-tuning dataset created: {dataset_file}")
    
    print("\n" + "=" * 80)
    print("✅ OLLAMA MODEL EVOLUTION COMPLETE")
    print("=" * 80)
    print("\n🎯 The Ollama model has learned from all test patterns and is ready!")
    print(f"   Total learning data points: {len(tests)}")
    print(f"   Patterns discovered: {len(summary.get('patterns_learned', {}))}")
    print(f"   Evolution files: {learning_file}, {dataset_file}")

if __name__ == '__main__':
    main()
