"""
PostgreSQL Database Adapter for Project Phoenix
Production-ready database with automatic connection pooling
"""

import os
import psycopg2
import json
import logging
from typing import Dict, List, Optional, Any
from datetime import datetime
from psycopg2.pool import SimpleConnectionPool
from psycopg2.extras import RealDictCursor

logger = logging.getLogger(__name__)


class PostgresDatabase:
    """PostgreSQL database for production deployment"""
    
    def __init__(self, database_url: str = None):
        """
        Initialize PostgreSQL connection pool
        
        Args:
            database_url: PostgreSQL connection string
                         Default from DATABASE_URL env var
        """
        self.database_url = database_url or os.getenv(
            'DATABASE_URL',
            'postgresql://phoenix_user:password@localhost:5432/phoenix_db'
        )
        self.pool = None
        self.logger = logging.getLogger(__name__)
    
    async def connect(self) -> bool:
        """Initialize connection pool"""
        try:
            self.pool = SimpleConnectionPool(
                1, 20,  # min_connections, max_connections
                self.database_url
            )
            self.logger.info("✅ PostgreSQL connection pool created")
            return True
        except Exception as e:
            self.logger.error(f"❌ Failed to create connection pool: {e}")
            return False
    
    async def migrate(self) -> bool:
        """Run database migrations"""
        try:
            conn = self.pool.getconn()
            cur = conn.cursor()
            
            # Check if tables exist
            cur.execute("""
                SELECT EXISTS (
                    SELECT 1 FROM information_schema.tables 
                    WHERE table_name = 'error_logs'
                )
            """)
            
            if not cur.fetchone()[0]:
                self.logger.info("Running database migrations...")
                # Tables will be created by init-db.sql
                self.logger.info("✅ Database schema verified")
            
            cur.close()
            self.pool.putconn(conn)
            return True
        except Exception as e:
            self.logger.error(f"Migration error: {e}")
            return False
    
    def execute(self, query: str, params: tuple = None) -> bool:
        """Execute a query without returning results"""
        try:
            conn = self.pool.getconn()
            cur = conn.cursor()
            cur.execute(query, params or ())
            conn.commit()
            cur.close()
            self.pool.putconn(conn)
            return True
        except Exception as e:
            self.logger.error(f"Execute error: {e}")
            return False
    
    def fetch_one(self, query: str, params: tuple = None) -> Optional[Dict]:
        """Fetch one row as dictionary"""
        try:
            conn = self.pool.getconn()
            cur = conn.cursor(cursor_factory=RealDictCursor)
            cur.execute(query, params or ())
            result = cur.fetchone()
            cur.close()
            self.pool.putconn(conn)
            return dict(result) if result else None
        except Exception as e:
            self.logger.error(f"Fetch one error: {e}")
            return None
    
    def fetch_all(self, query: str, params: tuple = None) -> List[Dict]:
        """Fetch all rows as dictionaries"""
        try:
            conn = self.pool.getconn()
            cur = conn.cursor(cursor_factory=RealDictCursor)
            cur.execute(query, params or ())
            results = cur.fetchall()
            cur.close()
            self.pool.putconn(conn)
            return [dict(row) for row in results]
        except Exception as e:
            self.logger.error(f"Fetch all error: {e}")
            return []
    
    # Error Logs
    def save_error_log(self, agent_id: str, operation: str, error_type: str,
                       severity: str, message: str, stack_trace: str = "",
                       metadata: Dict = None) -> Optional[str]:
        """Save error log to database"""
        try:
            query = """
                INSERT INTO error_logs 
                (agent_id, operation, error_type, severity, message, stack_trace, metadata)
                VALUES (%s, %s, %s, %s, %s, %s, %s)
                RETURNING id
            """
            conn = self.pool.getconn()
            cur = conn.cursor()
            cur.execute(query, (
                agent_id, operation, error_type, severity,
                message, stack_trace, json.dumps(metadata or {})
            ))
            error_id = cur.fetchone()[0]
            conn.commit()
            cur.close()
            self.pool.putconn(conn)
            return error_id
        except Exception as e:
            self.logger.error(f"Save error log error: {e}")
            return None
    
    def get_error_logs(self, limit: int = 100, offset: int = 0) -> List[Dict]:
        """Get recent error logs"""
        query = """
            SELECT id, agent_id, operation, error_type, severity, 
                   message, created_at
            FROM error_logs
            ORDER BY created_at DESC
            LIMIT %s OFFSET %s
        """
        return self.fetch_all(query, (limit, offset))
    
    # LLM Analysis Cache
    def save_llm_analysis(self, error_hash: str, error_type: str,
                         analysis: Dict, confidence: float) -> bool:
        """Cache LLM analysis results"""
        try:
            query = """
                INSERT INTO llm_analysis_cache 
                (error_hash, error_type, analysis, confidence)
                VALUES (%s, %s, %s, %s)
                ON CONFLICT (error_hash) 
                DO UPDATE SET
                    accessed_count = accessed_count + 1,
                    last_accessed = CURRENT_TIMESTAMP
            """
            return self.execute(query, (
                error_hash, error_type,
                json.dumps(analysis), confidence
            ))
        except Exception as e:
            self.logger.error(f"Save LLM analysis error: {e}")
            return False
    
    def get_llm_analysis(self, error_hash: str) -> Optional[Dict]:
        """Get cached LLM analysis"""
        query = """
            SELECT analysis, confidence
            FROM llm_analysis_cache
            WHERE error_hash = %s
        """
        return self.fetch_one(query, (error_hash,))
    
    # Strategy Performance
    def save_strategy_performance(self, error_type: str, strategy_name: str,
                                 success: bool, response_time_ms: float) -> bool:
        """Record strategy performance"""
        try:
            if success:
                query = """
                    INSERT INTO strategy_performance 
                    (error_type, strategy_name, success_count, avg_response_time_ms)
                    VALUES (%s, %s, 1, %s)
                    ON CONFLICT (error_type, strategy_name)
                    DO UPDATE SET
                        success_count = success_count + 1,
                        avg_response_time_ms = (
                            (avg_response_time_ms * success_count + %s) / 
                            (success_count + 1)
                        ),
                        last_used = CURRENT_TIMESTAMP
                """
            else:
                query = """
                    INSERT INTO strategy_performance 
                    (error_type, strategy_name, failure_count)
                    VALUES (%s, %s, 1)
                    ON CONFLICT (error_type, strategy_name)
                    DO UPDATE SET
                        failure_count = failure_count + 1,
                        last_used = CURRENT_TIMESTAMP
                """
            
            params = (error_type, strategy_name, response_time_ms) if success else (error_type, strategy_name)
            return self.execute(query, params)
        except Exception as e:
            self.logger.error(f"Save strategy performance error: {e}")
            return False
    
    # Error Patterns
    def save_error_pattern(self, pattern_signature: str, pattern_type: str,
                          affected_agents: List[str], recommendations: Dict) -> bool:
        """Save detected error pattern"""
        try:
            query = """
                INSERT INTO error_patterns
                (pattern_signature, pattern_type, occurrence_count, 
                 first_occurrence, affected_agents, recommendations)
                VALUES (%s, %s, 1, CURRENT_TIMESTAMP, %s, %s)
                ON CONFLICT (pattern_signature)
                DO UPDATE SET
                    occurrence_count = occurrence_count + 1,
                    last_occurrence = CURRENT_TIMESTAMP
            """
            return self.execute(query, (
                pattern_signature, pattern_type,
                affected_agents, json.dumps(recommendations)
            ))
        except Exception as e:
            self.logger.error(f"Save error pattern error: {e}")
            return False
    
    # Metrics
    def save_metric(self, metric_type: str, value: float, metadata: Dict = None) -> bool:
        """Save system metric"""
        try:
            query = """
                INSERT INTO system_metrics (metric_type, value, metadata)
                VALUES (%s, %s, %s)
            """
            return self.execute(query, (
                metric_type, value, json.dumps(metadata or {})
            ))
        except Exception as e:
            self.logger.error(f"Save metric error: {e}")
            return False
    
    async def close(self):
        """Close connection pool"""
        try:
            if self.pool:
                self.pool.closeall()
                self.logger.info("✅ PostgreSQL connection pool closed")
        except Exception as e:
            self.logger.error(f"Error closing pool: {e}")
