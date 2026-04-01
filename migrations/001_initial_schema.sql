-- AI Project Assistant - Initial Schema
-- This migration creates all tables for the AI project assistant

-- Enable UUID extension
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";

-- Users table
CREATE TABLE IF NOT EXISTS users (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    email VARCHAR(255) UNIQUE NOT NULL,
    name VARCHAR(255),
    hashed_password VARCHAR(255) NOT NULL,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Projects table
CREATE TABLE IF NOT EXISTS projects (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    user_id UUID NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    title VARCHAR(255) NOT NULL,
    description TEXT,
    goals TEXT,
    reference_links JSONB DEFAULT '[]',
    tags JSONB DEFAULT '[]',
    status VARCHAR(50) DEFAULT 'active',
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Conversations table
CREATE TABLE IF NOT EXISTS conversations (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    project_id UUID NOT NULL REFERENCES projects(id) ON DELETE CASCADE,
    title VARCHAR(255),
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Messages table
CREATE TABLE IF NOT EXISTS messages (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    conversation_id UUID NOT NULL REFERENCES conversations(id) ON DELETE CASCADE,
    role VARCHAR(20) NOT NULL CHECK (role IN ('user', 'assistant', 'system')),
    content TEXT NOT NULL,
    metadata JSONB DEFAULT '{}',
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Images table
CREATE TABLE IF NOT EXISTS images (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    project_id UUID NOT NULL REFERENCES projects(id) ON DELETE CASCADE,
    conversation_id UUID REFERENCES conversations(id) ON DELETE SET NULL,
    prompt TEXT,
    image_url TEXT NOT NULL,
    storage_type VARCHAR(50) DEFAULT 'url',
    analysis_result TEXT,
    analyzed_at TIMESTAMP WITH TIME ZONE,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Project memory table
CREATE TABLE IF NOT EXISTS project_memory (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    project_id UUID NOT NULL REFERENCES projects(id) ON DELETE CASCADE,
    memory_type VARCHAR(50) NOT NULL,
    title VARCHAR(255),
    content JSONB NOT NULL,
    metadata JSONB DEFAULT '{}',
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Agent executions table
CREATE TABLE IF NOT EXISTS agent_executions (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    project_id UUID NOT NULL REFERENCES projects(id) ON DELETE CASCADE,
    agent_type VARCHAR(100) NOT NULL,
    status VARCHAR(50) NOT NULL DEFAULT 'pending' CHECK (status IN ('pending', 'running', 'completed', 'failed')),
    input_data JSONB DEFAULT '{}',
    output_data JSONB DEFAULT '{}',
    error_message TEXT,
    started_at TIMESTAMP WITH TIME ZONE,
    completed_at TIMESTAMP WITH TIME ZONE,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Indexes for better query performance
CREATE INDEX IF NOT EXISTS idx_projects_user_id ON projects(user_id);
CREATE INDEX IF NOT EXISTS idx_conversations_project_id ON conversations(project_id);
CREATE INDEX IF NOT EXISTS idx_messages_conversation_id ON messages(conversation_id);
CREATE INDEX IF NOT EXISTS idx_messages_created_at ON messages(created_at DESC);
CREATE INDEX IF NOT EXISTS idx_images_project_id ON images(project_id);
CREATE INDEX IF NOT EXISTS idx_project_memory_project_id ON project_memory(project_id);
CREATE INDEX IF NOT EXISTS idx_project_memory_type ON project_memory(memory_type);
CREATE INDEX IF NOT EXISTS idx_agent_executions_project_id ON agent_executions(project_id);
CREATE INDEX IF NOT EXISTS idx_agent_executions_status ON agent_executions(status);

-- Row Level Security (RLS) policies
ALTER TABLE users ENABLE ROW LEVEL SECURITY;
ALTER TABLE projects ENABLE ROW LEVEL SECURITY;
ALTER TABLE conversations ENABLE ROW LEVEL SECURITY;
ALTER TABLE messages ENABLE ROW LEVEL SECURITY;
ALTER TABLE images ENABLE ROW LEVEL SECURITY;
ALTER TABLE project_memory ENABLE ROW LEVEL SECURITY;
ALTER TABLE agent_executions ENABLE ROW LEVEL SECURITY;

-- Users: Users can only see/edit their own data
CREATE POLICY "Users can view own profile" ON users FOR SELECT USING (auth.uid() = id);
CREATE POLICY "Users can update own profile" ON users FOR UPDATE USING (auth.uid() = id);

-- Projects: Users can only access their own projects
CREATE POLICY "Users can view own projects" ON projects FOR SELECT USING (auth.uid() = user_id);
CREATE POLICY "Users can create own projects" ON projects FOR INSERT WITH CHECK (auth.uid() = user_id);
CREATE POLICY "Users can update own projects" ON projects FOR UPDATE USING (auth.uid() = user_id);
CREATE POLICY "Users can delete own projects" ON projects FOR DELETE USING (auth.uid() = user_id);

-- Conversations: Users can only access conversations in their projects
CREATE POLICY "Users can view own conversations" ON conversations 
    FOR SELECT USING (
        EXISTS (SELECT 1 FROM projects WHERE projects.id = conversations.project_id AND projects.user_id = auth.uid())
    );
CREATE POLICY "Users can create own conversations" ON conversations 
    FOR INSERT WITH CHECK (
        EXISTS (SELECT 1 FROM projects WHERE projects.id = conversations.project_id AND projects.user_id = auth.uid())
    );
CREATE POLICY "Users can delete own conversations" ON conversations 
    FOR DELETE USING (
        EXISTS (SELECT 1 FROM projects WHERE projects.id = conversations.project_id AND projects.user_id = auth.uid())
    );

-- Messages: Users can only access messages in their conversations
CREATE POLICY "Users can view own messages" ON messages 
    FOR SELECT USING (
        EXISTS (
            SELECT 1 FROM conversations c 
            JOIN projects p ON c.project_id = p.id 
            WHERE c.id = messages.conversation_id AND p.user_id = auth.uid()
        )
    );
CREATE POLICY "Users can create own messages" ON messages 
    FOR INSERT WITH CHECK (
        EXISTS (
            SELECT 1 FROM conversations c 
            JOIN projects p ON c.project_id = p.id 
            WHERE c.id = messages.conversation_id AND p.user_id = auth.uid()
        )
    );
CREATE POLICY "Users can delete own messages" ON messages 
    FOR DELETE USING (
        EXISTS (
            SELECT 1 FROM conversations c 
            JOIN projects p ON c.project_id = p.id 
            WHERE c.id = messages.conversation_id AND p.user_id = auth.uid()
        )
    );

-- Images: Users can only access images in their projects
CREATE POLICY "Users can view own images" ON images 
    FOR SELECT USING (EXISTS (SELECT 1 FROM projects WHERE projects.id = images.project_id AND projects.user_id = auth.uid()));
CREATE POLICY "Users can create own images" ON images 
    FOR INSERT WITH CHECK (EXISTS (SELECT 1 FROM projects WHERE projects.id = images.project_id AND projects.user_id = auth.uid()));
CREATE POLICY "Users can delete own images" ON images 
    FOR DELETE USING (EXISTS (SELECT 1 FROM projects WHERE projects.id = images.project_id AND projects.user_id = auth.uid()));

-- Project memory: Users can only access memory in their projects
CREATE POLICY "Users can view own memory" ON project_memory 
    FOR SELECT USING (EXISTS (SELECT 1 FROM projects WHERE projects.id = project_memory.project_id AND projects.user_id = auth.uid()));
CREATE POLICY "Users can create own memory" ON project_memory 
    FOR INSERT WITH CHECK (EXISTS (SELECT 1 FROM projects WHERE projects.id = project_memory.project_id AND projects.user_id = auth.uid()));
CREATE POLICY "Users can update own memory" ON project_memory 
    FOR UPDATE USING (EXISTS (SELECT 1 FROM projects WHERE projects.id = project_memory.project_id AND projects.user_id = auth.uid()));
CREATE POLICY "Users can delete own memory" ON project_memory 
    FOR DELETE USING (EXISTS (SELECT 1 FROM projects WHERE projects.id = project_memory.project_id AND projects.user_id = auth.uid()));

-- Agent executions: Users can only access agents in their projects
CREATE POLICY "Users can view own agents" ON agent_executions 
    FOR SELECT USING (EXISTS (SELECT 1 FROM projects WHERE projects.id = agent_executions.project_id AND projects.user_id = auth.uid()));
CREATE POLICY "Users can create own agents" ON agent_executions 
    FOR INSERT WITH CHECK (EXISTS (SELECT 1 FROM projects WHERE projects.id = agent_executions.project_id AND projects.user_id = auth.uid()));
