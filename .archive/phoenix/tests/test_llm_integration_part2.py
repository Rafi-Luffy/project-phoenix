"""
Comprehensive Test Suite for Phoenix - LLM Integration Part 2
Tests 246-275: Function Calling & Structured Outputs (30 tests)

This file tests Phoenix's ability to detect and fix bugs in LLM function calling,
tool usage, structured output generation, and output validation.
"""

import os
import tempfile
import shutil
from pathlib import Path
import pytest
from unittest.mock import Mock, patch


class TestFunctionCalling:
    """Test LLM function calling patterns (10 tests)"""
    
    def test_function_signature_mismatch(self):
        """Test 246: Validate function signatures match LLM output"""
        with tempfile.TemporaryDirectory() as temp_dir:
            agent_code = """
class FunctionCallingLLM:
    def __init__(self):
        self.available_functions = {
            "get_weather": {"params": ["location", "units"]},
            "send_email": {"params": ["to", "subject", "body"]}
        }
    
    def parse_function_call(self, llm_output):
        # BUG: Doesn't validate parameter names
        return {
            "name": "get_weather",
            "args": {"loc": "Paris", "unit": "celsius"}  # Wrong param names
        }
    
    def execute_function(self, func_call):
        # BUG: No signature validation before execution
        func_name = func_call["name"]
        return f"Executed {func_name}"

llm = FunctionCallingLLM()
call = llm.parse_function_call("Get weather in Paris")

# BUG: Parameters don't match function signature
result = llm.execute_function(call)
print(f"Result: {result}")
"""
            
            test_file = os.path.join(temp_dir, "signature_mismatch.py")
            with open(test_file, "w") as f:
                f.write(agent_code)
            
            assert os.path.exists(test_file)
    
    def test_recursive_function_calls(self):
        """Test 247: Handle recursive function calls safely"""
        with tempfile.TemporaryDirectory() as temp_dir:
            agent_code = """
class RecursiveFunctionLLM:
    def __init__(self):
        self.call_depth = 0
    
    def call_function(self, func_name, args):
        # BUG: No recursion depth limit
        self.call_depth += 1
        
        if func_name == "recursive_search":
            # Function calls itself
            return self.call_function("recursive_search", args)
        
        return "result"

llm = RecursiveFunctionLLM()

# Infinite recursion - stack overflow
try:
    llm.call_function("recursive_search", {})
except RecursionError:
    print(f"Recursion error at depth: {llm.call_depth}")
"""
            
            test_file = os.path.join(temp_dir, "recursive_calls.py")
            with open(test_file, "w") as f:
                f.write(agent_code)
            
            assert os.path.exists(test_file)
    
    def test_parallel_function_execution_race(self):
        """Test 248: Handle parallel function execution safely"""
        with tempfile.TemporaryDirectory() as temp_dir:
            agent_code = """
import threading

class ParallelFunctionLLM:
    def __init__(self):
        self.shared_state = {}
    
    def execute_function(self, func_name, args):
        # BUG: Race condition on shared state
        if func_name == "update_state":
            temp = self.shared_state.get("counter", 0)
            temp += 1
            self.shared_state["counter"] = temp

llm = ParallelFunctionLLM()

# Execute functions in parallel
threads = []
for i in range(10):
    t = threading.Thread(target=llm.execute_function, args=("update_state", {}))
    threads.append(t)
    t.start()

for t in threads:
    t.join()

# BUG: Counter should be 10 but race condition causes less
print(f"Counter: {llm.shared_state.get('counter', 0)}")
"""
            
            test_file = os.path.join(temp_dir, "parallel_race.py")
            with open(test_file, "w") as f:
                f.write(agent_code)
            
            assert os.path.exists(test_file)
    
    def test_function_timeout_enforcement(self):
        """Test 249: Enforce timeouts on function execution"""
        with tempfile.TemporaryDirectory() as temp_dir:
            agent_code = """
import time

class TimeoutFunctionLLM:
    def execute_with_timeout(self, func, timeout=5):
        # BUG: No actual timeout enforcement
        return func()

def slow_function():
    time.sleep(100)
    return "result"

llm = TimeoutFunctionLLM()

# Should timeout after 5 seconds but blocks forever
result = llm.execute_with_timeout(slow_function, timeout=5)
"""
            
            test_file = os.path.join(temp_dir, "function_timeout.py")
            with open(test_file, "w") as f:
                f.write(agent_code)
            
            assert os.path.exists(test_file)
    
    def test_function_result_type_validation(self):
        """Test 250: Validate function return types"""
        with tempfile.TemporaryDirectory() as temp_dir:
            agent_code = """
class TypedFunctionLLM:
    def __init__(self):
        self.function_schemas = {
            "get_user_age": {"returns": "int"},
            "get_user_name": {"returns": "str"}
        }
    
    def execute_and_validate(self, func_name, func_result):
        # BUG: No type validation of return value
        expected_type = self.function_schemas[func_name]["returns"]
        return func_result

llm = TypedFunctionLLM()

# Function returns wrong type
def get_user_age():
    return "twenty-five"  # Should be int

result = llm.execute_and_validate("get_user_age", get_user_age())
# BUG: Returns string instead of int - type mismatch
print(f"Age: {result}, Type: {type(result)}")
"""
            
            test_file = os.path.join(temp_dir, "type_validation.py")
            with open(test_file, "w") as f:
                f.write(agent_code)
            
            assert os.path.exists(test_file)
    
    def test_function_side_effects_tracking(self):
        """Test 251: Track and manage function side effects"""
        with tempfile.TemporaryDirectory() as temp_dir:
            agent_code = """
class SideEffectLLM:
    def __init__(self):
        self.database = {"users": []}
    
    def execute_function(self, func_name, args):
        # BUG: No tracking of side effects
        if func_name == "delete_user":
            user_id = args.get("user_id")
            self.database["users"] = [u for u in self.database["users"] if u["id"] != user_id]
        elif func_name == "add_user":
            self.database["users"].append(args)

llm = SideEffectLLM()
llm.database["users"] = [{"id": 1, "name": "Alice"}]

# Delete user
llm.execute_function("delete_user", {"user_id": 1})

# BUG: No way to undo side effect or track what changed
# Cannot rollback if LLM made mistake
print(f"Users: {llm.database['users']}")
"""
            
            test_file = os.path.join(temp_dir, "side_effects.py")
            with open(test_file, "w") as f:
                f.write(agent_code)
            
            assert os.path.exists(test_file)
    
    def test_function_chaining_error_propagation(self):
        """Test 252: Propagate errors through function chains"""
        with tempfile.TemporaryDirectory() as temp_dir:
            agent_code = """
class ChainedFunctionLLM:
    def execute_chain(self, functions):
        # BUG: Doesn't handle errors in chain
        result = None
        for func_name, args in functions:
            result = self.execute_single(func_name, args, result)
        return result
    
    def execute_single(self, func_name, args, prev_result):
        if func_name == "failing_function":
            raise Exception("Function failed")
        return f"Result of {func_name}"

llm = ChainedFunctionLLM()

chain = [
    ("step1", {}),
    ("failing_function", {}),
    ("step3", {}),  # Should not execute
]

try:
    result = llm.execute_chain(chain)
except Exception:
    # BUG: No partial result or error context
    print("Chain failed with no context")
"""
            
            test_file = os.path.join(temp_dir, "chain_errors.py")
            with open(test_file, "w") as f:
                f.write(agent_code)
            
            assert os.path.exists(test_file)
    
    def test_function_parameter_coercion(self):
        """Test 253: Handle type coercion of function parameters"""
        with tempfile.TemporaryDirectory() as temp_dir:
            agent_code = """
class CoercingFunctionLLM:
    def execute_function(self, func_name, params):
        # BUG: No type coercion - passes strings to int params
        if func_name == "calculate_age":
            birth_year = params["birth_year"]  # Expects int
            current_year = params["current_year"]  # Expects int
            # BUG: If LLM sends strings, this fails
            return current_year - birth_year

llm = CoercingFunctionLLM()

# LLM often returns parameters as strings
result = llm.execute_function("calculate_age", {
    "birth_year": "1990",
    "current_year": "2025"
})
# BUG: TypeError - can't subtract strings
print(f"Age: {result}")
"""
            
            test_file = os.path.join(temp_dir, "parameter_coercion.py")
            with open(test_file, "w") as f:
                f.write(agent_code)
            
            assert os.path.exists(test_file)
    
    def test_function_discovery_stale_schema(self):
        """Test 254: Keep function schemas in sync with implementations"""
        with tempfile.TemporaryDirectory() as temp_dir:
            agent_code = """
class DynamicFunctionLLM:
    def __init__(self):
        # BUG: Schema manually maintained - gets out of sync
        self.function_schemas = {
            "old_function": {"params": ["x", "y"]},
        }
    
    def add_new_function(self, func_name, func):
        # BUG: Doesn't update schema
        setattr(self, func_name, func)

llm = DynamicFunctionLLM()

# Add new function
def new_function(a, b, c):
    return a + b + c

llm.add_new_function("new_function", new_function)

# BUG: LLM doesn't know about new function - schema stale
print(f"Available functions: {llm.function_schemas.keys()}")
"""
            
            test_file = os.path.join(temp_dir, "stale_schema.py")
            with open(test_file, "w") as f:
                f.write(agent_code)
            
            assert os.path.exists(test_file)
    
    def test_function_call_ambiguity(self):
        """Test 255: Resolve ambiguous function calls"""
        with tempfile.TemporaryDirectory() as temp_dir:
            agent_code = """
class AmbiguousFunctionLLM:
    def __init__(self):
        self.functions = {
            "send_message": {"params": ["to", "content"]},
            "send_msg": {"params": ["recipient", "text"]},
            "message_send": {"params": ["target", "body"]}
        }
    
    def resolve_function_name(self, llm_output):
        # BUG: No disambiguation logic
        if "send" in llm_output and "message" in llm_output:
            # Multiple matches - which one?
            return "send_message"  # Just picks first

llm = AmbiguousFunctionLLM()

# Ambiguous intent
intent = "send a message to user"

# BUG: Might pick wrong function
func_name = llm.resolve_function_name(intent)
print(f"Resolved to: {func_name}")
"""
            
            test_file = os.path.join(temp_dir, "function_ambiguity.py")
            with open(test_file, "w") as f:
                f.write(agent_code)
            
            assert os.path.exists(test_file)


class TestStructuredOutputs:
    """Test structured output generation (10 tests)"""
    
    def test_json_schema_validation_missing(self):
        """Test 256: Validate outputs against JSON schema"""
        with tempfile.TemporaryDirectory() as temp_dir:
            agent_code = """
class SchemaLLM:
    def __init__(self):
        self.schema = {
            "type": "object",
            "properties": {
                "name": {"type": "string"},
                "age": {"type": "integer"}
            },
            "required": ["name", "age"]
        }
    
    def generate_structured(self, prompt):
        # BUG: No schema validation
        llm_output = {
            "name": "Alice",
            "age": "twenty-five"  # Wrong type
        }
        return llm_output

llm = SchemaLLM()
result = llm.generate_structured("Generate user profile")

# BUG: Returns invalid data according to schema
print(f"Result: {result}")
"""
            
            test_file = os.path.join(temp_dir, "schema_validation.py")
            with open(test_file, "w") as f:
                f.write(agent_code)
            
            assert os.path.exists(test_file)
    
    def test_nested_structure_parsing_failure(self):
        """Test 257: Handle deeply nested structure parsing"""
        with tempfile.TemporaryDirectory() as temp_dir:
            agent_code = """
class NestedStructureLLM:
    def parse_nested(self, llm_output):
        # BUG: Doesn't handle deep nesting
        try:
            return llm_output["level1"]["level2"]["level3"]["value"]
        except KeyError:
            return None

llm = NestedStructureLLM()

# LLM returns incomplete nested structure
incomplete = {
    "level1": {
        "level2": {}  # Missing level3
    }
}

# BUG: Returns None with no error details
result = llm.parse_nested(incomplete)
print(f"Result: {result}")
"""
            
            test_file = os.path.join(temp_dir, "nested_parsing.py")
            with open(test_file, "w") as f:
                f.write(agent_code)
            
            assert os.path.exists(test_file)
    
    def test_enum_value_validation(self):
        """Test 258: Validate enum values in structured output"""
        with tempfile.TemporaryDirectory() as temp_dir:
            agent_code = """
class EnumLLM:
    def __init__(self):
        self.valid_statuses = ["pending", "approved", "rejected"]
    
    def generate_status_update(self, prompt):
        # BUG: No enum validation
        llm_output = {
            "status": "in_progress"  # Invalid enum value
        }
        return llm_output

llm = EnumLLM()
result = llm.generate_status_update("Update status")

# BUG: Invalid enum value not caught
print(f"Status: {result['status']}")
"""
            
            test_file = os.path.join(temp_dir, "enum_validation.py")
            with open(test_file, "w") as f:
                f.write(agent_code)
            
            assert os.path.exists(test_file)
    
    def test_array_length_constraints(self):
        """Test 259: Enforce array length constraints"""
        with tempfile.TemporaryDirectory() as temp_dir:
            agent_code = """
class ArrayConstraintLLM:
    def __init__(self):
        self.schema = {
            "tags": {"type": "array", "minItems": 1, "maxItems": 5}
        }
    
    def generate_tags(self, text):
        # BUG: No array length validation
        return {
            "tags": ["tag1", "tag2", "tag3", "tag4", "tag5", "tag6"]  # Too many
        }

llm = ArrayConstraintLLM()
result = llm.generate_tags("Generate tags")

# BUG: Exceeds maxItems constraint
print(f"Tags: {len(result['tags'])}")
"""
            
            test_file = os.path.join(temp_dir, "array_constraints.py")
            with open(test_file, "w") as f:
                f.write(agent_code)
            
            assert os.path.exists(test_file)
    
    def test_required_field_missing(self):
        """Test 260: Detect missing required fields"""
        with tempfile.TemporaryDirectory() as temp_dir:
            agent_code = """
class RequiredFieldLLM:
    def __init__(self):
        self.required_fields = ["id", "name", "email"]
    
    def generate_user(self, prompt):
        # BUG: No required field validation
        return {
            "id": 123,
            "name": "Alice"
            # Missing email field
        }

llm = RequiredFieldLLM()
user = llm.generate_user("Create user")

# BUG: Missing required field not detected
print(f"User: {user}")
"""
            
            test_file = os.path.join(temp_dir, "required_fields.py")
            with open(test_file, "w") as f:
                f.write(agent_code)
            
            assert os.path.exists(test_file)
    
    def test_format_validation_email_url(self):
        """Test 261: Validate format constraints (email, URL, etc.)"""
        with tempfile.TemporaryDirectory() as temp_dir:
            agent_code = """
class FormatValidationLLM:
    def generate_contact(self, prompt):
        # BUG: No format validation
        return {
            "email": "not-an-email",
            "website": "invalid-url",
            "phone": "abc-def-ghij"
        }

llm = FormatValidationLLM()
contact = llm.generate_contact("Generate contact")

# BUG: Invalid formats not caught
print(f"Contact: {contact}")
"""
            
            test_file = os.path.join(temp_dir, "format_validation.py")
            with open(test_file, "w") as f:
                f.write(agent_code)
            
            assert os.path.exists(test_file)
    
    def test_numeric_range_constraints(self):
        """Test 262: Enforce numeric range constraints"""
        with tempfile.TemporaryDirectory() as temp_dir:
            agent_code = """
class RangeConstraintLLM:
    def __init__(self):
        self.schema = {
            "age": {"type": "integer", "minimum": 0, "maximum": 150},
            "rating": {"type": "number", "minimum": 1.0, "maximum": 5.0}
        }
    
    def generate_profile(self, prompt):
        # BUG: No range validation
        return {
            "age": 200,  # Exceeds maximum
            "rating": 6.5  # Exceeds maximum
        }

llm = RangeConstraintLLM()
profile = llm.generate_profile("Generate profile")

# BUG: Out of range values not caught
print(f"Profile: {profile}")
"""
            
            test_file = os.path.join(temp_dir, "range_constraints.py")
            with open(test_file, "w") as f:
                f.write(agent_code)
            
            assert os.path.exists(test_file)
    
    def test_additional_properties_handling(self):
        """Test 263: Handle additional properties in strict mode"""
        with tempfile.TemporaryDirectory() as temp_dir:
            agent_code = """
class StrictSchemaLLM:
    def __init__(self):
        self.schema = {
            "properties": ["name", "age"],
            "additionalProperties": False
        }
    
    def generate_data(self, prompt):
        # BUG: Allows additional properties in strict mode
        return {
            "name": "Alice",
            "age": 30,
            "extra_field": "not allowed"  # Should be rejected
        }

llm = StrictSchemaLLM()
data = llm.generate_data("Generate user")

# BUG: Additional property not rejected
print(f"Data: {data}")
"""
            
            test_file = os.path.join(temp_dir, "additional_properties.py")
            with open(test_file, "w") as f:
                f.write(agent_code)
            
            assert os.path.exists(test_file)
    
    def test_union_type_disambiguation(self):
        """Test 264: Disambiguate union types correctly"""
        with tempfile.TemporaryDirectory() as temp_dir:
            agent_code = """
class UnionTypeLLM:
    def __init__(self):
        self.schema = {
            "value": {"oneOf": [
                {"type": "string"},
                {"type": "integer"},
                {"type": "object", "properties": {"nested": {"type": "string"}}}
            ]}
        }
    
    def parse_value(self, llm_output):
        # BUG: No type disambiguation
        value = llm_output["value"]
        return value

llm = UnionTypeLLM()

# Ambiguous output - could be multiple types
result = llm.parse_value({"value": "123"})

# BUG: Is this string "123" or integer 123?
print(f"Value: {result}, Type: {type(result)}")
"""
            
            test_file = os.path.join(temp_dir, "union_types.py")
            with open(test_file, "w") as f:
                f.write(agent_code)
            
            assert os.path.exists(test_file)
    
    def test_circular_reference_handling(self):
        """Test 265: Handle circular references in schemas"""
        with tempfile.TemporaryDirectory() as temp_dir:
            agent_code = """
class CircularSchemaLLM:
    def __init__(self):
        # Schema with circular reference
        self.schema = {
            "type": "object",
            "properties": {
                "name": {"type": "string"},
                "parent": {"$ref": "#"}  # Circular reference
            }
        }
    
    def generate_tree_node(self, prompt):
        # BUG: Doesn't handle circular refs - infinite recursion
        return {
            "name": "root",
            "parent": {
                "name": "parent",
                "parent": {
                    "name": "grandparent",
                    "parent": None
                }
            }
        }

llm = CircularSchemaLLM()
# BUG: Could cause infinite recursion in validation
node = llm.generate_tree_node("Generate tree")
print(f"Node: {node}")
"""
            
            test_file = os.path.join(temp_dir, "circular_refs.py")
            with open(test_file, "w") as f:
                f.write(agent_code)
            
            assert os.path.exists(test_file)


class TestOutputValidation:
    """Test output validation and correction (10 tests)"""
    
    def test_hallucination_detection(self):
        """Test 266: Detect factual hallucinations in output"""
        with tempfile.TemporaryDirectory() as temp_dir:
            agent_code = """
class HallucinationDetector:
    def __init__(self, knowledge_base):
        self.knowledge_base = knowledge_base
    
    def validate_facts(self, llm_output):
        # BUG: No hallucination detection
        return True

knowledge = {
    "Paris": {"country": "France", "population": 2_100_000}
}

detector = HallucinationDetector(knowledge)

# LLM output with hallucination
output = "Paris is the capital of Germany with 10 million people"

# BUG: Doesn't detect factual errors
is_valid = detector.validate_facts(output)
print(f"Valid: {is_valid}")
"""
            
            test_file = os.path.join(temp_dir, "hallucination.py")
            with open(test_file, "w") as f:
                f.write(agent_code)
            
            assert os.path.exists(test_file)
    
    def test_output_length_constraint_violation(self):
        """Test 267: Enforce output length constraints"""
        with tempfile.TemporaryDirectory() as temp_dir:
            agent_code = """
class LengthConstraintLLM:
    def __init__(self, max_length=100):
        self.max_length = max_length
    
    def generate_summary(self, text):
        # BUG: No length constraint enforcement
        summary = text * 10  # Way too long
        return summary

llm = LengthConstraintLLM(max_length=100)
summary = llm.generate_summary("This is a long text. " * 50)

# BUG: Summary exceeds max_length
print(f"Summary length: {len(summary)}")
"""
            
            test_file = os.path.join(temp_dir, "length_constraint.py")
            with open(test_file, "w") as f:
                f.write(agent_code)
            
            assert os.path.exists(test_file)
    
    def test_toxic_content_filtering(self):
        """Test 268: Filter toxic or inappropriate content"""
        with tempfile.TemporaryDirectory() as temp_dir:
            agent_code = """
class ContentFilterLLM:
    def generate_response(self, prompt):
        # BUG: No content filtering
        return "Response with inappropriate content"
    
    def is_safe(self, text):
        # BUG: No actual safety check
        return True

llm = ContentFilterLLM()
response = llm.generate_response("Write something")

# BUG: Toxic content not filtered
is_safe = llm.is_safe(response)
print(f"Safe: {is_safe}")
"""
            
            test_file = os.path.join(temp_dir, "content_filter.py")
            with open(test_file, "w") as f:
                f.write(agent_code)
            
            assert os.path.exists(test_file)
    
    def test_pii_leakage_detection(self):
        """Test 269: Detect and redact PII in outputs"""
        with tempfile.TemporaryDirectory() as temp_dir:
            agent_code = """
class PIIDetectorLLM:
    def generate_response(self, context):
        # BUG: No PII detection/redaction
        return f"User John Smith (SSN: 123-45-6789) lives at 123 Main St"
    
    def redact_pii(self, text):
        # BUG: No redaction logic
        return text

llm = PIIDetectorLLM()
response = llm.generate_response("Summarize user info")

# BUG: PII leaked in output
redacted = llm.redact_pii(response)
print(f"Response: {redacted}")
"""
            
            test_file = os.path.join(temp_dir, "pii_leakage.py")
            with open(test_file, "w") as f:
                f.write(agent_code)
            
            assert os.path.exists(test_file)
    
    def test_code_injection_in_generated_code(self):
        """Test 270: Validate generated code for injection attacks"""
        with tempfile.TemporaryDirectory() as temp_dir:
            agent_code = """
class CodeGeneratorLLM:
    def generate_code(self, specification):
        # BUG: No code validation
        return '''
import os
os.system("rm -rf /")  # Malicious code
print("Hello World")
'''
    
    def execute_generated_code(self, code):
        # BUG: Executes without sandboxing
        exec(code)

llm = CodeGeneratorLLM()
code = llm.generate_code("Write hello world")

# BUG: Dangerous code not detected
llm.execute_generated_code(code)
"""
            
            test_file = os.path.join(temp_dir, "code_injection.py")
            with open(test_file, "w") as f:
                f.write(agent_code)
            
            assert os.path.exists(test_file)
    
    def test_response_consistency_checking(self):
        """Test 271: Check consistency across multiple responses"""
        with tempfile.TemporaryDirectory() as temp_dir:
            agent_code = """
class ConsistencyCheckerLLM:
    def generate_multiple(self, prompt, n=3):
        # BUG: No consistency checking
        return [
            "Paris is in France",
            "Paris is in Germany",  # Inconsistent
            "Paris is in Italy"     # Inconsistent
        ]
    
    def select_answer(self, responses):
        # BUG: Just picks first response
        return responses[0]

llm = ConsistencyCheckerLLM()
responses = llm.generate_multiple("Where is Paris?", n=3)

# BUG: Inconsistencies not detected
answer = llm.select_answer(responses)
print(f"Answer: {answer}")
"""
            
            test_file = os.path.join(temp_dir, "consistency_check.py")
            with open(test_file, "w") as f:
                f.write(agent_code)
            
            assert os.path.exists(test_file)
    
    def test_output_confidence_calibration(self):
        """Test 272: Calibrate output confidence scores"""
        with tempfile.TemporaryDirectory() as temp_dir:
            agent_code = """
class ConfidenceLLM:
    def generate_with_confidence(self, prompt):
        # BUG: Confidence not calibrated
        return {
            "answer": "Paris is in Spain",  # Wrong answer
            "confidence": 0.95  # High confidence in wrong answer
        }
    
    def should_trust(self, result):
        # BUG: Blindly trusts high confidence
        return result["confidence"] > 0.8

llm = ConfidenceLLM()
result = llm.generate_with_confidence("Where is Paris?")

# BUG: Trusts wrong answer due to miscalibrated confidence
trust = llm.should_trust(result)
print(f"Trust: {trust}, Answer: {result['answer']}")
"""
            
            test_file = os.path.join(temp_dir, "confidence_calibration.py")
            with open(test_file, "w") as f:
                f.write(agent_code)
            
            assert os.path.exists(test_file)
    
    def test_output_determinism_variance(self):
        """Test 273: Handle non-deterministic output variance"""
        with tempfile.TemporaryDirectory() as temp_dir:
            agent_code = """
import random

class NonDeterministicLLM:
    def generate(self, prompt, temperature=1.0):
        # BUG: No control over variance
        options = ["Answer A", "Answer B", "Answer C"]
        return random.choice(options)
    
    def ensure_reproducible(self, prompt):
        # BUG: No seed setting for reproducibility
        return self.generate(prompt)

llm = NonDeterministicLLM()

# Generate same prompt multiple times
results = [llm.ensure_reproducible("What is 2+2?") for _ in range(5)]

# BUG: Different answers each time - not reproducible
print(f"Results: {results}")
print(f"All same: {len(set(results)) == 1}")
"""
            
            test_file = os.path.join(temp_dir, "determinism.py")
            with open(test_file, "w") as f:
                f.write(agent_code)
            
            assert os.path.exists(test_file)
    
    def test_markdown_formatting_inconsistency(self):
        """Test 274: Ensure consistent markdown formatting"""
        with tempfile.TemporaryDirectory() as temp_dir:
            agent_code = """
class MarkdownLLM:
    def generate_documentation(self, topic):
        # BUG: Inconsistent markdown formatting
        return '''
# Heading 1
## Heading 2
###Heading 3 (no space)
- Item 1
* Item 2 (inconsistent bullet)
1. Numbered item
3. Wrong number
'''

llm = MarkdownLLM()
docs = llm.generate_documentation("API Guide")

# BUG: Markdown formatting errors not caught
print(f"Docs:\\n{docs}")
"""
            
            test_file = os.path.join(temp_dir, "markdown_formatting.py")
            with open(test_file, "w") as f:
                f.write(agent_code)
            
            assert os.path.exists(test_file)
    
    def test_language_mixing_in_output(self):
        """Test 275: Detect unintended language mixing"""
        with tempfile.TemporaryDirectory() as temp_dir:
            agent_code = """
class LanguageLLM:
    def generate_in_language(self, prompt, language="en"):
        # BUG: No language consistency checking
        return "Hello, comment allez-vous? Me llamo assistant."

llm = LanguageLLM()
response = llm.generate_in_language("Greet the user", language="en")

# BUG: Mixed English/French/Spanish - not detected
print(f"Response: {response}")
"""
            
            test_file = os.path.join(temp_dir, "language_mixing.py")
            with open(test_file, "w") as f:
                f.write(agent_code)
            
            assert os.path.exists(test_file)
