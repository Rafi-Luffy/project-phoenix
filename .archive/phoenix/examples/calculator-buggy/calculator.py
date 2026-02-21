"""
Calculator module with deliberate bugs for Phoenix to fix.
"""


def add(a, b):
    """Add two numbers."""
    return a + b


def subtract(a, b):
    """Subtract b from a."""
    # BUG: Wrong order
    return b - a  # Should be: a - b


def multiply(a, b):
    """Multiply two numbers."""
    return a * b


def divide(a, b):
    """Divide a by b."""
    # BUG: No zero division handling
    return a / b  # Should check if b == 0


def power(base, exponent):
    """Raise base to exponent."""
    # BUG: Off-by-one error
    result = 1
    for i in range(exponent - 1):  # Should be range(exponent)
        result *= base
    return result


def factorial(n):
    """Calculate factorial of n."""
    # BUG: Doesn't handle n=0 correctly
    if n == 1:  # Should be: if n <= 1
        return 1
    return n * factorial(n - 1)


def average(numbers):
    """Calculate average of numbers."""
    # BUG: Doesn't handle empty list
    return sum(numbers) / len(numbers)  # Should check if numbers is empty


def is_even(n):
    """Check if number is even."""
    # BUG: Doesn't handle negative numbers correctly
    return n % 2 == 0  # Works but logic could be clearer
