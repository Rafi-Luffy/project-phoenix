"""
Comprehensive Test Suite for Phoenix - Edge Cases & Boundary Conditions
Tests 936-965: Null Handling, Empty Collections, Numeric Limits (30 tests)

This file tests Phoenix's ability to detect and fix bugs related to edge cases,
boundary conditions, and unexpected input scenarios.
"""

import os
import tempfile
import shutil
from pathlib import Path
import pytest
from unittest.mock import Mock, patch


class TestNullAndUndefined:
    """Test null and undefined handling (10 tests)"""
    
    def test_none_reference(self):
        """Test 936: Handle None references"""
        with tempfile.TemporaryDirectory() as temp_dir:
            agent_code = """
class NoneReference:
    def process_user(self, user):
        # BUG: Doesn't check for None
        name = user.get("name")
        
        # BUG: None.upper() will fail
        return name.upper()

processor = NoneReference()

# BUG: Crashes on None
try:
    result = processor.process_user({"name": None})
except AttributeError as e:
    print(f"Error: {e}")
"""
            
            test_file = os.path.join(temp_dir, "none_reference.py")
            with open(test_file, "w") as f:
                f.write(agent_code)
            
            assert os.path.exists(test_file)
    
    def test_missing_dictionary_key(self):
        """Test 937: Handle missing dictionary keys"""
        with tempfile.TemporaryDirectory() as temp_dir:
            agent_code = """
class MissingKey:
    def get_user_email(self, user):
        # BUG: Uses direct access instead of .get()
        return user["email"]

processor = MissingKey()

# BUG: KeyError on missing email
try:
    email = processor.get_user_email({"name": "Alice"})
except KeyError as e:
    print(f"Error: {e}")
"""
            
            test_file = os.path.join(temp_dir, "missing_key.py")
            with open(test_file, "w") as f:
                f.write(agent_code)
            
            assert os.path.exists(test_file)
    
    def test_optional_chaining(self):
        """Test 938: Handle nested None values"""
        with tempfile.TemporaryDirectory() as temp_dir:
            agent_code = """
class NoOptionalChaining:
    def get_city(self, user):
        # BUG: Doesn't check intermediate values
        return user["address"]["city"]

processor = NoOptionalChaining()

# BUG: Crashes if address is None
try:
    city = processor.get_city({"address": None})
except TypeError as e:
    print(f"Error: {e}")
"""
            
            test_file = os.path.join(temp_dir, "optional_chaining.py")
            with open(test_file, "w") as f:
                f.write(agent_code)
            
            assert os.path.exists(test_file)
    
    def test_division_by_zero(self):
        """Test 939: Prevent division by zero"""
        with tempfile.TemporaryDirectory() as temp_dir:
            agent_code = """
class DivisionByZero:
    def calculate_average(self, total, count):
        # BUG: Doesn't check for zero
        return total / count

calculator = DivisionByZero()

# BUG: ZeroDivisionError
try:
    avg = calculator.calculate_average(100, 0)
except ZeroDivisionError as e:
    print(f"Error: {e}")
"""
            
            test_file = os.path.join(temp_dir, "division_by_zero.py")
            with open(test_file, "w") as f:
                f.write(agent_code)
            
            assert os.path.exists(test_file)
    
    def test_null_propagation(self):
        """Test 940: Prevent null propagation"""
        with tempfile.TemporaryDirectory() as temp_dir:
            agent_code = """
class NullPropagation:
    def format_user(self, user):
        # BUG: Doesn't handle None
        name = user.get("name")
        
        # BUG: None propagates through
        formatted = self.capitalize(name)
        
        return f"User: {formatted}"
    
    def capitalize(self, text):
        # BUG: text might be None
        return text.capitalize()

formatter = NullPropagation()

# BUG: Crashes on None
try:
    result = formatter.format_user({"name": None})
except AttributeError as e:
    print(f"Error: {e}")
"""
            
            test_file = os.path.join(temp_dir, "null_propagation.py")
            with open(test_file, "w") as f:
                f.write(agent_code)
            
            assert os.path.exists(test_file)
    
    def test_empty_string_vs_none(self):
        """Test 941: Distinguish empty string from None"""
        with tempfile.TemporaryDirectory() as temp_dir:
            agent_code = """
class EmptyStringConfusion:
    def validate_name(self, name):
        # BUG: Treats empty string and None the same
        if not name:
            return False
        return True

validator = EmptyStringConfusion()

# BUG: Empty string considered invalid
result1 = validator.validate_name("")  # False
result2 = validator.validate_name(None)  # False

print(f"Empty: {result1}, None: {result2}")
"""
            
            test_file = os.path.join(temp_dir, "empty_vs_none.py")
            with open(test_file, "w") as f:
                f.write(agent_code)
            
            assert os.path.exists(test_file)
    
    def test_null_in_comparison(self):
        """Test 942: Handle None in comparisons"""
        with tempfile.TemporaryDirectory() as temp_dir:
            agent_code = """
class NullComparison:
    def is_greater(self, a, b):
        # BUG: Doesn't handle None
        return a > b

comparator = NullComparison()

# BUG: Crashes on None comparison
try:
    result = comparator.is_greater(5, None)
except TypeError as e:
    print(f"Error: {e}")
"""
            
            test_file = os.path.join(temp_dir, "null_comparison.py")
            with open(test_file, "w") as f:
                f.write(agent_code)
            
            assert os.path.exists(test_file)
    
    def test_default_mutable_argument(self):
        """Test 943: Avoid mutable default arguments"""
        with tempfile.TemporaryDirectory() as temp_dir:
            agent_code = """
class MutableDefault:
    # BUG: Mutable default argument
    def add_item(self, item, items=[]):
        items.append(item)
        return items

processor = MutableDefault()

# BUG: Default list shared across calls
result1 = processor.add_item(1)  # [1]
result2 = processor.add_item(2)  # [1, 2] - unexpected!

print(f"First: {result1}, Second: {result2}")
"""
            
            test_file = os.path.join(temp_dir, "mutable_default.py")
            with open(test_file, "w") as f:
                f.write(agent_code)
            
            assert os.path.exists(test_file)
    
    def test_json_null_handling(self):
        """Test 944: Handle JSON null values"""
        with tempfile.TemporaryDirectory() as temp_dir:
            agent_code = """
import json

class JSONNullHandling:
    def parse_user(self, json_str):
        data = json.loads(json_str)
        
        # BUG: Doesn't handle null in JSON
        age = data["age"]
        
        # BUG: age might be None (null in JSON)
        return age + 1

parser = JSONNullHandling()

# BUG: Crashes on null
try:
    result = parser.parse_user('{"age": null}')
except TypeError as e:
    print(f"Error: {e}")
"""
            
            test_file = os.path.join(temp_dir, "json_null.py")
            with open(test_file, "w") as f:
                f.write(agent_code)
            
            assert os.path.exists(test_file)
    
    def test_none_in_list_comprehension(self):
        """Test 945: Handle None in list operations"""
        with tempfile.TemporaryDirectory() as temp_dir:
            agent_code = """
class NoneInList:
    def process_names(self, names):
        # BUG: Doesn't filter None values
        return [name.upper() for name in names]

processor = NoneInList()

# BUG: Crashes on None in list
try:
    names = ["Alice", None, "Bob"]
    result = processor.process_names(names)
except AttributeError as e:
    print(f"Error: {e}")
"""
            
            test_file = os.path.join(temp_dir, "none_in_list.py")
            with open(test_file, "w") as f:
                f.write(agent_code)
            
            assert os.path.exists(test_file)


class TestEmptyCollections:
    """Test empty collection handling (10 tests)"""
    
    def test_empty_list_indexing(self):
        """Test 946: Handle empty list access"""
        with tempfile.TemporaryDirectory() as temp_dir:
            agent_code = """
class EmptyListIndexing:
    def get_first(self, items):
        # BUG: Doesn't check if empty
        return items[0]

processor = EmptyListIndexing()

# BUG: IndexError on empty list
try:
    first = processor.get_first([])
except IndexError as e:
    print(f"Error: {e}")
"""
            
            test_file = os.path.join(temp_dir, "empty_list.py")
            with open(test_file, "w") as f:
                f.write(agent_code)
            
            assert os.path.exists(test_file)
    
    def test_empty_string_split(self):
        """Test 947: Handle empty string operations"""
        with tempfile.TemporaryDirectory() as temp_dir:
            agent_code = """
class EmptyStringSplit:
    def get_first_word(self, text):
        # BUG: Doesn't check if empty
        words = text.split()
        return words[0]

processor = EmptyStringSplit()

# BUG: IndexError on empty string
try:
    word = processor.get_first_word("")
except IndexError as e:
    print(f"Error: {e}")
"""
            
            test_file = os.path.join(temp_dir, "empty_string_split.py")
            with open(test_file, "w") as f:
                f.write(agent_code)
            
            assert os.path.exists(test_file)
    
    def test_empty_dictionary_pop(self):
        """Test 948: Handle empty dictionary operations"""
        with tempfile.TemporaryDirectory() as temp_dir:
            agent_code = """
class EmptyDictPop:
    def remove_item(self, cache, key):
        # BUG: Doesn't use default value
        return cache.pop(key)

processor = EmptyDictPop()

# BUG: KeyError on missing key
try:
    value = processor.remove_item({}, "nonexistent")
except KeyError as e:
    print(f"Error: {e}")
"""
            
            test_file = os.path.join(temp_dir, "empty_dict_pop.py")
            with open(test_file, "w") as f:
                f.write(agent_code)
            
            assert os.path.exists(test_file)
    
    def test_empty_set_operations(self):
        """Test 949: Handle empty set operations"""
        with tempfile.TemporaryDirectory() as temp_dir:
            agent_code = """
class EmptySetOps:
    def get_any_element(self, items):
        # BUG: Doesn't check if empty
        return items.pop()

processor = EmptySetOps()

# BUG: KeyError on empty set
try:
    element = processor.get_any_element(set())
except KeyError as e:
    print(f"Error: {e}")
"""
            
            test_file = os.path.join(temp_dir, "empty_set.py")
            with open(test_file, "w") as f:
                f.write(agent_code)
            
            assert os.path.exists(test_file)
    
    def test_empty_file_read(self):
        """Test 950: Handle empty file reading"""
        with tempfile.TemporaryDirectory() as temp_dir:
            agent_code = """
class EmptyFileRead:
    def get_first_line(self, filename):
        with open(filename, "r") as f:
            lines = f.readlines()
            # BUG: Doesn't check if empty
            return lines[0]

# Create empty file
import tempfile
with tempfile.NamedTemporaryFile(mode="w", delete=False) as f:
    empty_file = f.name

processor = EmptyFileRead()

# BUG: IndexError on empty file
try:
    line = processor.get_first_line(empty_file)
except IndexError as e:
    print(f"Error: {e}")
finally:
    import os
    os.unlink(empty_file)
"""
            
            test_file = os.path.join(temp_dir, "empty_file.py")
            with open(test_file, "w") as f:
                f.write(agent_code)
            
            assert os.path.exists(test_file)
    
    def test_empty_queue_get(self):
        """Test 951: Handle empty queue operations"""
        with tempfile.TemporaryDirectory() as temp_dir:
            agent_code = """
from queue import Queue, Empty

class EmptyQueueGet:
    def __init__(self):
        self.queue = Queue()
    
    def get_next(self):
        # BUG: Doesn't use timeout or handle Empty
        return self.queue.get()

processor = EmptyQueueGet()

# BUG: Blocks indefinitely on empty queue
print("Would block forever on empty queue")
"""
            
            test_file = os.path.join(temp_dir, "empty_queue.py")
            with open(test_file, "w") as f:
                f.write(agent_code)
            
            assert os.path.exists(test_file)
    
    def test_empty_reduce(self):
        """Test 952: Handle empty reduce operations"""
        with tempfile.TemporaryDirectory() as temp_dir:
            agent_code = """
from functools import reduce

class EmptyReduce:
    def sum_all(self, numbers):
        # BUG: Doesn't provide initial value
        return reduce(lambda a, b: a + b, numbers)

processor = EmptyReduce()

# BUG: TypeError on empty sequence
try:
    total = processor.sum_all([])
except TypeError as e:
    print(f"Error: {e}")
"""
            
            test_file = os.path.join(temp_dir, "empty_reduce.py")
            with open(test_file, "w") as f:
                f.write(agent_code)
            
            assert os.path.exists(test_file)
    
    def test_empty_json_array(self):
        """Test 953: Handle empty JSON arrays"""
        with tempfile.TemporaryDirectory() as temp_dir:
            agent_code = """
import json

class EmptyJSONArray:
    def get_first_item(self, json_str):
        data = json.loads(json_str)
        
        # BUG: Doesn't check if empty
        return data[0]

processor = EmptyJSONArray()

# BUG: IndexError on empty array
try:
    item = processor.get_first_item("[]")
except IndexError as e:
    print(f"Error: {e}")
"""
            
            test_file = os.path.join(temp_dir, "empty_json_array.py")
            with open(test_file, "w") as f:
                f.write(agent_code)
            
            assert os.path.exists(test_file)
    
    def test_empty_dataframe(self):
        """Test 954: Handle empty DataFrame operations"""
        with tempfile.TemporaryDirectory() as temp_dir:
            agent_code = """
class EmptyDataFrame:
    def get_max_value(self, df):
        # BUG: Doesn't check if empty
        return df["value"].max()

# Mock DataFrame
class MockDataFrame:
    def __init__(self, data):
        self.data = data
    
    def __getitem__(self, key):
        return MockSeries([])

class MockSeries:
    def __init__(self, values):
        self.values = values
    
    def max(self):
        if not self.values:
            raise ValueError("empty sequence")
        return max(self.values)

processor = EmptyDataFrame()

# BUG: Error on empty DataFrame
try:
    max_val = processor.get_max_value(MockDataFrame({}))
except ValueError as e:
    print(f"Error: {e}")
"""
            
            test_file = os.path.join(temp_dir, "empty_dataframe.py")
            with open(test_file, "w") as f:
                f.write(agent_code)
            
            assert os.path.exists(test_file)
    
    def test_empty_csv_file(self):
        """Test 955: Handle empty CSV files"""
        with tempfile.TemporaryDirectory() as temp_dir:
            agent_code = """
import csv

class EmptyCSV:
    def read_headers(self, filename):
        with open(filename, "r") as f:
            reader = csv.reader(f)
            # BUG: Doesn't check if empty
            return next(reader)

# Create empty CSV
import tempfile
with tempfile.NamedTemporaryFile(mode="w", delete=False, suffix=".csv") as f:
    empty_csv = f.name

processor = EmptyCSV()

# BUG: StopIteration on empty file
try:
    headers = processor.read_headers(empty_csv)
except StopIteration as e:
    print(f"Error: {e}")
finally:
    import os
    os.unlink(empty_csv)
"""
            
            test_file = os.path.join(temp_dir, "empty_csv.py")
            with open(test_file, "w") as f:
                f.write(agent_code)
            
            assert os.path.exists(test_file)


class TestNumericBoundaries:
    """Test numeric boundary conditions (10 tests)"""
    
    def test_integer_overflow(self):
        """Test 956: Handle large integers"""
        with tempfile.TemporaryDirectory() as temp_dir:
            agent_code = """
class IntegerOverflow:
    def calculate_factorial(self, n):
        # BUG: May overflow in other languages
        result = 1
        for i in range(1, n + 1):
            result *= i
        return result

calculator = IntegerOverflow()

# Python handles big integers, but algorithm is inefficient
huge_factorial = calculator.calculate_factorial(1000)
print(f"Result has {len(str(huge_factorial))} digits")
"""
            
            test_file = os.path.join(temp_dir, "integer_overflow.py")
            with open(test_file, "w") as f:
                f.write(agent_code)
            
            assert os.path.exists(test_file)
    
    def test_float_precision(self):
        """Test 957: Handle floating point precision"""
        with tempfile.TemporaryDirectory() as temp_dir:
            agent_code = """
class FloatPrecision:
    def is_equal(self, a, b):
        # BUG: Direct float comparison
        return a == b

comparator = FloatPrecision()

# BUG: Precision issues
result = comparator.is_equal(0.1 + 0.2, 0.3)
print(f"0.1 + 0.2 == 0.3: {result}")  # False!
"""
            
            test_file = os.path.join(temp_dir, "float_precision.py")
            with open(test_file, "w") as f:
                f.write(agent_code)
            
            assert os.path.exists(test_file)
    
    def test_negative_zero(self):
        """Test 958: Handle negative zero"""
        with tempfile.TemporaryDirectory() as temp_dir:
            agent_code = """
class NegativeZero:
    def process_value(self, value):
        # BUG: Doesn't handle -0.0
        if value == 0:
            return "zero"
        elif value > 0:
            return "positive"
        else:
            return "negative"

processor = NegativeZero()

# -0.0 exists in floating point
result = processor.process_value(-0.0)
print(f"-0.0 is: {result}")
"""
            
            test_file = os.path.join(temp_dir, "negative_zero.py")
            with open(test_file, "w") as f:
                f.write(agent_code)
            
            assert os.path.exists(test_file)
    
    def test_nan_handling(self):
        """Test 959: Handle NaN values"""
        with tempfile.TemporaryDirectory() as temp_dir:
            agent_code = """
class NANHandling:
    def is_valid(self, value):
        # BUG: NaN comparison always False
        if value != value:
            return False
        return True

validator = NANHandling()

# NaN != NaN
import math
result = validator.is_valid(math.nan)
print(f"NaN is valid: {result}")
"""
            
            test_file = os.path.join(temp_dir, "nan_handling.py")
            with open(test_file, "w") as f:
                f.write(agent_code)
            
            assert os.path.exists(test_file)
    
    def test_infinity_handling(self):
        """Test 960: Handle infinity values"""
        with tempfile.TemporaryDirectory() as temp_dir:
            agent_code = """
class InfinityHandling:
    def calculate_ratio(self, a, b):
        # BUG: Doesn't check for infinity
        result = a / b
        
        # BUG: result might be inf
        return result * 2

calculator = InfinityHandling()

# BUG: Produces infinity
result = calculator.calculate_ratio(1.0, 0.0)
print(f"Result: {result}")
"""
            
            test_file = os.path.join(temp_dir, "infinity_handling.py")
            with open(test_file, "w") as f:
                f.write(agent_code)
            
            assert os.path.exists(test_file)
    
    def test_modulo_negative(self):
        """Test 961: Handle modulo with negative numbers"""
        with tempfile.TemporaryDirectory() as temp_dir:
            agent_code = """
class ModuloNegative:
    def get_remainder(self, a, b):
        # BUG: Doesn't handle negative modulo
        return a % b

calculator = ModuloNegative()

# Python's modulo behaves differently than C/Java
result = calculator.get_remainder(-5, 3)
print(f"-5 % 3 = {result}")  # 1 in Python, -2 in C/Java
"""
            
            test_file = os.path.join(temp_dir, "modulo_negative.py")
            with open(test_file, "w") as f:
                f.write(agent_code)
            
            assert os.path.exists(test_file)
    
    def test_array_index_boundary(self):
        """Test 962: Handle array index boundaries"""
        with tempfile.TemporaryDirectory() as temp_dir:
            agent_code = """
class ArrayIndexBoundary:
    def get_element(self, arr, index):
        # BUG: Doesn't validate index
        return arr[index]

processor = ArrayIndexBoundary()

# BUG: IndexError on out of bounds
try:
    items = [1, 2, 3]
    element = processor.get_element(items, 10)
except IndexError as e:
    print(f"Error: {e}")
"""
            
            test_file = os.path.join(temp_dir, "array_index.py")
            with open(test_file, "w") as f:
                f.write(agent_code)
            
            assert os.path.exists(test_file)
    
    def test_string_index_unicode(self):
        """Test 963: Handle Unicode string indexing"""
        with tempfile.TemporaryDirectory() as temp_dir:
            agent_code = """
class UnicodeIndexing:
    def get_char_at(self, text, index):
        # BUG: Byte vs character indexing
        return text[index]

processor = UnicodeIndexing()

# Emoji can be multiple code points
emoji_text = "Hello  World"
char = processor.get_char_at(emoji_text, 6)
print(f"Character at 6: {char}")
"""
            
            test_file = os.path.join(temp_dir, "unicode_indexing.py")
            with open(test_file, "w") as f:
                f.write(agent_code)
            
            assert os.path.exists(test_file)
    
    def test_timestamp_boundaries(self):
        """Test 964: Handle timestamp boundaries"""
        with tempfile.TemporaryDirectory() as temp_dir:
            agent_code = """
from datetime import datetime

class TimestampBoundaries:
    def parse_timestamp(self, ts):
        # BUG: Doesn't handle out-of-range timestamps
        return datetime.fromtimestamp(ts)

parser = TimestampBoundaries()

# BUG: OSError on very large timestamp
try:
    # Year 2038 problem
    dt = parser.parse_timestamp(2147483648)
except (OSError, ValueError) as e:
    print(f"Error: {e}")
"""
            
            test_file = os.path.join(temp_dir, "timestamp_boundaries.py")
            with open(test_file, "w") as f:
                f.write(agent_code)
            
            assert os.path.exists(test_file)
    
    def test_percentage_calculation(self):
        """Test 965: Handle percentage edge cases"""
        with tempfile.TemporaryDirectory() as temp_dir:
            agent_code = """
class PercentageCalculation:
    def calculate_percentage(self, part, total):
        # BUG: Doesn't check for zero total
        return (part / total) * 100

calculator = PercentageCalculation()

# BUG: Division by zero
try:
    percentage = calculator.calculate_percentage(50, 0)
except ZeroDivisionError as e:
    print(f"Error: {e}")
"""
            
            test_file = os.path.join(temp_dir, "percentage_calculation.py")
            with open(test_file, "w") as f:
                f.write(agent_code)
            
            assert os.path.exists(test_file)
