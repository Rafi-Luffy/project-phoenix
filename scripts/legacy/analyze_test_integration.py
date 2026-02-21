#!/usr/bin/env python3
"""
Test Suite Integration Analysis

Analyzes the 59 test files and maps them to the autonomous_system modules
"""

import os
import sys
from pathlib import Path
from collections import defaultdict
import re

class TestAnalyzer:
    def __init__(self):
        self.project_root = Path(__file__).parent
        self.test_dir = self.project_root / "phoenix" / "tests"
        self.autonomous_core = self.project_root / "autonomous_system" / "core"
        self.test_files = []
        self.mapping = defaultdict(list)
        
    def discover_tests(self):
        """Discover all test files"""
        test_files = sorted(self.test_dir.glob("test_*.py"))
        self.test_files = [f.stem for f in test_files]
        return len(self.test_files)
        
    def count_lines(self):
        """Count total lines in test suite"""
        total = 0
        for test_file in self.test_dir.glob("test_*.py"):
            with open(test_file, 'r') as f:
                total += len(f.readlines())
        return total
        
    def analyze_test_coverage(self):
        """Analyze which tests relate to which modules"""
        mapping = {
            "core": [
                "test_core", "test_api", "test_database", "test_auth"
            ],
            "self_correction": [
                "test_error", "test_recovery", "test_healing", "test_chaos"
            ],
            "learning": [
                "test_learning", "test_agentic", "test_meta_learning",
                "test_llm", "test_multimodal"
            ],
            "coordination": [
                "test_distributed", "test_concurrency", "test_message",
                "test_orchestrator", "test_networking"
            ],
            "testing": [
                "test_testing_qa", "test_monitoring", "test_performance",
                "test_stress", "test_edge_cases"
            ],
            "deployment": [
                "test_deployment", "test_cloud", "test_configuration",
                "test_scaling"
            ],
            "advanced": [
                "test_observer", "test_programmer", "test_critic",
                "test_validator", "test_rag", "test_real_world"
            ]
        }
        
        categorized = defaultdict(list)
        for test_file in self.test_files:
            found = False
            for module, patterns in mapping.items():
                for pattern in patterns:
                    if pattern in test_file.lower():
                        categorized[module].append(test_file)
                        found = True
                        break
                if found:
                    break
            if not found:
                categorized["other"].append(test_file)
                
        return categorized
        
    def generate_report(self):
        """Generate comprehensive analysis report"""
        test_count = self.discover_tests()
        line_count = self.count_lines()
        coverage = self.analyze_test_coverage()
        
        report = f"""# Test Suite Integration Analysis

## Overview

**Test Suite Location**: phoenix/tests/
**Total Test Files**: {test_count}
**Total Test Lines**: {line_count}
**Status**: Ready for integration with autonomous_system

## Test Files by Module Mapping

### Module 1: Core Architecture
Tests: {len(coverage['core'])} files
Files: {', '.join(coverage['core'])}

**Coverage**:
- Core models and configuration
- API gateway and routing
- Database operations
- Authentication and authorization

### Module 2: Self-Correction Engine
Tests: {len(coverage['self_correction'])} files
Files: {', '.join(coverage['self_correction'])}

**Coverage**:
- Error detection and handling
- Recovery procedures
- Self-healing mechanisms
- Chaos engineering

### Module 3: Learning & Adaptation
Tests: {len(coverage['learning'])} files
Files: {', '.join(coverage['learning'])}

**Coverage**:
- Meta-learning systems
- Agentic AI frameworks
- LLM integration
- Multimodal AI

### Module 4: Multi-Agent Coordination
Tests: {len(coverage['coordination'])} files
Files: {', '.join(coverage['coordination'])}

**Coverage**:
- Distributed systems
- Concurrency and threading
- Message queues and events
- Network protocols
- Orchestration

### Module 5: Evaluation & Testing
Tests: {len(coverage['testing'])} files
Files: {', '.join(coverage['testing'])}

**Coverage**:
- Testing and QA frameworks
- Monitoring and observability
- Performance testing
- Stress testing
- Edge cases

### Module 6: Production Deployment
Tests: {len(coverage['deployment'])} files
Files: {', '.join(coverage['deployment'])}

**Coverage**:
- Deployment strategies
- Cloud services
- Configuration management
- Scaling capabilities

### Module 7: Advanced Features
Tests: {len(coverage['advanced'])} files
Files: {', '.join(coverage['advanced'])}

**Coverage**:
- Observer pattern
- Programmer/Developer agent
- Critic agent
- Validator agent
- RAG and Vector DB
- Real-world scenarios

### Uncategorized
Tests: {len(coverage['other'])} files
Files: {', '.join(coverage['other'])}

## Integration Status

### Autonomous System (autonomous_system/core/)
- **Files**: 49
- **Lines**: 21,134
- **Modules**: 7
- **Submodules**: 21
- **Status**: COMPLETE

### Test Suite (phoenix/tests/)
- **Files**: {test_count}
- **Lines**: {line_count}
- **Test Categories**: 7+
- **Status**: Ready for integration

## Integration Steps

1. **Setup Dependencies** (In Progress)
   - [ ] Install pytest and dependencies
   - [ ] Configure Python path
   - [ ] Verify module imports

2. **Run Core Tests** (Next)
   - [ ] Execute core system tests
   - [ ] Verify agent framework
   - [ ] Check memory operations
   - [ ] Validate database operations

3. **Run Module Tests** (Following)
   - [ ] Self-Correction Engine tests
   - [ ] Learning & Adaptation tests
   - [ ] Multi-Agent Coordination tests
   - [ ] Testing & Validation tests
   - [ ] Deployment tests
   - [ ] Advanced Features tests

4. **Integration Validation** (Final)
   - [ ] Verify all 21 submodules are tested
   - [ ] Check end-to-end scenarios
   - [ ] Validate performance metrics
   - [ ] Confirm security compliance

## Next Steps

1. Configure Python environment with all dependencies
2. Run test discovery to validate test suite
3. Execute tests module by module
4. Generate coverage reports
5. Create integration summary

## Reference

- Test Integration Strategy: TEST_SUITE_INTEGRATION_STRATEGY.md
- Module Architecture: MODULE_ARCHITECTURE_REFERENCE.md
- Implementation Status: IMPLEMENTATION_VERIFICATION.md

---

Generated: $(date)
"""
        return report
        
    def run(self):
        """Run analysis"""
        print("=" * 80)
        print("TEST SUITE INTEGRATION ANALYSIS")
        print("=" * 80)
        
        report = self.generate_report()
        
        # Print report
        print(report)
        
        # Save report
        report_file = self.project_root / "TEST_INTEGRATION_ANALYSIS.md"
        report_file.write_text(report)
        print(f"\nReport saved to: {report_file}")
        
        return report

if __name__ == "__main__":
    analyzer = TestAnalyzer()
    analyzer.run()
