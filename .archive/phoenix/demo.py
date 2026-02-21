#!/usr/bin/env python3
"""
Phoenix Demo Script
Demonstrates the self-healing capabilities of Phoenix with the calculator-buggy example.
"""
import os
import sys
from pathlib import Path

# Add phoenix to path
sys.path.insert(0, str(Path(__file__).parent))

from phoenix.observer.test_runner import TestRunner
from phoenix.observer.failure_detector import FailureDetector
from phoenix.core.models import Project


def demo_observer():
    """Demo: Observer detecting failures"""
    print("=" * 80)
    print("DEMO 1: Observer - Test Running & Failure Detection")
    print("=" * 80)
    
    # Setup
    project_path = Path(__file__).parent / "examples" / "calculator-buggy"
    
    print(f"\nProject: {project_path}")
    print(f"Running tests...\n")
    
    # Run tests
    runner = TestRunner(project_path=project_path)
    results = runner.run_tests()
    
    print(f"Tests executed: {results.total_tests}")
    print(f"Tests failed: {results.failed}")
    print(f"Duration: {results.duration:.2f}s\n")
    
    # Detect failures
    if results.failed > 0:
        project = Project(
            name="calculator-buggy",
            local_path=str(project_path),
            language="python"
        )
        
        detector = FailureDetector(
            project_id=project.id,
            project_path=project_path
        )
        
        failures = detector.detect_failures(results)
        
        print(f"Failures Detected!")
        print(f"   Total failures: {len(failures)}")
        if failures:
            for i, failure in enumerate(failures[:3], 1):  # Show first 3
                print(f"\n   Failure {i}:")
                print(f"   Test: {failure.test_name}")
                print(f"   Type: {failure.failure_type.value}")
                print(f"   Error: {failure.error_message[:80]}...")
        
        return failures[0] if failures else None
    else:
        print("[PASS] All tests passed!")
        return None


def demo_critic(failure_event):
    """Demo: Critic diagnosing failures"""
    if not failure_event:
        print("\nSkipping Critic demo - no failures to diagnose")
        return None
    
    print("\n" + "=" * 80)
    print("DEMO 2: Critic - LLM-Based Diagnosis")
    print("=" * 80)
    
    print("\nNote: Critic requires OpenAI/Gemini/Anthropic API keys")
    print("   Set OPENAI_API_KEY, GEMINI_API_KEY, or ANTHROPIC_API_KEY in .env")
    print("   Skipping LLM call in demo mode.\n")
    
    # Mock diagnosis for demo
    print("Critic would analyze:")
    print(f"   - Error: {failure_event.error_message[:80]}...")
    print(f"   - Test: {failure_event.test_name}\n")
    
    print("Expected diagnosis:")
    print("   - Bug type: Logic Error")
    print("   - Root cause: Incorrect operator in calculation")
    print("   - Suggested fix: Change operator or add validation")
    print("   - Confidence: 0.85")


def demo_programmer():
    """Demo: Programmer generating patches"""
    print("\n" + "=" * 80)
    print("DEMO 3: Programmer - Patch Generation")
    print("=" * 80)
    
    print("\nNote: Programmer requires LLM API keys")
    print("   Demonstrating code editing capabilities instead.\n")
    
    from phoenix.programmer.code_editor import CodeEditor
    
    project_path = Path(__file__).parent / "examples" / "calculator-buggy"
    calc_file = project_path / "calculator.py"
    
    editor = CodeEditor(project_path=project_path)
    
    # Show original content
    print(f"Reading: {calc_file}")
    content = editor.read_file(str(calc_file))
    
    # Find the buggy line
    lines = content.split('\n')
    for i, line in enumerate(lines[:20], 1):
        if 'def add' in line or 'return' in line:
            print(f"   Line {i}: {line}")
    
    print("\nPatch would:")
    print("   - Fix operator errors")
    print("   - Add input validation")
    print("   - Preserve existing logic")


def demo_validator():
    """Demo: Validator testing patches safely"""
    print("\n" + "=" * 80)
    print("DEMO 4: Validator - Safe Patch Testing")
    print("=" * 80)
    
    print("\nNote: Sandbox requires Docker")
    print("   Demonstrating validation logic instead.\n")
    
    from phoenix.observer.test_runner import TestRunner
    
    project_path = Path(__file__).parent / "examples" / "calculator-buggy"
    
    print("Sandbox would:")
    print("   1. Create isolated Docker container")
    print("   2. Copy project files")
    print("   3. Apply patch")
    print("   4. Run tests in isolation")
    print("   5. Report results without affecting original\n")
    
    print("Running tests in current environment (demo):")
    runner = TestRunner(project_path=project_path)
    results = runner.run_tests()
    print(f"   Tests: {results.total_tests} total, {results.failed} failed")


def demo_orchestrator():
    """Demo: Orchestrator coordinating workflow"""
    print("\n" + "=" * 80)
    print("DEMO 5: Orchestrator - Complete Remediation Loop")
    print("=" * 80)
    
    print("\nFull workflow:")
    print("   1. Observer: Detect test failures")
    print("   2. ⏩ Critic: Diagnose with LLM (requires API key)")
    print("   3. ⏩ Programmer: Generate patch (requires API key)")
    print("   4. ⏩ Validator: Test in sandbox (requires Docker)")
    print("   5. ⏩ Integrator: Apply patch & commit (if validated)")
    print("   6. ⏩ Knowledge: Store experience for learning\n")
    
    print("Orchestrator manages:")
    print("   - Retry policies (max 3 attempts)")
    print("   - Timeout handling")
    print("   - Error recovery")
    print("   - Metrics tracking")


def demo_knowledge():
    """Demo: Knowledge Base learning from experience"""
    print("\n" + "=" * 80)
    print("DEMO 6: Knowledge Base - Learning from Experience")
    print("=" * 80)
    
    print("\nExperience Store:")
    print("   - Stores successful remediation patterns")
    print("   - Uses vector similarity for matching")
    print("   - Provides few-shot examples to LLMs\n")
    
    print("Learning loop:")
    print("   1. Fix applied successfully")
    print("   2. Pattern extracted (error → diagnosis → patch)")
    print("   3. Embedded for similarity search")
    print("   4. Retrieved for similar future failures")


def main():
    """Run all demos"""
    print("\n")
    print("=" * 80)
    print("                   PHOENIX FRAMEWORK DEMO")
    print("              Self-Healing Agentic AI System")
    print("=" * 80)
    print()
    
    # Check environment
    env_file = Path(__file__).parent / ".env"
    if not env_file.exists():
        print("Warning: .env file not found")
        print("   Copy .env.example to .env and configure API keys for full functionality\n")
    
    # Run demos
    failure = demo_observer()
    demo_critic(failure)
    demo_programmer()
    demo_validator()
    demo_orchestrator()
    demo_knowledge()
    
    # Summary
    print("\n" + "=" * 80)
    print("SUMMARY")
    print("=" * 80)
    print("""
Phoenix demonstrates:
- Autonomous test execution and failure detection
- Multi-LLM diagnosis (OpenAI, Gemini, Claude)
- Automated patch generation with self-refine
- Safe Docker sandbox validation
- Git integration with rollback support
- Experience-based learning

Next steps:
1. Add API keys to .env (OPENAI_API_KEY, etc.)
2. Install Docker for sandbox validation
3. Start API server: python -m phoenix.api.main
4. Try: POST /projects/{id}/run for full remediation

Documentation:
- QUICKSTART.md  - 10-minute setup guide
- USAGE.md       - Complete API reference
- ARCHITECTURE.md - System design & diagrams
""")
    
    print("=" * 80)
    print("Demo complete! Phoenix is ready for self-healing AI.\n")


if __name__ == "__main__":
    main()
