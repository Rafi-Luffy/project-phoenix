"""
Core Database Layer
Manages all persistent data storage and schema definitions
"""

from datetime import datetime
from enum import Enum
from typing import Dict, List, Optional, Any
import json
import uuid
import os
from dataclasses import dataclass, asdict, field


class EntityType(Enum):
    AGENT = "agent"
    INCIDENT = "incident"
    CORRECTION = "correction"
    LEARNING_RECORD = "learning_record"
    MEMORY_ENTRY = "memory_entry"
    COMMUNICATION = "communication"
    TASK = "task"


@dataclass
class Agent:
    """Agent entity for multi-agent system"""
    id: str = field(default_factory=lambda: str(uuid.uuid4()))
    name: str = ""
    agent_type: str = ""
    status: str = "inactive"
    capabilities: List[str] = field(default_factory=list)
    created_at: datetime = field(default_factory=datetime.now)
    last_heartbeat: datetime = field(default_factory=datetime.now)
    configuration: Dict[str, Any] = field(default_factory=dict)
    
    def to_dict(self):
        data = asdict(self)
        data['created_at'] = self.created_at.isoformat()
        data['last_heartbeat'] = self.last_heartbeat.isoformat()
        return data


@dataclass
class Incident:
    """System incident/error"""
    id: str = field(default_factory=lambda: str(uuid.uuid4()))
    type: str = ""
    severity: str = "medium"
    description: str = ""
    component: str = ""
    detected_by: str = ""
    detected_at: datetime = field(default_factory=datetime.now)
    status: str = "open"
    error_trace: str = ""
    metadata: Dict[str, Any] = field(default_factory=dict)
    
    def to_dict(self):
        data = asdict(self)
        data['detected_at'] = self.detected_at.isoformat()
        return data


@dataclass
class Correction:
    """Correction applied to fix an incident"""
    id: str = field(default_factory=lambda: str(uuid.uuid4()))
    incident_id: str = ""
    correction_type: str = ""
    applied_by: str = ""
    applied_at: datetime = field(default_factory=datetime.now)
    outcome: str = "pending"
    details: Dict[str, Any] = field(default_factory=dict)
    effectiveness_score: float = 0.0
    
    def to_dict(self):
        data = asdict(self)
        data['applied_at'] = self.applied_at.isoformat()
        return data


@dataclass
class LearningRecord:
    """Record of learning from corrections and feedback"""
    id: str = field(default_factory=lambda: str(uuid.uuid4()))
    incident_id: str = ""
    correction_id: str = ""
    learned_pattern: str = ""
    confidence: float = 0.0
    applicable_domains: List[str] = field(default_factory=list)
    learned_at: datetime = field(default_factory=datetime.now)
    extracted_rules: List[Dict] = field(default_factory=list)
    
    def to_dict(self):
        data = asdict(self)
        data['learned_at'] = self.learned_at.isoformat()
        return data


@dataclass
class MemoryEntry:
    """Memory entry in long-term memory"""
    id: str = field(default_factory=lambda: str(uuid.uuid4()))
    memory_type: str = ""
    content: str = ""
    embedding: List[float] = field(default_factory=list)
    created_at: datetime = field(default_factory=datetime.now)
    last_accessed: datetime = field(default_factory=datetime.now)
    access_count: int = 0
    relevance_score: float = 1.0
    tags: List[str] = field(default_factory=list)
    
    def to_dict(self):
        data = asdict(self)
        data['created_at'] = self.created_at.isoformat()
        data['last_accessed'] = self.last_accessed.isoformat()
        return data


@dataclass
class Communication:
    """Inter-agent communication record"""
    id: str = field(default_factory=lambda: str(uuid.uuid4()))
    sender_id: str = ""
    recipient_id: str = ""
    message_type: str = ""
    content: str = ""
    sent_at: datetime = field(default_factory=datetime.now)
    status: str = "pending"
    priority: int = 5
    payload: Dict[str, Any] = field(default_factory=dict)
    
    def to_dict(self):
        data = asdict(self)
        data['sent_at'] = self.sent_at.isoformat()
        return data


@dataclass
class Task:
    """Task in the orchestration system"""
    id: str = field(default_factory=lambda: str(uuid.uuid4()))
    name: str = ""
    task_type: str = ""
    assigned_to: str = ""
    status: str = "pending"
    priority: int = 5
    created_at: datetime = field(default_factory=datetime.now)
    started_at: Optional[datetime] = None
    completed_at: Optional[datetime] = None
    dependencies: List[str] = field(default_factory=list)
    payload: Dict[str, Any] = field(default_factory=dict)
    result: Optional[str] = None
    
    def to_dict(self):
        data = asdict(self)
        data['created_at'] = self.created_at.isoformat()
        if self.started_at:
            data['started_at'] = self.started_at.isoformat()
        if self.completed_at:
            data['completed_at'] = self.completed_at.isoformat()
        return data


class InMemoryDatabase:
    """In-memory database for development and testing"""
    
    def __init__(self):
        self.agents: Dict[str, Agent] = {}
        self.incidents: Dict[str, Incident] = {}
        self.corrections: Dict[str, Correction] = {}
        self.learning_records: Dict[str, LearningRecord] = {}
        self.memory_entries: Dict[str, MemoryEntry] = {}
        self.communications: Dict[str, Communication] = {}
        self.tasks: Dict[str, Task] = {}
        self.lock = __import__('threading').Lock()
    
    async def connect(self) -> bool:
        """Connect to in-memory database (always succeeds)"""
        return True
    
    async def disconnect(self) -> bool:
        """Disconnect from in-memory database (always succeeds)"""
        return True
    
    def save_agent(self, agent: Agent) -> str:
        with self.lock:
            self.agents[agent.id] = agent
        return agent.id
    
    def get_agent(self, agent_id: str) -> Optional[Agent]:
        with self.lock:
            return self.agents.get(agent_id)
    
    def get_all_agents(self) -> List[Agent]:
        with self.lock:
            return list(self.agents.values())
    
    def save_incident(self, incident: Incident) -> str:
        with self.lock:
            self.incidents[incident.id] = incident
        return incident.id
    
    def get_incident(self, incident_id: str) -> Optional[Incident]:
        with self.lock:
            return self.incidents.get(incident_id)
    
    def get_incidents_by_status(self, status: str) -> List[Incident]:
        with self.lock:
            return [inc for inc in self.incidents.values() if inc.status == status]
    
    def get_all_incidents(self) -> List[Incident]:
        with self.lock:
            return list(self.incidents.values())
    
    def save_correction(self, correction: Correction) -> str:
        with self.lock:
            self.corrections[correction.id] = correction
        return correction.id
    
    def get_correction(self, correction_id: str) -> Optional[Correction]:
        with self.lock:
            return self.corrections.get(correction_id)
    
    def get_corrections_by_incident(self, incident_id: str) -> List[Correction]:
        with self.lock:
            return [cor for cor in self.corrections.values() if cor.incident_id == incident_id]
    
    def save_learning_record(self, record: LearningRecord) -> str:
        with self.lock:
            self.learning_records[record.id] = record
        return record.id
    
    def get_learning_records(self) -> List[LearningRecord]:
        with self.lock:
            return list(self.learning_records.values())
    
    def save_memory_entry(self, entry: MemoryEntry) -> str:
        with self.lock:
            self.memory_entries[entry.id] = entry
        return entry.id
    
    def get_memory_by_tags(self, tags: List[str]) -> List[MemoryEntry]:
        with self.lock:
            results = []
            for entry in self.memory_entries.values():
                if any(tag in entry.tags for tag in tags):
                    results.append(entry)
            return results
    
    def save_communication(self, comm: Communication) -> str:
        with self.lock:
            self.communications[comm.id] = comm
        return comm.id
    
    def get_communications_for_agent(self, agent_id: str) -> List[Communication]:
        with self.lock:
            return [c for c in self.communications.values() 
                   if c.recipient_id == agent_id]
    
    def save_task(self, task: Task) -> str:
        with self.lock:
            self.tasks[task.id] = task
        return task.id
    
    def get_task(self, task_id: str) -> Optional[Task]:
        with self.lock:
            return self.tasks.get(task_id)
    
    def get_tasks_by_status(self, status: str) -> List[Task]:
        with self.lock:
            return [t for t in self.tasks.values() if t.status == status]
    
    def get_tasks_for_agent(self, agent_id: str) -> List[Task]:
        with self.lock:
            return [t for t in self.tasks.values() if t.assigned_to == agent_id]


class PostgreSQLDatabase:
    """PostgreSQL database implementation for production use"""
    
    def __init__(self, dbname: str = "phoenix_db", user: str = None, host: str = "localhost", port: str = "5432"):
        import psycopg2
        import psycopg2.extras
        
        self.dbname = dbname
        self.user = user or os.environ.get('USER')
        self.host = host
        self.port = port
        self.connection = None
        self.psycopg2 = psycopg2
        self.extras = psycopg2.extras
        
    async def connect(self) -> bool:
        """Connect to PostgreSQL database"""
        try:
            self.connection = self.psycopg2.connect(
                dbname=self.dbname,
                user=self.user,
                host=self.host,
                port=self.port
            )
            self.connection.autocommit = True
            print(f"✅ Connected to PostgreSQL database: {self.dbname}")
            return True
        except Exception as e:
            print(f"❌ Failed to connect to database: {e}")
            raise

    async def disconnect(self) -> bool:
        """Disconnect from PostgreSQL database"""
        try:
            self.close()
            return True
        except Exception as e:
            print(f"❌ Failed to disconnect from database: {e}")
            return False

    async def health_check(self) -> Dict[str, Any]:
        """Lightweight database health check."""
        try:
            if not self.connection:
                return {"status": "unhealthy", "database": "postgresql", "error": "not_connected"}

            cursor = self.connection.cursor()
            cursor.execute("SELECT 1")
            cursor.fetchone()
            return {"status": "healthy", "database": "postgresql"}
        except Exception as e:
            return {"status": "unhealthy", "database": "postgresql", "error": str(e)}
    
    async def migrate(self):
        """Run database migrations"""
        cursor = self.connection.cursor()
        
        # Create tables if they don't exist
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS autonomous_system.memory (
                id SERIAL PRIMARY KEY,
                content JSONB NOT NULL,
                memory_type VARCHAR(50) NOT NULL,
                agent_id VARCHAR(100),
                tags TEXT[],
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            );
            
            CREATE TABLE IF NOT EXISTS autonomous_system.errors (
                id SERIAL PRIMARY KEY,
                error_type VARCHAR(50) NOT NULL,
                message TEXT NOT NULL,
                severity VARCHAR(20) NOT NULL,
                context JSONB,
                timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            );
            
            CREATE TABLE IF NOT EXISTS autonomous_system.llm_cache (
                id SERIAL PRIMARY KEY,
                cache_key VARCHAR(255) UNIQUE NOT NULL,
                response JSONB NOT NULL,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            );
            
            CREATE TABLE IF NOT EXISTS autonomous_system.learning_patterns (
                id SERIAL PRIMARY KEY,
                pattern_key VARCHAR(255) UNIQUE NOT NULL,
                pattern_data JSONB NOT NULL,
                confidence_score FLOAT,
                last_updated TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            );
        ''')
        
        print("✅ Database migrations completed")
    
    def store_memory(self, content: Dict[str, Any], memory_type: str, agent_id: str = None, tags: List[str] = None) -> str:
        """Store memory entry"""
        cursor = self.connection.cursor()
        memory_id = str(uuid.uuid4())
        
        cursor.execute('''
            INSERT INTO autonomous_system.memory (id, content, memory_type, agent_id, tags)
            VALUES (%s, %s, %s, %s, %s)
        ''', (memory_id, json.dumps(content), memory_type, agent_id, tags or []))
        
        return memory_id
    
    def retrieve_memory(self, memory_id: str) -> Optional[Dict[str, Any]]:
        """Retrieve memory entry"""
        cursor = self.connection.cursor(cursor_factory=self.extras.RealDictCursor)
        
        cursor.execute('SELECT * FROM autonomous_system.memory WHERE id = %s', (memory_id,))
        result = cursor.fetchone()
        
        if result:
            return dict(result)
        return None
    
    def search_memories(self, query: Dict[str, Any] = None, limit: int = 100) -> List[Dict[str, Any]]:
        """Search memories"""
        cursor = self.connection.cursor(cursor_factory=self.extras.RealDictCursor)
        
        # Simple search for now
        cursor.execute('SELECT * FROM autonomous_system.memory ORDER BY created_at DESC LIMIT %s', (limit,))
        results = cursor.fetchall()
        
        return [dict(row) for row in results]
    
    def store_error(self, error_type: str, message: str, severity: str, context: Dict[str, Any] = None) -> str:
        """Store error record"""
        cursor = self.connection.cursor()
        error_id = str(uuid.uuid4())
        
        cursor.execute('''
            INSERT INTO autonomous_system.errors (id, error_type, message, severity, context)
            VALUES (%s, %s, %s, %s, %s)
        ''', (error_id, error_type, message, severity, json.dumps(context or {})))
        
        return error_id
    
    def get_recent_errors(self, limit: int = 50) -> List[Dict[str, Any]]:
        """Get recent errors"""
        cursor = self.connection.cursor(cursor_factory=self.extras.RealDictCursor)
        
        cursor.execute('SELECT * FROM autonomous_system.errors ORDER BY timestamp DESC LIMIT %s', (limit,))
        results = cursor.fetchall()
        
        return [dict(row) for row in results]
    
    def cache_llm_response(self, cache_key: str, response: Dict[str, Any]) -> None:
        """Cache LLM response"""
        cursor = self.connection.cursor()
        
        cursor.execute('''
            INSERT INTO autonomous_system.llm_cache (cache_key, response)
            VALUES (%s, %s)
            ON CONFLICT (cache_key) DO UPDATE SET
                response = EXCLUDED.response,
                created_at = CURRENT_TIMESTAMP
        ''', (cache_key, json.dumps(response)))
    
    def get_cached_llm_response(self, cache_key: str) -> Optional[Dict[str, Any]]:
        """Get cached LLM response"""
        cursor = self.connection.cursor(cursor_factory=self.extras.RealDictCursor)
        
        cursor.execute('SELECT response FROM autonomous_system.llm_cache WHERE cache_key = %s', (cache_key,))
        result = cursor.fetchone()
        
        if result:
            return result['response']
        return None
    
    def close(self):
        """Close database connection"""
        if self.connection:
            self.connection.close()
            print("✅ Database connection closed")
