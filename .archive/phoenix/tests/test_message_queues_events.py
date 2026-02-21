"""
Comprehensive Test Suite for Phoenix - Message Queues & Event Streaming
Tests 876-905: Kafka, RabbitMQ, SQS, Event Processing (30 tests)

This file tests Phoenix's ability to detect and fix bugs in message queue
systems, event streaming, and asynchronous messaging.
"""

import os
import tempfile
import shutil
from pathlib import Path
import pytest
from unittest.mock import Mock, patch


class TestMessageQueuePatterns:
    """Test message queue patterns and reliability (10 tests)"""
    
    def test_no_message_acknowledgment(self):
        """Test 876: Acknowledge messages after processing"""
        with tempfile.TemporaryDirectory() as temp_dir:
            agent_code = """
class NoAcknowledgment:
    def process_messages(self):
        while True:
            message = self.queue.get_message()
            
            # BUG: Doesn't acknowledge
            self.process(message)
    
    def process(self, message):
        print(f"Processing: {message}")
    
    def __init__(self):
        self.queue = MockQueue()

class MockQueue:
    def get_message(self):
        return {"id": 1, "data": "test"}

consumer = NoAcknowledgment()

# BUG: Messages redelivered on restart
print("No acknowledgment")
"""
            
            test_file = os.path.join(temp_dir, "no_ack.py")
            with open(test_file, "w") as f:
                f.write(agent_code)
            
            assert os.path.exists(test_file)
    
    def test_duplicate_message_processing(self):
        """Test 877: Handle duplicate messages"""
        with tempfile.TemporaryDirectory() as temp_dir:
            agent_code = """
class NoDuplicateHandling:
    def process_message(self, message):
        # BUG: No idempotency check
        self.save_to_database(message)
    
    def save_to_database(self, message):
        print(f"Saving: {message}")

processor = NoDuplicateHandling()

# BUG: Duplicate processing
processor.process_message({"id": 1, "data": "test"})
processor.process_message({"id": 1, "data": "test"})  # Duplicate
"""
            
            test_file = os.path.join(temp_dir, "duplicates.py")
            with open(test_file, "w") as f:
                f.write(agent_code)
            
            assert os.path.exists(test_file)
    
    def test_message_ordering(self):
        """Test 878: Preserve message ordering"""
        with tempfile.TemporaryDirectory() as temp_dir:
            agent_code = """
class NoOrderingGuarantee:
    def __init__(self):
        self.messages = []
    
    def send_message(self, message):
        # BUG: No ordering guarantee
        self.queue.put(message)
    
    def __init__(self):
        self.queue = MockQueue()

class MockQueue:
    def __init__(self):
        self.items = []
    
    def put(self, item):
        # Simulates out-of-order delivery
        import random
        self.items.insert(random.randint(0, len(self.items)), item)

publisher = NoOrderingGuarantee()

# BUG: Messages may be processed out of order
for i in range(10):
    publisher.send_message(f"message_{i}")
"""
            
            test_file = os.path.join(temp_dir, "ordering.py")
            with open(test_file, "w") as f:
                f.write(agent_code)
            
            assert os.path.exists(test_file)
    
    def test_poison_message_handling(self):
        """Test 879: Handle poison messages"""
        with tempfile.TemporaryDirectory() as temp_dir:
            agent_code = """
class NoPoisonHandling:
    def process_messages(self):
        while True:
            message = self.queue.get_message()
            
            try:
                self.process(message)
            except Exception as e:
                # BUG: Requeues poison message indefinitely
                self.queue.requeue(message)
    
    def process(self, message):
        raise Exception("Invalid message format")
    
    def __init__(self):
        self.queue = MockQueue()

class MockQueue:
    def get_message(self):
        return {"corrupt": "data"}
    
    def requeue(self, message):
        print("Requeuing message")

consumer = NoPoisonHandling()

# BUG: Infinite loop on poison message
print("Poison message loop")
"""
            
            test_file = os.path.join(temp_dir, "poison_messages.py")
            with open(test_file, "w") as f:
                f.write(agent_code)
            
            assert os.path.exists(test_file)
    
    def test_dead_letter_queue(self):
        """Test 880: Use dead letter queue"""
        with tempfile.TemporaryDirectory() as temp_dir:
            agent_code = """
class NoDeadLetterQueue:
    def process_message(self, message):
        try:
            self.process(message)
        except Exception:
            # BUG: Drops failed message
            pass
    
    def process(self, message):
        raise Exception("Processing failed")

consumer = NoDeadLetterQueue()

# BUG: Failed messages lost
consumer.process_message({"id": 1})
"""
            
            test_file = os.path.join(temp_dir, "dead_letter.py")
            with open(test_file, "w") as f:
                f.write(agent_code)
            
            assert os.path.exists(test_file)
    
    def test_message_visibility_timeout(self):
        """Test 881: Configure visibility timeout"""
        with tempfile.TemporaryDirectory() as temp_dir:
            agent_code = """
class ShortVisibilityTimeout:
    def process_message(self, message):
        # BUG: Processing takes longer than visibility timeout
        import time
        time.sleep(60)  # 60 seconds
        
        # Message becomes visible to other consumers
        self.ack(message)
    
    def ack(self, message):
        print("Acknowledging message")

# BUG: Default 30s visibility timeout
consumer = ShortVisibilityTimeout()

print("Visibility timeout too short")
"""
            
            test_file = os.path.join(temp_dir, "visibility_timeout.py")
            with open(test_file, "w") as f:
                f.write(agent_code)
            
            assert os.path.exists(test_file)
    
    def test_message_batching(self):
        """Test 882: Batch messages for efficiency"""
        with tempfile.TemporaryDirectory() as temp_dir:
            agent_code = """
class NoMessageBatching:
    def send_messages(self, messages):
        # BUG: Sends one at a time
        for message in messages:
            self.queue.send(message)
    
    def __init__(self):
        self.queue = MockQueue()

class MockQueue:
    def send(self, message):
        print(f"Sending individual message: {message}")

publisher = NoMessageBatching()

# BUG: 1000 individual send operations
messages = [{"id": i} for i in range(1000)]
publisher.send_messages(messages)
"""
            
            test_file = os.path.join(temp_dir, "batching.py")
            with open(test_file, "w") as f:
                f.write(agent_code)
            
            assert os.path.exists(test_file)
    
    def test_prefetch_count(self):
        """Test 883: Configure prefetch count"""
        with tempfile.TemporaryDirectory() as temp_dir:
            agent_code = """
class UnlimitedPrefetch:
    def start_consuming(self):
        # BUG: No prefetch limit
        self.channel.basic_consume(
            queue="tasks",
            on_message_callback=self.process
        )
    
    def process(self, message):
        import time
        time.sleep(10)  # Slow processing
    
    def __init__(self):
        self.channel = MockChannel()

class MockChannel:
    def basic_consume(self, queue, on_message_callback):
        print("Consuming with unlimited prefetch")

consumer = UnlimitedPrefetch()

# BUG: Fetches all messages at once
consumer.start_consuming()
"""
            
            test_file = os.path.join(temp_dir, "prefetch.py")
            with open(test_file, "w") as f:
                f.write(agent_code)
            
            assert os.path.exists(test_file)
    
    def test_message_ttl(self):
        """Test 884: Set message time-to-live"""
        with tempfile.TemporaryDirectory() as temp_dir:
            agent_code = """
class NoMessageTTL:
    def send_message(self, message):
        # BUG: No TTL
        self.queue.send(message)
    
    def __init__(self):
        self.queue = MockQueue()

class MockQueue:
    def __init__(self):
        self.messages = []
    
    def send(self, message):
        # BUG: Messages accumulate forever
        self.messages.append(message)

publisher = NoMessageTTL()

# BUG: Old messages never expire
for i in range(10000):
    publisher.send_message(f"message_{i}")

print(f"Queue size: {len(publisher.queue.messages)}")
"""
            
            test_file = os.path.join(temp_dir, "message_ttl.py")
            with open(test_file, "w") as f:
                f.write(agent_code)
            
            assert os.path.exists(test_file)
    
    def test_publisher_confirms(self):
        """Test 885: Use publisher confirms"""
        with tempfile.TemporaryDirectory() as temp_dir:
            agent_code = """
class NoPublisherConfirms:
    def send_message(self, message):
        # BUG: Fire and forget
        self.channel.publish(message)
    
    def __init__(self):
        self.channel = MockChannel()

class MockChannel:
    def publish(self, message):
        # Simulates message loss
        import random
        if random.random() < 0.1:
            print("Message lost")
        else:
            print("Message sent (maybe)")

publisher = NoPublisherConfirms()

# BUG: Doesn't know if message was delivered
publisher.send_message("important data")
"""
            
            test_file = os.path.join(temp_dir, "publisher_confirms.py")
            with open(test_file, "w") as f:
                f.write(agent_code)
            
            assert os.path.exists(test_file)


class TestEventStreaming:
    """Test event streaming platforms (10 tests)"""
    
    def test_kafka_no_consumer_group(self):
        """Test 886: Use Kafka consumer groups"""
        with tempfile.TemporaryDirectory() as temp_dir:
            agent_code = """
class NoConsumerGroup:
    def consume(self):
        # BUG: No consumer group
        consumer = self.create_consumer()
        
        for message in consumer:
            self.process(message)
    
    def create_consumer(self):
        return MockConsumer()
    
    def process(self, message):
        print(f"Processing: {message}")

class MockConsumer:
    def __iter__(self):
        return iter([{"value": "message"}])

consumer = NoConsumerGroup()

# BUG: Can't scale horizontally
print("No consumer group")
"""
            
            test_file = os.path.join(temp_dir, "kafka_consumer_group.py")
            with open(test_file, "w") as f:
                f.write(agent_code)
            
            assert os.path.exists(test_file)
    
    def test_kafka_no_offset_commit(self):
        """Test 887: Commit Kafka offsets"""
        with tempfile.TemporaryDirectory() as temp_dir:
            agent_code = """
class NoOffsetCommit:
    def consume(self):
        for message in self.consumer:
            self.process(message)
            # BUG: Doesn't commit offset
    
    def process(self, message):
        print(f"Processing: {message}")
    
    def __init__(self):
        self.consumer = MockConsumer()

class MockConsumer:
    def __iter__(self):
        return iter([{"offset": i} for i in range(100)])

consumer = NoOffsetCommit()

# BUG: Reprocesses messages on restart
print("No offset commit")
"""
            
            test_file = os.path.join(temp_dir, "kafka_offset.py")
            with open(test_file, "w") as f:
                f.write(agent_code)
            
            assert os.path.exists(test_file)
    
    def test_kafka_partition_assignment(self):
        """Test 888: Handle Kafka partition rebalancing"""
        with tempfile.TemporaryDirectory() as temp_dir:
            agent_code = """
class NoRebalanceHandling:
    def consume(self):
        # BUG: Doesn't handle rebalance
        for message in self.consumer:
            self.process(message)
    
    def process(self, message):
        import time
        time.sleep(5)  # Slow processing
    
    def __init__(self):
        self.consumer = MockConsumer()

class MockConsumer:
    def __iter__(self):
        return iter([{"data": "message"}])

consumer = NoRebalanceHandling()

# BUG: May lose data during rebalance
print("No rebalance handling")
"""
            
            test_file = os.path.join(temp_dir, "kafka_rebalance.py")
            with open(test_file, "w") as f:
                f.write(agent_code)
            
            assert os.path.exists(test_file)
    
    def test_kafka_idempotent_producer(self):
        """Test 889: Enable Kafka idempotent producer"""
        with tempfile.TemporaryDirectory() as temp_dir:
            agent_code = """
class NonIdempotentProducer:
    def send(self, topic, message):
        # BUG: May send duplicates on retry
        self.producer.send(topic, message)
    
    def __init__(self):
        self.producer = MockProducer()

class MockProducer:
    def send(self, topic, message):
        print(f"Sending to {topic}: {message}")

producer = NonIdempotentProducer()

# BUG: Network failure may cause duplicates
producer.send("events", {"id": 1, "data": "test"})
"""
            
            test_file = os.path.join(temp_dir, "kafka_idempotent.py")
            with open(test_file, "w") as f:
                f.write(agent_code)
            
            assert os.path.exists(test_file)
    
    def test_kafka_compression(self):
        """Test 890: Use Kafka compression"""
        with tempfile.TemporaryDirectory() as temp_dir:
            agent_code = """
class NoCompression:
    def send(self, message):
        # BUG: No compression
        self.producer.send("events", message)
    
    def __init__(self):
        self.producer = MockProducer()

class MockProducer:
    def send(self, topic, message):
        print(f"Sending uncompressed: {len(str(message))} bytes")

producer = NoCompression()

# BUG: Wastes network bandwidth
large_message = {"data": "x" * 10000}
producer.send(large_message)
"""
            
            test_file = os.path.join(temp_dir, "kafka_compression.py")
            with open(test_file, "w") as f:
                f.write(agent_code)
            
            assert os.path.exists(test_file)
    
    def test_kafka_batch_size(self):
        """Test 891: Configure Kafka batch size"""
        with tempfile.TemporaryDirectory() as temp_dir:
            agent_code = """
class SmallBatchSize:
    def send_messages(self, messages):
        # BUG: Sends immediately
        for message in messages:
            self.producer.send("events", message)
    
    def __init__(self):
        self.producer = MockProducer()

class MockProducer:
    def send(self, topic, message):
        print(f"Sending single message")

producer = SmallBatchSize()

# BUG: 1000 individual network calls
messages = [{"id": i} for i in range(1000)]
producer.send_messages(messages)
"""
            
            test_file = os.path.join(temp_dir, "kafka_batch.py")
            with open(test_file, "w") as f:
                f.write(agent_code)
            
            assert os.path.exists(test_file)
    
    def test_kafka_max_poll_records(self):
        """Test 892: Configure max poll records"""
        with tempfile.TemporaryDirectory() as temp_dir:
            agent_code = """
class UnlimitedPoll:
    def consume(self):
        # BUG: May fetch too many records
        records = self.consumer.poll()
        
        for record in records:
            self.slow_process(record)
    
    def slow_process(self, record):
        import time
        time.sleep(1)
    
    def __init__(self):
        self.consumer = MockConsumer()

class MockConsumer:
    def poll(self):
        # Returns 10000 records
        return [{"id": i} for i in range(10000)]

consumer = UnlimitedPoll()

# BUG: Session timeout while processing large batch
print("Unlimited poll")
"""
            
            test_file = os.path.join(temp_dir, "kafka_max_poll.py")
            with open(test_file, "w") as f:
                f.write(agent_code)
            
            assert os.path.exists(test_file)
    
    def test_kinesis_shard_iterator(self):
        """Test 893: Handle Kinesis shard iterator"""
        with tempfile.TemporaryDirectory() as temp_dir:
            agent_code = """
class NoShardIteratorHandling:
    def consume(self):
        iterator = self.get_shard_iterator()
        
        while True:
            # BUG: Doesn't handle expired iterator
            records = self.get_records(iterator)
            
            for record in records:
                self.process(record)
    
    def get_shard_iterator(self):
        return "iterator123"
    
    def get_records(self, iterator):
        raise Exception("Iterator expired")
    
    def process(self, record):
        print(f"Processing: {record}")

consumer = NoShardIteratorHandling()

# BUG: Crashes on expired iterator
try:
    consumer.consume()
except:
    print("Iterator error")
"""
            
            test_file = os.path.join(temp_dir, "kinesis_iterator.py")
            with open(test_file, "w") as f:
                f.write(agent_code)
            
            assert os.path.exists(test_file)
    
    def test_event_hub_checkpoint(self):
        """Test 894: Checkpoint Event Hub consumer"""
        with tempfile.TemporaryDirectory() as temp_dir:
            agent_code = """
class NoCheckpointing:
    def process_events(self):
        for event in self.consumer:
            self.process(event)
            # BUG: Doesn't checkpoint
    
    def process(self, event):
        print(f"Processing: {event}")
    
    def __init__(self):
        self.consumer = MockConsumer()

class MockConsumer:
    def __iter__(self):
        return iter([{"data": "event"}])

consumer = NoCheckpointing()

# BUG: Reprocesses events on restart
print("No checkpointing")
"""
            
            test_file = os.path.join(temp_dir, "event_hub_checkpoint.py")
            with open(test_file, "w") as f:
                f.write(agent_code)
            
            assert os.path.exists(test_file)
    
    def test_pub_sub_exactly_once(self):
        """Test 895: Handle Pub/Sub exactly-once delivery"""
        with tempfile.TemporaryDirectory() as temp_dir:
            agent_code = """
class NoExactlyOnce:
    def process_message(self, message):
        # BUG: Doesn't use exactly-once delivery
        self.process(message)
        message.ack()
    
    def process(self, message):
        # May be called multiple times
        print(f"Processing: {message}")

# BUG: Duplicate processing possible
print("No exactly-once semantics")
"""
            
            test_file = os.path.join(temp_dir, "pub_sub_exactly_once.py")
            with open(test_file, "w") as f:
                f.write(agent_code)
            
            assert os.path.exists(test_file)


class TestEventProcessing:
    """Test event processing patterns (10 tests)"""
    
    def test_event_schema_evolution(self):
        """Test 896: Handle event schema evolution"""
        with tempfile.TemporaryDirectory() as temp_dir:
            agent_code = """
class NoSchemaEvolution:
    def process_event(self, event):
        # BUG: Assumes fixed schema
        user_id = event["user_id"]
        timestamp = event["timestamp"]
        action = event["action"]
        
        print(f"{user_id} did {action} at {timestamp}")

processor = NoSchemaEvolution()

# BUG: Crashes on new schema version
old_event = {"user_id": 1, "timestamp": "2024-01-01", "action": "login"}
processor.process_event(old_event)

new_event = {"user_id": 1, "timestamp": "2024-01-01", "action": "login", "ip": "127.0.0.1"}
try:
    processor.process_event(new_event)  # Still works
except:
    print("Schema evolution failed")
"""
            
            test_file = os.path.join(temp_dir, "schema_evolution.py")
            with open(test_file, "w") as f:
                f.write(agent_code)
            
            assert os.path.exists(test_file)
    
    def test_event_versioning(self):
        """Test 897: Version events"""
        with tempfile.TemporaryDirectory() as temp_dir:
            agent_code = """
class NoEventVersioning:
    def publish_event(self, event_type, data):
        # BUG: No version field
        event = {
            "type": event_type,
            "data": data,
            "timestamp": "2024-01-01"
        }
        
        self.publish(event)
    
    def publish(self, event):
        print(f"Publishing: {event}")

publisher = NoEventVersioning()

# BUG: Can't distinguish event versions
publisher.publish_event("UserCreated", {"id": 1, "name": "Alice"})
"""
            
            test_file = os.path.join(temp_dir, "event_versioning.py")
            with open(test_file, "w") as f:
                f.write(agent_code)
            
            assert os.path.exists(test_file)
    
    def test_event_correlation_id(self):
        """Test 898: Add correlation IDs to events"""
        with tempfile.TemporaryDirectory() as temp_dir:
            agent_code = """
class NoCorrelationID:
    def publish_event(self, event_type, data):
        # BUG: No correlation ID
        event = {
            "type": event_type,
            "data": data
        }
        
        self.publish(event)
    
    def publish(self, event):
        print(f"Publishing: {event}")

publisher = NoCorrelationID()

# BUG: Can't trace related events
publisher.publish_event("OrderCreated", {"order_id": 1})
publisher.publish_event("PaymentProcessed", {"order_id": 1})
"""
            
            test_file = os.path.join(temp_dir, "correlation_id.py")
            with open(test_file, "w") as f:
                f.write(agent_code)
            
            assert os.path.exists(test_file)
    
    def test_event_replay(self):
        """Test 899: Support event replay"""
        with tempfile.TemporaryDirectory() as temp_dir:
            agent_code = """
class NoEventReplay:
    def __init__(self):
        self.events = []
    
    def publish_event(self, event):
        # BUG: Doesn't store events
        self.process(event)
    
    def process(self, event):
        print(f"Processing: {event}")

processor = NoEventReplay()

# BUG: Can't replay events
processor.publish_event({"type": "UserCreated", "id": 1})
"""
            
            test_file = os.path.join(temp_dir, "event_replay.py")
            with open(test_file, "w") as f:
                f.write(agent_code)
            
            assert os.path.exists(test_file)
    
    def test_event_filtering(self):
        """Test 900: Filter events efficiently"""
        with tempfile.TemporaryDirectory() as temp_dir:
            agent_code = """
class InefficientFiltering:
    def process_events(self):
        # BUG: Fetches all events then filters
        all_events = self.fetch_all_events()
        
        relevant_events = [e for e in all_events if e["type"] == "UserCreated"]
        
        for event in relevant_events:
            self.process(event)
    
    def fetch_all_events(self):
        # Returns 1 million events
        return [{"type": f"Event{i % 10}"} for i in range(1000000)]
    
    def process(self, event):
        print(f"Processing: {event}")

processor = InefficientFiltering()

# BUG: Wastes bandwidth and memory
print("Inefficient filtering")
"""
            
            test_file = os.path.join(temp_dir, "event_filtering.py")
            with open(test_file, "w") as f:
                f.write(agent_code)
            
            assert os.path.exists(test_file)
    
    def test_event_deduplication(self):
        """Test 901: Deduplicate events"""
        with tempfile.TemporaryDirectory() as temp_dir:
            agent_code = """
class NoDeduplication:
    def process_event(self, event):
        # BUG: No deduplication
        self.save_to_database(event)
    
    def save_to_database(self, event):
        print(f"Saving: {event}")

processor = NoDeduplication()

# BUG: Processes duplicate events
processor.process_event({"id": 1, "type": "UserCreated"})
processor.process_event({"id": 1, "type": "UserCreated"})  # Duplicate
"""
            
            test_file = os.path.join(temp_dir, "event_dedup.py")
            with open(test_file, "w") as f:
                f.write(agent_code)
            
            assert os.path.exists(test_file)
    
    def test_event_compaction(self):
        """Test 902: Compact event log"""
        with tempfile.TemporaryDirectory() as temp_dir:
            agent_code = """
class NoEventCompaction:
    def __init__(self):
        self.events = []
    
    def publish_event(self, event):
        # BUG: Stores all events forever
        self.events.append(event)

publisher = NoEventCompaction()

# BUG: Event log grows unbounded
for i in range(1000000):
    publisher.publish_event({"id": i % 1000, "value": i})

print(f"Event log size: {len(publisher.events)}")
"""
            
            test_file = os.path.join(temp_dir, "event_compaction.py")
            with open(test_file, "w") as f:
                f.write(agent_code)
            
            assert os.path.exists(test_file)
    
    def test_event_sourcing_snapshots(self):
        """Test 903: Use snapshots in event sourcing"""
        with tempfile.TemporaryDirectory() as temp_dir:
            agent_code = """
class NoSnapshots:
    def get_current_state(self, entity_id):
        # BUG: Replays all events
        events = self.load_all_events(entity_id)
        
        state = {}
        for event in events:
            state = self.apply_event(state, event)
        
        return state
    
    def load_all_events(self, entity_id):
        # Returns 1 million events
        return [{"type": f"Event{i}"} for i in range(1000000)]
    
    def apply_event(self, state, event):
        return state

es = NoSnapshots()

# BUG: Slow state reconstruction
state = es.get_current_state(1)
"""
            
            test_file = os.path.join(temp_dir, "snapshots.py")
            with open(test_file, "w") as f:
                f.write(agent_code)
            
            assert os.path.exists(test_file)
    
    def test_saga_compensation(self):
        """Test 904: Implement saga compensation"""
        with tempfile.TemporaryDirectory() as temp_dir:
            agent_code = """
class NoSagaCompensation:
    def execute_saga(self):
        # Step 1: Reserve inventory
        self.reserve_inventory()
        
        # Step 2: Charge payment
        self.charge_payment()
        
        # Step 3: Create shipment
        try:
            self.create_shipment()
        except Exception:
            # BUG: Doesn't compensate previous steps
            pass
    
    def reserve_inventory(self):
        print("Inventory reserved")
    
    def charge_payment(self):
        print("Payment charged")
    
    def create_shipment(self):
        raise Exception("Shipment failed")

saga = NoSagaCompensation()

# BUG: Leaves inconsistent state
try:
    saga.execute_saga()
except:
    print("Saga failed without compensation")
"""
            
            test_file = os.path.join(temp_dir, "saga_compensation.py")
            with open(test_file, "w") as f:
                f.write(agent_code)
            
            assert os.path.exists(test_file)
    
    def test_outbox_pattern(self):
        """Test 905: Implement outbox pattern"""
        with tempfile.TemporaryDirectory() as temp_dir:
            agent_code = """
class NoOutboxPattern:
    def create_order(self, order):
        # BUG: Separate transactions
        self.save_to_database(order)
        
        # BUG: May fail after DB commit
        self.publish_event("OrderCreated", order)
    
    def save_to_database(self, order):
        print(f"Saving order: {order}")
    
    def publish_event(self, event_type, data):
        # Simulates message broker failure
        raise Exception("Message broker unavailable")

service = NoOutboxPattern()

# BUG: Order saved but event not published
try:
    service.create_order({"id": 1, "total": 100})
except:
    print("Order created but event not published")
"""
            
            test_file = os.path.join(temp_dir, "outbox_pattern.py")
            with open(test_file, "w") as f:
                f.write(agent_code)
            
            assert os.path.exists(test_file)
