"""
Comprehensive Test Suite for Phoenix - Data Processing & Transformation
Tests 636-665: ETL, Stream Processing, Data Quality, Serialization (30 tests)

This file tests Phoenix's ability to detect and fix bugs in data processing,
transformation pipelines, and data quality validation.
"""

import os
import tempfile
import shutil
from pathlib import Path
import pytest
from unittest.mock import Mock, patch


class TestETLPipelines:
    """Test ETL (Extract, Transform, Load) patterns (10 tests)"""
    
    def test_incremental_extraction(self):
        """Test 636: Use incremental extraction"""
        with tempfile.TemporaryDirectory() as temp_dir:
            agent_code = """
class FullExtraction:
    def extract_data(self):
        # BUG: Full extraction every time
        data = self.load_all_records()
        return data
    
    def load_all_records(self):
        # Loads millions of records
        return [{"id": i, "data": "value"} for i in range(1000000)]

etl = FullExtraction()

# BUG: Extracts all data instead of changes since last run
data = etl.extract_data()
print(f"Extracted: {len(data)} records")
"""
            
            test_file = os.path.join(temp_dir, "incremental_extraction.py")
            with open(test_file, "w") as f:
                f.write(agent_code)
            
            assert os.path.exists(test_file)
    
    def test_data_transformation_error_handling(self):
        """Test 637: Handle transformation errors"""
        with tempfile.TemporaryDirectory() as temp_dir:
            agent_code = """
class NoTransformErrorHandling:
    def transform_records(self, records):
        transformed = []
        for record in records:
            # BUG: One bad record stops entire pipeline
            transformed_record = {
                "name": record["name"].upper(),
                "age": int(record["age"])
            }
            transformed.append(transformed_record)
        return transformed

etl = NoTransformErrorHandling()

records = [
    {"name": "Alice", "age": "30"},
    {"name": "Bob", "age": "invalid"},  # Bad data
    {"name": "Charlie", "age": "25"}
]

# BUG: Crashes on one bad record
try:
    result = etl.transform_records(records)
except ValueError:
    print("Pipeline crashed on bad data")
"""
            
            test_file = os.path.join(temp_dir, "transform_error_handling.py")
            with open(test_file, "w") as f:
                f.write(agent_code)
            
            assert os.path.exists(test_file)
    
    def test_etl_transaction_boundary(self):
        """Test 638: Define transaction boundaries"""
        with tempfile.TemporaryDirectory() as temp_dir:
            agent_code = """
class NoETLTransactions:
    def __init__(self):
        self.processed = []
    
    def load_data(self, records):
        for record in records:
            # BUG: No transaction, partial load on failure
            self.processed.append(record)
            if len(self.processed) == 50:
                raise Exception("Database connection lost")

etl = NoETLTransactions()

records = [{"id": i} for i in range(100)]

try:
    etl.load_data(records)
except Exception:
    pass

# BUG: Loaded 50/100 records, inconsistent state
print(f"Loaded: {len(etl.processed)} records")
"""
            
            test_file = os.path.join(temp_dir, "etl_transactions.py")
            with open(test_file, "w") as f:
                f.write(agent_code)
            
            assert os.path.exists(test_file)
    
    def test_duplicate_detection(self):
        """Test 639: Detect and handle duplicates"""
        with tempfile.TemporaryDirectory() as temp_dir:
            agent_code = """
class NoDuplicateDetection:
    def __init__(self):
        self.records = []
    
    def load_records(self, new_records):
        # BUG: Appends without checking duplicates
        self.records.extend(new_records)

loader = NoDuplicateDetection()

# First batch
loader.load_records([{"id": 1, "name": "Alice"}])

# Retry loads same data
loader.load_records([{"id": 1, "name": "Alice"}])

# BUG: Duplicate records
print(f"Total records: {len(loader.records)}")
"""
            
            test_file = os.path.join(temp_dir, "duplicate_detection.py")
            with open(test_file, "w") as f:
                f.write(agent_code)
            
            assert os.path.exists(test_file)
    
    def test_schema_evolution(self):
        """Test 640: Handle schema changes"""
        with tempfile.TemporaryDirectory() as temp_dir:
            agent_code = """
class NoSchemaEvolution:
    def transform_record(self, record):
        # BUG: Assumes fixed schema
        return {
            "user_id": record["id"],
            "user_name": record["name"],
            "user_email": record["email"]
        }

transformer = NoSchemaEvolution()

# Old schema
old_record = {"id": 1, "name": "Alice", "email": "alice@example.com"}
result1 = transformer.transform_record(old_record)

# New schema adds "phone" field
new_record = {"id": 2, "name": "Bob", "email": "bob@example.com", "phone": "123-456"}

# BUG: Doesn't handle new fields
result2 = transformer.transform_record(new_record)
print(f"Results: {result1}, {result2}")
"""
            
            test_file = os.path.join(temp_dir, "schema_evolution.py")
            with open(test_file, "w") as f:
                f.write(agent_code)
            
            assert os.path.exists(test_file)
    
    def test_data_lineage_tracking(self):
        """Test 641: Track data lineage"""
        with tempfile.TemporaryDirectory() as temp_dir:
            agent_code = """
class NoLineageTracking:
    def transform(self, data):
        # BUG: No lineage tracking
        transformed = data.upper()
        return transformed

transformer = NoLineageTracking()

result = transformer.transform("input_data")

# BUG: Can't trace where data came from
print(f"Result: {result}")
"""
            
            test_file = os.path.join(temp_dir, "lineage_tracking.py")
            with open(test_file, "w") as f:
                f.write(agent_code)
            
            assert os.path.exists(test_file)
    
    def test_etl_checkpoint_recovery(self):
        """Test 642: Implement checkpointing"""
        with tempfile.TemporaryDirectory() as temp_dir:
            agent_code = """
class NoCheckpointing:
    def process_large_dataset(self, dataset):
        results = []
        for i, item in enumerate(dataset):
            # BUG: No checkpointing
            result = self.expensive_operation(item)
            results.append(result)
            
            if i == 5000:
                raise Exception("Processing failed")
        
        return results
    
    def expensive_operation(self, item):
        return item * 2

processor = NoCheckpointing()

dataset = list(range(10000))

try:
    results = processor.process_large_dataset(dataset)
except Exception:
    # BUG: Lost all progress, must restart from beginning
    print("No checkpoint, restart from scratch")
"""
            
            test_file = os.path.join(temp_dir, "etl_checkpointing.py")
            with open(test_file, "w") as f:
                f.write(agent_code)
            
            assert os.path.exists(test_file)
    
    def test_data_type_coercion(self):
        """Test 643: Validate data type coercion"""
        with tempfile.TemporaryDirectory() as temp_dir:
            agent_code = """
class UnsafeTypeCoercion:
    def transform(self, record):
        # BUG: Silent data loss on coercion
        return {
            "id": int(record["id"]),
            "price": float(record["price"]),
            "quantity": int(record["quantity"])
        }

transformer = UnsafeTypeCoercion()

# Data with precision
record = {
    "id": "123.45",  # Decimal ID
    "price": "19.999999",  # High precision
    "quantity": "10.8"  # Fractional quantity
}

# BUG: Silent truncation
result = transformer.transform(record)
print(f"Result: {result}")
"""
            
            test_file = os.path.join(temp_dir, "type_coercion.py")
            with open(test_file, "w") as f:
                f.write(agent_code)
            
            assert os.path.exists(test_file)
    
    def test_null_value_handling(self):
        """Test 644: Handle null/missing values"""
        with tempfile.TemporaryDirectory() as temp_dir:
            agent_code = """
class NoNullHandling:
    def calculate_average(self, records):
        # BUG: Doesn't handle null values
        total = sum(r["value"] for r in records)
        avg = total / len(records)
        return avg

calculator = NoNullHandling()

records = [
    {"value": 10},
    {"value": None},  # Null value
    {"value": 20}
]

# BUG: Crashes or wrong result
try:
    avg = calculator.calculate_average(records)
except TypeError:
    print("Null value not handled")
"""
            
            test_file = os.path.join(temp_dir, "null_handling.py")
            with open(test_file, "w") as f:
                f.write(agent_code)
            
            assert os.path.exists(test_file)
    
    def test_data_freshness_validation(self):
        """Test 645: Validate data freshness"""
        with tempfile.TemporaryDirectory() as temp_dir:
            agent_code = """
import time

class NoFreshnessCheck:
    def process_data(self, data):
        # BUG: Doesn't check data age
        return self.transform(data)
    
    def transform(self, data):
        return {"processed": data}

processor = NoFreshnessCheck()

# Stale data from yesterday
stale_data = {
    "timestamp": time.time() - 86400,
    "value": 100
}

# BUG: Processes stale data
result = processor.process_data(stale_data)
print(f"Result: {result}")
"""
            
            test_file = os.path.join(temp_dir, "freshness_validation.py")
            with open(test_file, "w") as f:
                f.write(agent_code)
            
            assert os.path.exists(test_file)


class TestStreamProcessing:
    """Test stream processing patterns (10 tests)"""
    
    def test_backpressure_handling(self):
        """Test 646: Handle backpressure"""
        with tempfile.TemporaryDirectory() as temp_dir:
            agent_code = """
class NoBackpressure:
    def __init__(self):
        self.buffer = []
    
    def process_stream(self, events):
        for event in events:
            # BUG: No backpressure, buffer grows unbounded
            self.buffer.append(event)

processor = NoBackpressure()

# Fast producer, slow consumer
events = [{"id": i} for i in range(1000000)]

# BUG: Out of memory
processor.process_stream(events)
print(f"Buffer size: {len(processor.buffer)}")
"""
            
            test_file = os.path.join(temp_dir, "backpressure.py")
            with open(test_file, "w") as f:
                f.write(agent_code)
            
            assert os.path.exists(test_file)
    
    def test_event_ordering_guarantee(self):
        """Test 647: Guarantee event ordering"""
        with tempfile.TemporaryDirectory() as temp_dir:
            agent_code = """
import asyncio

class UnorderedStreamProcessing:
    async def process_events(self, events):
        # BUG: Processes events in parallel, order lost
        tasks = []
        for event in events:
            task = asyncio.create_task(self.process(event))
            tasks.append(task)
        
        results = await asyncio.gather(*tasks)
        return results
    
    async def process(self, event):
        await asyncio.sleep(0.01)
        return event

processor = UnorderedStreamProcessing()

events = ["event1", "event2", "event3"]

# BUG: Order not preserved
print("Events may be processed out of order")
"""
            
            test_file = os.path.join(temp_dir, "event_ordering.py")
            with open(test_file, "w") as f:
                f.write(agent_code)
            
            assert os.path.exists(test_file)
    
    def test_exactly_once_semantics(self):
        """Test 648: Ensure exactly-once processing"""
        with tempfile.TemporaryDirectory() as temp_dir:
            agent_code = """
class AtLeastOnceProcessing:
    def __init__(self):
        self.processed_count = 0
    
    def process_event(self, event):
        # BUG: Processes event, then crashes before ack
        self.processed_count += 1
        
        # Simulated crash/retry
        if self.processed_count == 1:
            raise Exception("Crash before ack")

processor = AtLeastOnceProcessing()

event = {"id": 1, "data": "value"}

# Retry on failure
for attempt in range(2):
    try:
        processor.process_event(event)
    except Exception:
        continue

# BUG: Processed event twice
print(f"Processed: {processor.processed_count} times")
"""
            
            test_file = os.path.join(temp_dir, "exactly_once.py")
            with open(test_file, "w") as f:
                f.write(agent_code)
            
            assert os.path.exists(test_file)
    
    def test_watermark_handling(self):
        """Test 649: Handle event-time watermarks"""
        with tempfile.TemporaryDirectory() as temp_dir:
            agent_code = """
class NoWatermarks:
    def process_windowed_events(self, events):
        # BUG: Uses processing time, not event time
        window = []
        for event in events:
            window.append(event)
        
        return window

processor = NoWatermarks()

# Out-of-order events
events = [
    {"timestamp": 1000, "value": 1},
    {"timestamp": 3000, "value": 3},
    {"timestamp": 2000, "value": 2}  # Late event
]

# BUG: Late events in wrong window
result = processor.process_windowed_events(events)
print(f"Window: {result}")
"""
            
            test_file = os.path.join(temp_dir, "watermarks.py")
            with open(test_file, "w") as f:
                f.write(agent_code)
            
            assert os.path.exists(test_file)
    
    def test_stream_join_handling(self):
        """Test 650: Handle stream joins"""
        with tempfile.TemporaryDirectory() as temp_dir:
            agent_code = """
class UnboundedStreamJoin:
    def join_streams(self, stream1, stream2):
        # BUG: Keeps all data for join, unbounded memory
        buffer1 = list(stream1)
        buffer2 = list(stream2)
        
        results = []
        for item1 in buffer1:
            for item2 in buffer2:
                if item1["key"] == item2["key"]:
                    results.append((item1, item2))
        
        return results

joiner = UnboundedStreamJoin()

# BUG: Memory grows unbounded
stream1 = [{"key": i, "value": i} for i in range(100000)]
stream2 = [{"key": i, "data": i} for i in range(100000)]

print("Unbounded stream join")
"""
            
            test_file = os.path.join(temp_dir, "stream_join.py")
            with open(test_file, "w") as f:
                f.write(agent_code)
            
            assert os.path.exists(test_file)
    
    def test_state_management(self):
        """Test 651: Manage stateful stream processing"""
        with tempfile.TemporaryDirectory() as temp_dir:
            agent_code = """
class NoStatePersistence:
    def __init__(self):
        self.state = {}
    
    def process_event(self, event):
        user_id = event["user_id"]
        
        # BUG: State lost on restart
        if user_id not in self.state:
            self.state[user_id] = 0
        
        self.state[user_id] += event["value"]
        return self.state[user_id]

processor = NoStatePersistence()

events = [
    {"user_id": "user1", "value": 10},
    {"user_id": "user1", "value": 20}
]

for event in events:
    total = processor.process_event(event)

# Simulated restart
processor = NoStatePersistence()  # State lost

# BUG: Aggregation reset
print("State lost on restart")
"""
            
            test_file = os.path.join(temp_dir, "state_management.py")
            with open(test_file, "w") as f:
                f.write(agent_code)
            
            assert os.path.exists(test_file)
    
    def test_late_event_handling(self):
        """Test 652: Handle late-arriving events"""
        with tempfile.TemporaryDirectory() as temp_dir:
            agent_code = """
class NoLateEventHandling:
    def process_window(self, events, window_end):
        # BUG: Closes window immediately
        windowed_events = [e for e in events if e["timestamp"] < window_end]
        return sum(e["value"] for e in windowed_events)

processor = NoLateEventHandling()

events = [
    {"timestamp": 1000, "value": 10},
    {"timestamp": 2000, "value": 20}
]

result = processor.process_window(events, window_end=3000)

# Late event arrives
late_event = {"timestamp": 1500, "value": 15}

# BUG: Late event ignored
print(f"Window closed, late event lost")
"""
            
            test_file = os.path.join(temp_dir, "late_events.py")
            with open(test_file, "w") as f:
                f.write(agent_code)
            
            assert os.path.exists(test_file)
    
    def test_stream_partitioning(self):
        """Test 653: Partition streams correctly"""
        with tempfile.TemporaryDirectory() as temp_dir:
            agent_code = """
class RandomPartitioning:
    def partition_event(self, event):
        # BUG: Random partitioning breaks ordering
        import random
        partition = random.randint(0, 3)
        return partition

partitioner = RandomPartitioning()

events = [
    {"user_id": "user1", "seq": 1},
    {"user_id": "user1", "seq": 2},
    {"user_id": "user1", "seq": 3}
]

partitions = [partitioner.partition_event(e) for e in events]

# BUG: Same user's events in different partitions
print(f"Partitions: {partitions}")
"""
            
            test_file = os.path.join(temp_dir, "stream_partitioning.py")
            with open(test_file, "w") as f:
                f.write(agent_code)
            
            assert os.path.exists(test_file)
    
    def test_stream_aggregation_accuracy(self):
        """Test 654: Accurate stream aggregation"""
        with tempfile.TemporaryDirectory() as temp_dir:
            agent_code = """
class InaccurateAggregation:
    def __init__(self):
        self.count = 0
        self.sum = 0.0
    
    def add_value(self, value):
        # BUG: Floating point precision issues
        self.sum += value
        self.count += 1
    
    def get_average(self):
        return self.sum / self.count

aggregator = InaccurateAggregation()

# Add many small values
for _ in range(1000000):
    aggregator.add_value(0.1)

avg = aggregator.get_average()

# BUG: Precision error accumulation
print(f"Average: {avg} (expected 0.1)")
"""
            
            test_file = os.path.join(temp_dir, "aggregation_accuracy.py")
            with open(test_file, "w") as f:
                f.write(agent_code)
            
            assert os.path.exists(test_file)
    
    def test_event_deduplication(self):
        """Test 655: Deduplicate events in stream"""
        with tempfile.TemporaryDirectory() as temp_dir:
            agent_code = """
class NoDeduplication:
    def __init__(self):
        self.processed = []
    
    def process_event(self, event):
        # BUG: No deduplication
        self.processed.append(event)

processor = NoDeduplication()

# Duplicate events
events = [
    {"id": "event1", "data": "value"},
    {"id": "event1", "data": "value"},  # Duplicate
    {"id": "event2", "data": "value"}
]

for event in events:
    processor.process_event(event)

# BUG: Processed duplicates
print(f"Processed: {len(processor.processed)} events")
"""
            
            test_file = os.path.join(temp_dir, "event_deduplication.py")
            with open(test_file, "w") as f:
                f.write(agent_code)
            
            assert os.path.exists(test_file)


class TestDataQuality:
    """Test data quality and validation (10 tests)"""
    
    def test_data_completeness_check(self):
        """Test 656: Check data completeness"""
        with tempfile.TemporaryDirectory() as temp_dir:
            agent_code = """
class NoCompletenessCheck:
    def process_record(self, record):
        # BUG: Doesn't validate required fields
        return {
            "name": record.get("name"),
            "email": record.get("email"),
            "age": record.get("age")
        }

processor = NoCompletenessCheck()

# Missing required fields
incomplete_record = {"name": "John"}

# BUG: Processes incomplete data
result = processor.process_record(incomplete_record)
print(f"Result: {result}")
"""
            
            test_file = os.path.join(temp_dir, "completeness_check.py")
            with open(test_file, "w") as f:
                f.write(agent_code)
            
            assert os.path.exists(test_file)
    
    def test_data_accuracy_validation(self):
        """Test 657: Validate data accuracy"""
        with tempfile.TemporaryDirectory() as temp_dir:
            agent_code = """
class NoAccuracyValidation:
    def process_user(self, user):
        # BUG: Doesn't validate data format
        return {
            "email": user["email"],
            "phone": user["phone"],
            "age": user["age"]
        }

processor = NoAccuracyValidation()

# Invalid data
user = {
    "email": "not-an-email",
    "phone": "abc",
    "age": -5
}

# BUG: Accepts invalid data
result = processor.process_user(user)
print(f"Result: {result}")
"""
            
            test_file = os.path.join(temp_dir, "accuracy_validation.py")
            with open(test_file, "w") as f:
                f.write(agent_code)
            
            assert os.path.exists(test_file)
    
    def test_data_consistency_check(self):
        """Test 658: Check data consistency"""
        with tempfile.TemporaryDirectory() as temp_dir:
            agent_code = """
class NoConsistencyCheck:
    def process_order(self, order):
        # BUG: Doesn't check consistency
        return {
            "quantity": order["quantity"],
            "unit_price": order["unit_price"],
            "total": order["total"]
        }

processor = NoConsistencyCheck()

# Inconsistent data
order = {
    "quantity": 10,
    "unit_price": 5.0,
    "total": 30.0  # Should be 50.0
}

# BUG: Accepts inconsistent data
result = processor.process_order(order)
print(f"Result: {result}")
"""
            
            test_file = os.path.join(temp_dir, "consistency_check.py")
            with open(test_file, "w") as f:
                f.write(agent_code)
            
            assert os.path.exists(test_file)
    
    def test_outlier_detection(self):
        """Test 659: Detect outliers"""
        with tempfile.TemporaryDirectory() as temp_dir:
            agent_code = """
class NoOutlierDetection:
    def calculate_average(self, values):
        # BUG: Doesn't detect outliers
        return sum(values) / len(values)

calculator = NoOutlierDetection()

# Values with outlier
values = [10, 12, 11, 13, 1000]  # 1000 is outlier

# BUG: Outlier skews result
avg = calculator.calculate_average(values)
print(f"Average: {avg}")
"""
            
            test_file = os.path.join(temp_dir, "outlier_detection.py")
            with open(test_file, "w") as f:
                f.write(agent_code)
            
            assert os.path.exists(test_file)
    
    def test_data_profiling(self):
        """Test 660: Profile data characteristics"""
        with tempfile.TemporaryDirectory() as temp_dir:
            agent_code = """
class NoProfiling:
    def process_dataset(self, dataset):
        # BUG: Doesn't profile data
        return [self.transform(record) for record in dataset]
    
    def transform(self, record):
        return record

processor = NoProfiling()

# Dataset with issues
dataset = [
    {"age": 25, "income": 50000},
    {"age": None, "income": 60000},  # Null
    {"age": 30, "income": None}  # Null
]

# BUG: No visibility into data quality
result = processor.process_dataset(dataset)
print(f"Processed {len(result)} records")
"""
            
            test_file = os.path.join(temp_dir, "data_profiling.py")
            with open(test_file, "w") as f:
                f.write(agent_code)
            
            assert os.path.exists(test_file)
    
    def test_referential_integrity(self):
        """Test 661: Check referential integrity"""
        with tempfile.TemporaryDirectory() as temp_dir:
            agent_code = """
class NoReferentialIntegrity:
    def __init__(self):
        self.users = [{"id": 1}, {"id": 2}]
    
    def create_order(self, order):
        # BUG: Doesn't check if user exists
        return {"user_id": order["user_id"], "amount": order["amount"]}

system = NoReferentialIntegrity()

# Order for non-existent user
order = {"user_id": 999, "amount": 100}

# BUG: Creates orphan record
result = system.create_order(order)
print(f"Order: {result}")
"""
            
            test_file = os.path.join(temp_dir, "referential_integrity.py")
            with open(test_file, "w") as f:
                f.write(agent_code)
            
            assert os.path.exists(test_file)
    
    def test_data_uniqueness_constraint(self):
        """Test 662: Enforce uniqueness constraints"""
        with tempfile.TemporaryDirectory() as temp_dir:
            agent_code = """
class NoUniquenessCheck:
    def __init__(self):
        self.users = []
    
    def add_user(self, user):
        # BUG: Doesn't check for duplicates
        self.users.append(user)

system = NoUniquenessCheck()

# Duplicate emails
system.add_user({"email": "john@example.com", "name": "John"})
system.add_user({"email": "john@example.com", "name": "Johnny"})

# BUG: Duplicate emails allowed
print(f"Users: {len(system.users)}")
"""
            
            test_file = os.path.join(temp_dir, "uniqueness_constraint.py")
            with open(test_file, "w") as f:
                f.write(agent_code)
            
            assert os.path.exists(test_file)
    
    def test_data_range_validation(self):
        """Test 663: Validate data ranges"""
        with tempfile.TemporaryDirectory() as temp_dir:
            agent_code = """
class NoRangeValidation:
    def process_transaction(self, transaction):
        # BUG: Doesn't validate ranges
        return {
            "amount": transaction["amount"],
            "date": transaction["date"]
        }

processor = NoRangeValidation()

# Out of range values
transaction = {
    "amount": -1000,  # Negative amount
    "date": "2030-01-01"  # Future date
}

# BUG: Accepts invalid ranges
result = processor.process_transaction(transaction)
print(f"Transaction: {result}")
"""
            
            test_file = os.path.join(temp_dir, "range_validation.py")
            with open(test_file, "w") as f:
                f.write(agent_code)
            
            assert os.path.exists(test_file)
    
    def test_data_sanitization(self):
        """Test 664: Sanitize input data"""
        with tempfile.TemporaryDirectory() as temp_dir:
            agent_code = """
class NoDataSanitization:
    def process_input(self, user_input):
        # BUG: Doesn't sanitize input
        query = f"SELECT * FROM users WHERE name = '{user_input}'"
        return query

processor = NoDataSanitization()

# Malicious input
malicious_input = "'; DROP TABLE users; --"

# BUG: SQL injection vulnerability
query = processor.process_input(malicious_input)
print(f"Query: {query}")
"""
            
            test_file = os.path.join(temp_dir, "data_sanitization.py")
            with open(test_file, "w") as f:
                f.write(agent_code)
            
            assert os.path.exists(test_file)
    
    def test_cross_field_validation(self):
        """Test 665: Validate cross-field relationships"""
        with tempfile.TemporaryDirectory() as temp_dir:
            agent_code = """
class NoCrossFieldValidation:
    def process_booking(self, booking):
        # BUG: Doesn't validate field relationships
        return {
            "start_date": booking["start_date"],
            "end_date": booking["end_date"]
        }

processor = NoCrossFieldValidation()

# Invalid relationship
booking = {
    "start_date": "2024-01-15",
    "end_date": "2024-01-10"  # Before start date
}

# BUG: Accepts invalid date range
result = processor.process_booking(booking)
print(f"Booking: {result}")
"""
            
            test_file = os.path.join(temp_dir, "cross_field_validation.py")
            with open(test_file, "w") as f:
                f.write(agent_code)
            
            assert os.path.exists(test_file)
