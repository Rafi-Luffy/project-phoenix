# Example Projects for Phoenix

This directory contains sample Python projects with deliberate bugs for testing Phoenix's self-healing capabilities.

## Projects

### 1. calculator-buggy
A simple calculator with various bugs:
- Off-by-one errors
- Null/None handling issues
- Logic errors
- Boundary cases

### 2. data-processor-buggy
A data processing application with:
- Type mismatches
- Import errors
- Configuration issues

## Usage

```bash
# Register a project with Phoenix
curl -X POST http://localhost:8000/projects \
  -H "Content-Type: application/json" \
  -d '{
    "name": "calculator-buggy",
    "local_path": "/path/to/examples/calculator-buggy",
    "test_command": "pytest"
  }'

# Trigger Phoenix remediation
curl -X POST http://localhost:8000/projects/{project_id}/run
```

Phoenix will:
1. Detect the failing tests
2. Diagnose the bugs
3. Generate and test patches
4. Apply successful fixes automatically
