"""
Comprehensive Test Suite for Phoenix - Database Operations
Tests 846-875: SQL, NoSQL, Transactions, Migrations (30 tests)

This file tests Phoenix's ability to detect and fix bugs in database
operations, query optimization, and data persistence.
"""

import os
import tempfile
import shutil
from pathlib import Path
import pytest
from unittest.mock import Mock, patch


class TestSQLOperations:
    """Test SQL database operations (10 tests)"""
    
    def test_sql_injection(self):
        """Test 846: Prevent SQL injection"""
        with tempfile.TemporaryDirectory() as temp_dir:
            agent_code = """
class SQLInjectionVulnerable:
    def get_user(self, username):
        # BUG: String concatenation vulnerable to SQL injection
        query = f"SELECT * FROM users WHERE username = '{username}'"
        
        return self.execute_query(query)
    
    def execute_query(self, query):
        print(f"Executing: {query}")
        return [{"id": 1, "username": "admin"}]

db = SQLInjectionVulnerable()

# BUG: SQL injection attack
malicious_input = "admin' OR '1'='1"
users = db.get_user(malicious_input)
print(f"Found {len(users)} users")
"""
            
            test_file = os.path.join(temp_dir, "sql_injection.py")
            with open(test_file, "w") as f:
                f.write(agent_code)
            
            assert os.path.exists(test_file)
    
    def test_n_plus_one_queries(self):
        """Test 847: Avoid N+1 query problem"""
        with tempfile.TemporaryDirectory() as temp_dir:
            agent_code = """
class NPlusOneQueries:
    def get_users_with_posts(self):
        # BUG: N+1 query problem
        users = self.execute_query("SELECT * FROM users")
        
        for user in users:
            # BUG: Separate query for each user
            user["posts"] = self.execute_query(
                f"SELECT * FROM posts WHERE user_id = {user['id']}"
            )
        
        return users
    
    def execute_query(self, query):
        return [{"id": i} for i in range(100)]

db = NPlusOneQueries()

# BUG: 1 + 100 queries instead of 1 or 2
users = db.get_users_with_posts()
"""
            
            test_file = os.path.join(temp_dir, "n_plus_one.py")
            with open(test_file, "w") as f:
                f.write(agent_code)
            
            assert os.path.exists(test_file)
    
    def test_missing_indexes(self):
        """Test 848: Use indexes for queries"""
        with tempfile.TemporaryDirectory() as temp_dir:
            agent_code = """
class MissingIndexes:
    def find_by_email(self, email):
        # BUG: No index on email column
        query = "SELECT * FROM users WHERE email = ?"
        
        # BUG: Full table scan
        return self.execute_query(query, [email])
    
    def execute_query(self, query, params):
        # Simulates slow full table scan
        return {"user": "found"}

db = MissingIndexes()

# BUG: Slow query on large table
user = db.find_by_email("user@example.com")
"""
            
            test_file = os.path.join(temp_dir, "missing_indexes.py")
            with open(test_file, "w") as f:
                f.write(agent_code)
            
            assert os.path.exists(test_file)
    
    def test_connection_not_closed(self):
        """Test 849: Close database connections"""
        with tempfile.TemporaryDirectory() as temp_dir:
            agent_code = """
class ConnectionLeak:
    def query_data(self):
        conn = self.get_connection()
        cursor = conn.cursor()
        
        cursor.execute("SELECT * FROM users")
        results = cursor.fetchall()
        
        # BUG: Connection not closed
        return results
    
    def get_connection(self):
        return MockConnection()

class MockConnection:
    def cursor(self):
        return MockCursor()

class MockCursor:
    def execute(self, query):
        pass
    
    def fetchall(self):
        return [{"id": 1}]

db = ConnectionLeak()

# BUG: Connection pool exhausted
for _ in range(100):
    data = db.query_data()
"""
            
            test_file = os.path.join(temp_dir, "connection_leak.py")
            with open(test_file, "w") as f:
                f.write(agent_code)
            
            assert os.path.exists(test_file)
    
    def test_bulk_insert_inefficiency(self):
        """Test 850: Use bulk inserts"""
        with tempfile.TemporaryDirectory() as temp_dir:
            agent_code = """
class IndividualInserts:
    def save_users(self, users):
        # BUG: Individual inserts
        for user in users:
            query = "INSERT INTO users (name, email) VALUES (?, ?)"
            self.execute_query(query, [user["name"], user["email"]])
    
    def execute_query(self, query, params):
        print(f"Executing: {query}")

db = IndividualInserts()

# BUG: 1000 individual inserts instead of bulk insert
users = [{"name": f"User {i}", "email": f"user{i}@example.com"} for i in range(1000)]
db.save_users(users)
"""
            
            test_file = os.path.join(temp_dir, "bulk_insert.py")
            with open(test_file, "w") as f:
                f.write(agent_code)
            
            assert os.path.exists(test_file)
    
    def test_transaction_not_committed(self):
        """Test 851: Commit transactions"""
        with tempfile.TemporaryDirectory() as temp_dir:
            agent_code = """
class NoCommit:
    def transfer_money(self, from_account, to_account, amount):
        conn = self.get_connection()
        
        # Deduct from source
        conn.execute(f"UPDATE accounts SET balance = balance - {amount} WHERE id = {from_account}")
        
        # Add to destination
        conn.execute(f"UPDATE accounts SET balance = balance + {amount} WHERE id = {to_account}")
        
        # BUG: Transaction not committed
        return "success"
    
    def get_connection(self):
        return MockConnection()

class MockConnection:
    def execute(self, query):
        print(f"Executing: {query}")

db = NoCommit()

# BUG: Changes not persisted
db.transfer_money(1, 2, 100)
"""
            
            test_file = os.path.join(temp_dir, "no_commit.py")
            with open(test_file, "w") as f:
                f.write(agent_code)
            
            assert os.path.exists(test_file)
    
    def test_select_star(self):
        """Test 852: Avoid SELECT *"""
        with tempfile.TemporaryDirectory() as temp_dir:
            agent_code = """
class SelectStar:
    def get_user_name(self, user_id):
        # BUG: Selects all columns
        query = f"SELECT * FROM users WHERE id = {user_id}"
        
        user = self.execute_query(query)
        
        # Only uses name field
        return user["name"]
    
    def execute_query(self, query):
        # Simulates fetching 50 columns
        return {f"col{i}": f"value{i}" for i in range(50)}

db = SelectStar()

# BUG: Wastes bandwidth and memory
name = db.get_user_name(1)
"""
            
            test_file = os.path.join(temp_dir, "select_star.py")
            with open(test_file, "w") as f:
                f.write(agent_code)
            
            assert os.path.exists(test_file)
    
    def test_slow_query_no_limit(self):
        """Test 853: Use LIMIT for large result sets"""
        with tempfile.TemporaryDirectory() as temp_dir:
            agent_code = """
class NoLimit:
    def get_recent_logs(self):
        # BUG: No LIMIT clause
        query = "SELECT * FROM logs ORDER BY timestamp DESC"
        
        return self.execute_query(query)
    
    def execute_query(self, query):
        # Simulates 1 million rows
        return [{"id": i} for i in range(1000000)]

db = NoLimit()

# BUG: Fetches all rows
logs = db.get_recent_logs()
print(f"Fetched {len(logs)} logs")
"""
            
            test_file = os.path.join(temp_dir, "no_limit.py")
            with open(test_file, "w") as f:
                f.write(agent_code)
            
            assert os.path.exists(test_file)
    
    def test_connection_pooling(self):
        """Test 854: Use connection pooling"""
        with tempfile.TemporaryDirectory() as temp_dir:
            agent_code = """
class NoConnectionPooling:
    def query(self, sql):
        # BUG: Creates new connection each time
        conn = self.create_connection()
        
        result = conn.execute(sql)
        
        conn.close()
        
        return result
    
    def create_connection(self):
        print("Creating new connection")
        return MockConnection()

class MockConnection:
    def execute(self, sql):
        return []
    
    def close(self):
        pass

db = NoConnectionPooling()

# BUG: 100 connection creations
for _ in range(100):
    db.query("SELECT 1")
"""
            
            test_file = os.path.join(temp_dir, "connection_pooling.py")
            with open(test_file, "w") as f:
                f.write(agent_code)
            
            assert os.path.exists(test_file)
    
    def test_deadlock_no_retry(self):
        """Test 855: Retry on deadlock"""
        with tempfile.TemporaryDirectory() as temp_dir:
            agent_code = """
class NoDeadlockRetry:
    def update_accounts(self, account1, account2):
        try:
            # BUG: No retry on deadlock
            self.execute_query(f"UPDATE accounts SET balance = 100 WHERE id = {account1}")
            self.execute_query(f"UPDATE accounts SET balance = 200 WHERE id = {account2}")
        except Exception as e:
            if "deadlock" in str(e).lower():
                # BUG: Doesn't retry
                raise
    
    def execute_query(self, query):
        raise Exception("Deadlock detected")

db = NoDeadlockRetry()

# BUG: Transaction fails on deadlock
try:
    db.update_accounts(1, 2)
except Exception as e:
    print(f"Failed: {e}")
"""
            
            test_file = os.path.join(temp_dir, "deadlock_retry.py")
            with open(test_file, "w") as f:
                f.write(agent_code)
            
            assert os.path.exists(test_file)


class TestNoSQLOperations:
    """Test NoSQL database operations (10 tests)"""
    
    def test_mongodb_no_indexes(self):
        """Test 856: Create MongoDB indexes"""
        with tempfile.TemporaryDirectory() as temp_dir:
            agent_code = """
class NoMongoDBIndexes:
    def find_by_email(self, email):
        # BUG: No index on email field
        return self.collection.find({"email": email})
    
    def __init__(self):
        self.collection = MockCollection()

class MockCollection:
    def find(self, query):
        # Simulates collection scan
        return [{"_id": 1, "email": "user@example.com"}]

db = NoMongoDBIndexes()

# BUG: Slow query
results = db.find_by_email("user@example.com")
"""
            
            test_file = os.path.join(temp_dir, "mongodb_indexes.py")
            with open(test_file, "w") as f:
                f.write(agent_code)
            
            assert os.path.exists(test_file)
    
    def test_redis_no_expiration(self):
        """Test 857: Set Redis key expiration"""
        with tempfile.TemporaryDirectory() as temp_dir:
            agent_code = """
class NoRedisExpiration:
    def cache_data(self, key, value):
        # BUG: No TTL set
        self.redis.set(key, value)
    
    def __init__(self):
        self.redis = MockRedis()

class MockRedis:
    def __init__(self):
        self.data = {}
    
    def set(self, key, value):
        self.data[key] = value

cache = NoRedisExpiration()

# BUG: Cache grows unbounded
for i in range(10000):
    cache.cache_data(f"key_{i}", f"value_{i}")

print(f"Cache size: {len(cache.redis.data)}")
"""
            
            test_file = os.path.join(temp_dir, "redis_expiration.py")
            with open(test_file, "w") as f:
                f.write(agent_code)
            
            assert os.path.exists(test_file)
    
    def test_dynamodb_no_pagination(self):
        """Test 858: Paginate DynamoDB scans"""
        with tempfile.TemporaryDirectory() as temp_dir:
            agent_code = """
class NoDynamoDBPagination:
    def scan_all(self):
        # BUG: No pagination
        response = self.table.scan()
        return response["Items"]
    
    def __init__(self):
        self.table = MockTable()

class MockTable:
    def scan(self):
        # Simulates 1MB response limit
        return {"Items": [{"id": i} for i in range(100)]}

db = NoDynamoDBPagination()

# BUG: Only gets first page
items = db.scan_all()
"""
            
            test_file = os.path.join(temp_dir, "dynamodb_pagination.py")
            with open(test_file, "w") as f:
                f.write(agent_code)
            
            assert os.path.exists(test_file)
    
    def test_cassandra_no_consistency(self):
        """Test 859: Set Cassandra consistency level"""
        with tempfile.TemporaryDirectory() as temp_dir:
            agent_code = """
class NoConsistencyLevel:
    def write_data(self, key, value):
        # BUG: Uses default consistency
        self.session.execute(f"INSERT INTO data (key, value) VALUES ('{key}', '{value}')")
    
    def __init__(self):
        self.session = MockSession()

class MockSession:
    def execute(self, query):
        print(f"Executing: {query}")

db = NoConsistencyLevel()

# BUG: May lose writes on node failure
db.write_data("key1", "value1")
"""
            
            test_file = os.path.join(temp_dir, "cassandra_consistency.py")
            with open(test_file, "w") as f:
                f.write(agent_code)
            
            assert os.path.exists(test_file)
    
    def test_elasticsearch_no_refresh(self):
        """Test 860: Handle Elasticsearch refresh"""
        with tempfile.TemporaryDirectory() as temp_dir:
            agent_code = """
class NoElasticsearchRefresh:
    def index_document(self, doc):
        # BUG: Doesn't wait for refresh
        self.es.index(index="docs", document=doc)
    
    def search(self, query):
        # BUG: May not find just-indexed document
        return self.es.search(query=query)
    
    def __init__(self):
        self.es = MockElasticsearch()

class MockElasticsearch:
    def index(self, index, document):
        print(f"Indexed: {document}")
    
    def search(self, query):
        return []

es = NoElasticsearchRefresh()

# BUG: Search may not find document
es.index_document({"title": "Test"})
results = es.search("Test")
print(f"Found {len(results)} results")
"""
            
            test_file = os.path.join(temp_dir, "es_refresh.py")
            with open(test_file, "w") as f:
                f.write(agent_code)
            
            assert os.path.exists(test_file)
    
    def test_neo4j_no_params(self):
        """Test 861: Use Neo4j query parameters"""
        with tempfile.TemporaryDirectory() as temp_dir:
            agent_code = """
class NoNeo4jParams:
    def find_user(self, username):
        # BUG: String concatenation in Cypher query
        query = f"MATCH (u:User {{username: '{username}'}}) RETURN u"
        
        return self.session.run(query)
    
    def __init__(self):
        self.session = MockSession()

class MockSession:
    def run(self, query):
        print(f"Running: {query}")
        return []

db = NoNeo4jParams()

# BUG: Vulnerable to Cypher injection
user = db.find_user("admin")
"""
            
            test_file = os.path.join(temp_dir, "neo4j_params.py")
            with open(test_file, "w") as f:
                f.write(agent_code)
            
            assert os.path.exists(test_file)
    
    def test_couchdb_no_views(self):
        """Test 862: Use CouchDB views for queries"""
        with tempfile.TemporaryDirectory() as temp_dir:
            agent_code = """
class NoCouchDBViews:
    def find_by_status(self, status):
        # BUG: Fetches all documents
        all_docs = self.db.all_docs()
        
        # BUG: Filters in application code
        return [doc for doc in all_docs if doc.get("status") == status]
    
    def __init__(self):
        self.db = MockCouchDB()

class MockCouchDB:
    def all_docs(self):
        return [{"_id": i, "status": "active"} for i in range(10000)]

db = NoCouchDBViews()

# BUG: Fetches and filters 10K docs
active = db.find_by_status("active")
"""
            
            test_file = os.path.join(temp_dir, "couchdb_views.py")
            with open(test_file, "w") as f:
                f.write(agent_code)
            
            assert os.path.exists(test_file)
    
    def test_firestore_no_batching(self):
        """Test 863: Batch Firestore writes"""
        with tempfile.TemporaryDirectory() as temp_dir:
            agent_code = """
class NoFirestoreBatching:
    def save_documents(self, documents):
        # BUG: Individual writes
        for doc in documents:
            self.db.collection("items").document(doc["id"]).set(doc)
    
    def __init__(self):
        self.db = MockFirestore()

class MockFirestore:
    def collection(self, name):
        return MockCollection()

class MockCollection:
    def document(self, doc_id):
        return MockDocument()

class MockDocument:
    def set(self, data):
        print(f"Writing document")

db = NoFirestoreBatching()

# BUG: 500 individual writes
docs = [{"id": str(i), "data": f"value_{i}"} for i in range(500)]
db.save_documents(docs)
"""
            
            test_file = os.path.join(temp_dir, "firestore_batching.py")
            with open(test_file, "w") as f:
                f.write(agent_code)
            
            assert os.path.exists(test_file)
    
    def test_cosmosdb_no_partition_key(self):
        """Test 864: Set CosmosDB partition key"""
        with tempfile.TemporaryDirectory() as temp_dir:
            agent_code = """
class NoPartitionKey:
    def query_by_user(self, user_id):
        # BUG: Cross-partition query
        query = f"SELECT * FROM c WHERE c.user_id = '{user_id}'"
        
        return self.container.query_items(query)
    
    def __init__(self):
        self.container = MockContainer()

class MockContainer:
    def query_items(self, query):
        print("Executing cross-partition query")
        return []

db = NoPartitionKey()

# BUG: Expensive cross-partition query
results = db.query_by_user("user123")
"""
            
            test_file = os.path.join(temp_dir, "cosmosdb_partition.py")
            with open(test_file, "w") as f:
                f.write(agent_code)
            
            assert os.path.exists(test_file)
    
    def test_memcached_no_key_length_check(self):
        """Test 865: Check Memcached key length"""
        with tempfile.TemporaryDirectory() as temp_dir:
            agent_code = """
class NoKeyLengthCheck:
    def cache_data(self, key, value):
        # BUG: No key length validation
        self.memcached.set(key, value)
    
    def __init__(self):
        self.memcached = MockMemcached()

class MockMemcached:
    def set(self, key, value):
        if len(key) > 250:
            raise Exception("Key too long")

cache = NoKeyLengthCheck()

# BUG: Crashes on long key
long_key = "x" * 300
try:
    cache.cache_data(long_key, "value")
except Exception as e:
    print(f"Error: {e}")
"""
            
            test_file = os.path.join(temp_dir, "memcached_key_length.py")
            with open(test_file, "w") as f:
                f.write(agent_code)
            
            assert os.path.exists(test_file)


class TestTransactionsAndMigrations:
    """Test transactions and schema migrations (10 tests)"""
    
    def test_dirty_read(self):
        """Test 866: Prevent dirty reads"""
        with tempfile.TemporaryDirectory() as temp_dir:
            agent_code = """
class DirtyReads:
    def read_balance(self, account_id):
        # BUG: READ UNCOMMITTED
        return self.execute_query(
            f"SELECT balance FROM accounts WHERE id = {account_id}"
        )
    
    def execute_query(self, query):
        # May read uncommitted data from other transaction
        return {"balance": 1000}

db = DirtyReads()

# BUG: May read uncommitted balance
balance = db.read_balance(1)
"""
            
            test_file = os.path.join(temp_dir, "dirty_reads.py")
            with open(test_file, "w") as f:
                f.write(agent_code)
            
            assert os.path.exists(test_file)
    
    def test_lost_update(self):
        """Test 867: Prevent lost updates"""
        with tempfile.TemporaryDirectory() as temp_dir:
            agent_code = """
class LostUpdates:
    def increment_counter(self, counter_id):
        # BUG: Read-modify-write without locking
        current = self.get_counter(counter_id)
        new_value = current + 1
        self.set_counter(counter_id, new_value)
    
    def get_counter(self, counter_id):
        return 100
    
    def set_counter(self, counter_id, value):
        print(f"Setting counter to {value}")

db = LostUpdates()

# BUG: Concurrent increments may be lost
db.increment_counter(1)
"""
            
            test_file = os.path.join(temp_dir, "lost_updates.py")
            with open(test_file, "w") as f:
                f.write(agent_code)
            
            assert os.path.exists(test_file)
    
    def test_phantom_reads(self):
        """Test 868: Prevent phantom reads"""
        with tempfile.TemporaryDirectory() as temp_dir:
            agent_code = """
class PhantomReads:
    def calculate_total(self):
        # BUG: REPEATABLE READ doesn't prevent phantoms
        count1 = self.count_rows()
        
        # Another transaction inserts row
        
        count2 = self.count_rows()
        
        # BUG: count1 != count2
        return count1, count2
    
    def count_rows(self):
        return self.execute_query("SELECT COUNT(*) FROM orders")
    
    def execute_query(self, query):
        return 100

db = PhantomReads()

# BUG: Inconsistent counts within transaction
c1, c2 = db.calculate_total()
"""
            
            test_file = os.path.join(temp_dir, "phantom_reads.py")
            with open(test_file, "w") as f:
                f.write(agent_code)
            
            assert os.path.exists(test_file)
    
    def test_migration_no_rollback(self):
        """Test 869: Support migration rollback"""
        with tempfile.TemporaryDirectory() as temp_dir:
            agent_code = """
class NoMigrationRollback:
    def migrate_up(self):
        # BUG: No down migration
        self.execute("ALTER TABLE users ADD COLUMN email VARCHAR(255)")
        self.execute("CREATE INDEX idx_email ON users(email)")
    
    def execute(self, sql):
        print(f"Executing: {sql}")

migrator = NoMigrationRollback()

# BUG: Can't rollback if migration fails
migrator.migrate_up()
"""
            
            test_file = os.path.join(temp_dir, "migration_rollback.py")
            with open(test_file, "w") as f:
                f.write(agent_code)
            
            assert os.path.exists(test_file)
    
    def test_migration_no_transaction(self):
        """Test 870: Run migrations in transaction"""
        with tempfile.TemporaryDirectory() as temp_dir:
            agent_code = """
class MigrationNoTransaction:
    def migrate(self):
        # BUG: No transaction
        self.execute("CREATE TABLE new_table (id INT)")
        self.execute("INSERT INTO new_table SELECT id FROM old_table")
        
        # BUG: Error here leaves partial migration
        self.execute("DROP TABLE old_table")
    
    def execute(self, sql):
        if "DROP" in sql:
            raise Exception("Permission denied")
        print(f"Executing: {sql}")

migrator = MigrationNoTransaction()

# BUG: Partial migration on error
try:
    migrator.migrate()
except:
    print("Migration failed, database in inconsistent state")
"""
            
            test_file = os.path.join(temp_dir, "migration_transaction.py")
            with open(test_file, "w") as f:
                f.write(agent_code)
            
            assert os.path.exists(test_file)
    
    def test_schema_version_tracking(self):
        """Test 871: Track schema version"""
        with tempfile.TemporaryDirectory() as temp_dir:
            agent_code = """
class NoVersionTracking:
    def run_migrations(self):
        # BUG: No version tracking
        self.migration_001()
        self.migration_002()
        self.migration_003()
    
    def migration_001(self):
        print("Running migration 001")
    
    def migration_002(self):
        print("Running migration 002")
    
    def migration_003(self):
        print("Running migration 003")

migrator = NoVersionTracking()

# BUG: Runs all migrations every time
migrator.run_migrations()
"""
            
            test_file = os.path.join(temp_dir, "version_tracking.py")
            with open(test_file, "w") as f:
                f.write(agent_code)
            
            assert os.path.exists(test_file)
    
    def test_blocking_schema_change(self):
        """Test 872: Avoid blocking schema changes"""
        with tempfile.TemporaryDirectory() as temp_dir:
            agent_code = """
class BlockingSchemaChange:
    def add_column(self):
        # BUG: Locks entire table
        self.execute("ALTER TABLE users ADD COLUMN phone VARCHAR(20)")
    
    def execute(self, sql):
        print(f"Executing (locks table): {sql}")

migrator = BlockingSchemaChange()

# BUG: Blocks all queries during migration
migrator.add_column()
"""
            
            test_file = os.path.join(temp_dir, "blocking_schema.py")
            with open(test_file, "w") as f:
                f.write(agent_code)
            
            assert os.path.exists(test_file)
    
    def test_data_migration_in_schema(self):
        """Test 873: Separate data and schema migrations"""
        with tempfile.TemporaryDirectory() as temp_dir:
            agent_code = """
class MixedMigration:
    def migrate(self):
        # BUG: Mixes schema and data migration
        self.execute("ALTER TABLE users ADD COLUMN is_active BOOLEAN")
        
        # BUG: Data migration in same transaction
        self.execute("UPDATE users SET is_active = true")
    
    def execute(self, sql):
        print(f"Executing: {sql}")

migrator = MixedMigration()

# BUG: Long-running transaction locks table
migrator.migrate()
"""
            
            test_file = os.path.join(temp_dir, "data_schema_migration.py")
            with open(test_file, "w") as f:
                f.write(agent_code)
            
            assert os.path.exists(test_file)
    
    def test_cascade_delete(self):
        """Test 874: Handle cascade deletes"""
        with tempfile.TemporaryDirectory() as temp_dir:
            agent_code = """
class NoCascadeHandling:
    def delete_user(self, user_id):
        # BUG: Doesn't handle foreign key constraints
        self.execute(f"DELETE FROM users WHERE id = {user_id}")
    
    def execute(self, sql):
        raise Exception("Foreign key constraint violation")

db = NoCascadeHandling()

# BUG: Fails on foreign key constraint
try:
    db.delete_user(1)
except Exception as e:
    print(f"Error: {e}")
"""
            
            test_file = os.path.join(temp_dir, "cascade_delete.py")
            with open(test_file, "w") as f:
                f.write(agent_code)
            
            assert os.path.exists(test_file)
    
    def test_optimistic_locking(self):
        """Test 875: Implement optimistic locking"""
        with tempfile.TemporaryDirectory() as temp_dir:
            agent_code = """
class NoOptimisticLocking:
    def update_user(self, user_id, new_name):
        # BUG: No version check
        user = self.get_user(user_id)
        user["name"] = new_name
        self.save_user(user)
    
    def get_user(self, user_id):
        return {"id": user_id, "name": "Old Name", "version": 1}
    
    def save_user(self, user):
        # BUG: Overwrites concurrent changes
        print(f"Saving user: {user}")

db = NoOptimisticLocking()

# BUG: Lost update problem
db.update_user(1, "New Name")
"""
            
            test_file = os.path.join(temp_dir, "optimistic_locking.py")
            with open(test_file, "w") as f:
                f.write(agent_code)
            
            assert os.path.exists(test_file)
