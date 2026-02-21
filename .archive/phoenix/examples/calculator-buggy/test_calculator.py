"""
Tests for calculator module.
These tests will fail due to bugs in calculator.py
"""

import pytest
from calculator import add, subtract, multiply, divide, power, factorial, average, is_even


def test_add():
    """Test addition."""
    assert add(2, 3) == 5
    assert add(-1, 1) == 0
    assert add(0, 0) == 0


def test_subtract():
    """Test subtraction - WILL FAIL."""
    assert subtract(5, 3) == 2
    assert subtract(0, 5) == -5
    assert subtract(10, 10) == 0


def test_multiply():
    """Test multiplication."""
    assert multiply(2, 3) == 6
    assert multiply(-2, 3) == -6
    assert multiply(0, 100) == 0


def test_divide():
    """Test division - WILL FAIL on zero division."""
    assert divide(6, 2) == 3
    assert divide(10, 5) == 2
    with pytest.raises(ZeroDivisionError):
        divide(10, 0)


def test_power():
    """Test power - WILL FAIL."""
    assert power(2, 3) == 8
    assert power(5, 2) == 25
    assert power(10, 0) == 1


def test_factorial():
    """Test factorial - WILL FAIL on 0."""
    assert factorial(5) == 120
    assert factorial(3) == 6
    assert factorial(0) == 1
    assert factorial(1) == 1


def test_average():
    """Test average - WILL FAIL on empty list."""
    assert average([1, 2, 3, 4, 5]) == 3
    assert average([10, 20]) == 15
    with pytest.raises(ZeroDivisionError):
        average([])


def test_is_even():
    """Test even number check."""
    assert is_even(2) == True
    assert is_even(3) == False
    assert is_even(0) == True
    assert is_even(-2) == True
    assert is_even(-3) == False
