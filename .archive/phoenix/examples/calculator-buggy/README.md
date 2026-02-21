# Calculator Buggy

A simple calculator with deliberate bugs for testing Phoenix's self-healing capabilities.

## Bugs included:
1. `subtract()` - Wrong operand order
2. `divide()` - No zero division handling
3. `power()` - Off-by-one error in loop
4. `factorial()` - Doesn't handle n=0
5. `average()` - Doesn't handle empty list

## Running tests

```bash
pytest test_calculator.py
```

Expected: 4-5 test failures

## Phoenix remediation

Once registered with Phoenix, it will:
1. Detect all test failures
2. Diagnose each bug
3. Generate and validate patches
4. Apply fixes automatically
