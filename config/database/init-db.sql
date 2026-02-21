-- Initialize Phoenix Database
-- PostgreSQL Schema for autonomous self-healing system

-- Create extensions
CREATE EXTENSION IF NOT EXISTS uuid-ossp;
CREATE EXTENSION IF NOT EXISTS jsonb;

-- Users table
CREATE TABLE IF NOT EXISTS users (
    id SERIAL PRIMARY KEY,
    username VARCHAR(255) UNIQUE NOT NULL,
    email VARCHAR(255) UNIQUE NOT NULL,
    password_hash VARCHAR(255) NOT NULL,
    role VARCHAR(50) DEFAULT 'user',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Error logs table
CREATE TABLE IF NOT EXISTS error_logs (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    agent_id VARCHAR(255) NOT NULL,
    operation VARCHAR(255),
    error_type VARCHAR(100) NOT NULL,
    severity VARCHAR(50),
    message TEXT,
    stack_trace TEXT,
    metadata JSONB,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    resolved_at TIMESTAMP,
    INDEX (agent_id),
    INDEX (error_type),
    INDEX (created_at)
);

-- Memory storage table
CREATE TABLE IF NOT EXISTS memory_store (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    agent_id VARCHAR(255),
    memory_type VARCHAR(100),
    content JSONB NOT NULL,
    tags TEXT[],
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    accessed_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    INDEX (agent_id),
    INDEX (memory_type),
    INDEX (created_at)
);

-- LLM analysis cache
CREATE TABLE IF NOT EXISTS llm_analysis_cache (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    error_hash VARCHAR(255) UNIQUE NOT NULL,
    error_type VARCHAR(100),
    analysis JSONB NOT NULL,
    confidence FLOAT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    accessed_count INT DEFAULT 1,
    last_accessed TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    INDEX (error_hash),
    INDEX (created_at)
);

-- Strategy learning table
CREATE TABLE IF NOT EXISTS strategy_performance (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    error_type VARCHAR(100),
    strategy_name VARCHAR(255),
    success_count INT DEFAULT 0,
    failure_count INT DEFAULT 0,
    avg_response_time_ms FLOAT,
    effectiveness FLOAT,
    last_used TIMESTAMP,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    INDEX (error_type),
    INDEX (strategy_name)
);

-- Pattern detection table
CREATE TABLE IF NOT EXISTS error_patterns (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    pattern_signature VARCHAR(255) UNIQUE,
    pattern_type VARCHAR(100),
    occurrence_count INT DEFAULT 1,
    first_occurrence TIMESTAMP,
    last_occurrence TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    affected_agents TEXT[],
    estimated_impact VARCHAR(100),
    recommendations JSONB,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    INDEX (pattern_signature),
    INDEX (pattern_type)
);

-- System metrics table
CREATE TABLE IF NOT EXISTS system_metrics (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    metric_type VARCHAR(100),
    value FLOAT,
    metadata JSONB,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    INDEX (metric_type),
    INDEX (created_at)
);

-- Create indexes for performance
CREATE INDEX IF NOT EXISTS idx_error_logs_timestamp ON error_logs(created_at DESC);
CREATE INDEX IF NOT EXISTS idx_memory_store_timestamp ON memory_store(created_at DESC);
CREATE INDEX IF NOT EXISTS idx_llm_cache_timestamp ON llm_analysis_cache(created_at DESC);

-- Create admin user
INSERT INTO users (username, email, password_hash, role) 
VALUES ('admin', 'admin@phoenix.local', 'admin_hash', 'admin')
ON CONFLICT (username) DO NOTHING;
