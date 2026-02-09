-- ============================================================================
-- TODO APP DATABASE SCHEMA
-- Database: neondb (Neon PostgreSQL)
-- Date: 2026-02-09
-- ============================================================================
-- RUN THIS SCRIPT DIRECTLY IN NEON SQL EDITOR
-- ============================================================================

-- Enable UUID extension if not already enabled
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";

-- ============================================================================
-- USERS TABLE
-- ============================================================================
CREATE TABLE IF NOT EXISTS users (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    email VARCHAR(255) NOT NULL UNIQUE,
    name VARCHAR(255),
    password_hash VARCHAR(255) NOT NULL,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

-- Create index on email for fast lookups during login
CREATE INDEX IF NOT EXISTS idx_users_email ON users(email);

-- ============================================================================
-- TASKS TABLE
-- ============================================================================
CREATE TABLE IF NOT EXISTS tasks (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    title VARCHAR(500) NOT NULL,
    description TEXT,
    completed BOOLEAN DEFAULT FALSE,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

-- Create indexes on tasks for performance
CREATE INDEX IF NOT EXISTS idx_tasks_user_id ON tasks(user_id);
CREATE INDEX IF NOT EXISTS idx_tasks_created_at ON tasks(created_at);
CREATE INDEX IF NOT EXISTS idx_tasks_user_created ON tasks(user_id, created_at DESC);

-- ============================================================================
-- VERIFICATION
-- ============================================================================

-- Display all tables created
SELECT
    'SCHEMA CREATION COMPLETE' as status,
    COUNT(*) as table_count
FROM information_schema.tables
WHERE table_schema = 'public'
AND table_type = 'BASE TABLE';

-- Display tables
SELECT table_name FROM information_schema.tables
WHERE table_schema = 'public'
AND table_type = 'BASE TABLE'
ORDER BY table_name;

-- Display indexes
SELECT
    indexname,
    tablename
FROM pg_indexes
WHERE schemaname = 'public'
ORDER BY tablename, indexname;

-- ============================================================================
-- Sample Data (Optional - uncomment to add test data)
-- ============================================================================

-- Insert test user
-- INSERT INTO users (email, name, password_hash)
-- VALUES ('test@example.com', 'Test User', 'hashed_password_here');

-- Insert test task (replace user_id with actual UUID from previous insert)
-- INSERT INTO tasks (user_id, title, description, completed)
-- VALUES ('550e8400-e29b-41d4-a716-446655440000', 'Buy groceries', 'Milk, eggs, bread', false);

-- ============================================================================
-- END OF SCHEMA CREATION SCRIPT
-- ============================================================================
