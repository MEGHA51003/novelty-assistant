# AI Project Assistant - Technical Specification

## 1. Project Overview

**Project Name:** AI Project Assistant  
**Type:** Full-stack AI-powered project management application  
**Core Functionality:** A chat-based assistant where users can interact with AI (Claude) about their projects, generate and analyze images, and maintain organized project knowledge using AI memory tools.  
**Target Users:** Developers, designers, and project managers who need AI assistance with project-related tasks.

---

## 2. Tech Stack

- **Backend:** Python 3.11+ with FastAPI
- **AI - Chat/Tools/Memory:** Anthropic Claude API
- **AI - Image Analysis:** Google Gemini API
- **AI - Image Generation:** Replicate API (or mock implementation)
- **Database:** Supabase (PostgreSQL)
- **Authentication:** Simple user-based auth (extensible to OAuth)

---

## 3. Database Schema Design

### Design Decisions

1. **Projects as the central entity** - All content (messages, images, memory) is scoped to projects
2. **Separate message history** - Full conversation history for context
3. **Image storage with metadata** - Track generation source, analysis results
4. **Memory as structured JSON** - Flexible storage for AI-organized knowledge
5. **Agent execution tracking** - Async job status for background processing

### Tables

#### `users`
```sql
CREATE TABLE users (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    email VARCHAR(255) UNIQUE NOT NULL,
    name VARCHAR(255),
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);
```

#### `projects`
```sql
CREATE TABLE projects (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
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
```

#### `conversations`
```sql
CREATE TABLE conversations (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    project_id UUID NOT NULL REFERENCES projects(id) ON DELETE CASCADE,
    title VARCHAR(255),
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);
```

#### `messages`
```sql
CREATE TABLE messages (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    conversation_id UUID NOT NULL REFERENCES conversations(id) ON DELETE CASCADE,
    role VARCHAR(20) NOT NULL CHECK (role IN ('user', 'assistant', 'system')),
    content TEXT NOT NULL,
    metadata JSONB DEFAULT '{}',
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);
```

#### `images`
```sql
CREATE TABLE images (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    project_id UUID NOT NULL REFERENCES projects(id) ON DELETE CASCADE,
    conversation_id UUID REFERENCES conversations(id) ON DELETE SET NULL,
    prompt TEXT,
    image_url TEXT NOT NULL,
    storage_type VARCHAR(50) DEFAULT 'url',
    analysis_result TEXT,
    analyzed_at TIMESTAMP WITH TIME ZONE,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);
```

#### `project_memory`
```sql
CREATE TABLE project_memory (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    project_id UUID NOT NULL REFERENCES projects(id) ON DELETE CASCADE,
    memory_type VARCHAR(50) NOT NULL,
    title VARCHAR(255),
    content JSONB NOT NULL,
    metadata JSONB DEFAULT '{}',
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);
```

#### `agent_executions`
```sql
CREATE TABLE agent_executions (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
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
```

---

## 4. API Endpoints

### Authentication
| Method | Endpoint | Description |
|--------|----------|-------------|
| POST | `/api/auth/register` | Register new user |
| POST | `/api/auth/login` | Login user |
| GET | `/api/auth/me` | Get current user |

### Projects
| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/api/projects` | List user's projects |
| POST | `/api/projects` | Create new project |
| GET | `/api/projects/{id}` | Get project details |
| PUT | `/api/projects/{id}` | Update project |
| DELETE | `/api/projects/{id}` | Delete project |

### Briefs
| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/api/projects/{id}/brief` | Get project brief |
| PUT | `/api/projects/{id}/brief` | Update project brief |

### Conversations
| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/api/projects/{id}/conversations` | List project conversations |
| POST | `/api/projects/{id}/conversations` | Create new conversation |
| GET | `/api/conversations/{id}` | Get conversation with messages |
| DELETE | `/api/conversations/{id}` | Delete conversation |

### Chat
| Method | Endpoint | Description |
|--------|----------|-------------|
| POST | `/api/chat/{conversation_id}` | Send message and get AI response |
| GET | `/api/chat/{conversation_id}/history` | Get chat history |

### Images
| Method | Endpoint | Description |
|--------|----------|-------------|
| POST | `/api/projects/{id}/images/generate` | Generate image |
| GET | `/api/projects/{id}/images` | List project images |
| POST | `/api/images/{id}/analyze` | Analyze image with Gemini |
| DELETE | `/api/images/{id}` | Delete image |

### Memory
| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/api/projects/{id}/memory` | Get project memory |
| POST | `/api/projects/{id}/memory` | Add manual memory entry |
| PUT | `/api/memory/{id}` | Update memory entry |
| DELETE | `/api/memory/{id}` | Delete memory entry |

### Agent
| Method | Endpoint | Description |
|--------|----------|-------------|
| POST | `/api/projects/{id}/agents/organize` | Trigger memory organization agent |
| GET | `/api/agents/{id}` | Get agent execution status |
| GET | `/api/projects/{id}/agents` | List project agent executions |

---

## 5. Core Features

### 5.1 Chat System

**User Flow:**
1. User selects a project
2. User sends a message in a conversation
3. Backend creates/retrieves conversation
4. Backend fetches recent messages for context
5. Backend checks project memory for relevant context
6. Backend sends message to Claude with tools
7. Claude processes message and may use tools (read memory, write memory, analyze image)
8. Response is returned and stored in database
9. Real-time updates via polling or WebSocket (simplified: polling)

**Claude Tools Available:**
- `read_memory` - Read project memory entries
- `write_memory` - Write new memory entry
- `update_memory` - Update existing memory
- `search_memory` - Search memory for relevant info
- `analyze_image` - Send image URL to Gemini for analysis

### 5.2 Image Generation

**Options (in order of preference):**
1. **Replicate API** (Flux model) - Real image generation
2. **OpenAI DALL-E** - Alternative image generation
3. **Mock Implementation** - Returns placeholder URLs for testing

**Generated images are:**
- Stored with project reference
- Linked to conversation where generated
- Available for later analysis

### 5.3 Image Analysis

**Flow:**
1. User asks Claude about an image
2. Claude uses `analyze_image` tool
3. Backend sends image URL to Gemini API
4. Gemini returns analysis
5. Claude incorporates analysis into response

### 5.4 Memory System

**Memory Types:**
- `context` - Project background and context
- `decisions` - Key decisions made
- `todos` - Tasks and action items
- `facts` - Important facts and information
- `concepts` - Key concepts and definitions

**Claude Memory Behavior:**
1. On each message, Claude searches memory for relevant context
2. Relevant memories are included in system prompt
3. Claude can write new memories when user provides key info
4. Memory is project-scoped (not shared across projects)

### 5.5 Background Agent

**Memory Organization Agent:**
1. Triggered via API endpoint
2. Reads project's brief, messages, and existing memory
3. Organizes information into structured memory entries
4. Updates `agent_executions` status throughout process
5. Can be polled for status

**Execution Flow:**
1. Create `agent_execution` record with status `pending`
2. Background worker picks up task, sets status to `running`
3. Agent processes all project data
4. Agent creates/updates memory entries
5. Status set to `completed` or `failed`

---

## 6. Claude Tools Schema

### read_memory
```json
{
  "name": "read_memory",
  "description": "Read memory entries from the project knowledge base",
  "input_schema": {
    "type": "object",
    "properties": {
      "memory_type": {
        "type": "string",
        "enum": ["context", "decisions", "todos", "facts", "concepts"],
        "description": "Type of memory to read"
      }
    }
  }
}
```

### write_memory
```json
{
  "name": "write_memory",
  "description": "Write a new memory entry to the project knowledge base",
  "input_schema": {
    "type": "object",
    "properties": {
      "memory_type": {
        "type": "string",
        "enum": ["context", "decisions", "todos", "facts", "concepts"],
        "description": "Type of memory"
      },
      "title": {"type": "string", "description": "Memory title"},
      "content": {"type": "object", "description": "Memory content as structured data"}
    },
    "required": ["memory_type", "title", "content"]
  }
}
```

### analyze_image
```json
{
  "name": "analyze_image",
  "description": "Analyze an image using AI vision capabilities",
  "input_schema": {
    "type": "object",
    "properties": {
      "image_url": {"type": "string", "description": "URL of the image to analyze"},
      "question": {"type": "string", "description": "Specific question about the image"}
    },
    "required": ["image_url"]
  }
}
```

---

## 7. Project Structure

```
ai-project-assistant/
├── app/
│   ├── __init__.py
│   ├── main.py                 # FastAPI application entry
│   ├── config.py               # Configuration settings
│   ├── database.py             # Database connection
│   ├── models/
│   │   ├── __init__.py
│   │   ├── user.py
│   │   ├── project.py
│   │   ├── conversation.py
│   │   ├── message.py
│   │   ├── image.py
│   │   ├── memory.py
│   │   └── agent.py
│   ├── schemas/
│   │   ├── __init__.py
│   │   ├── user.py
│   │   ├── project.py
│   │   ├── conversation.py
│   │   ├── message.py
│   │   ├── image.py
│   │   ├── memory.py
│   │   └── agent.py
│   ├── routers/
│   │   ├── __init__.py
│   │   ├── auth.py
│   │   ├── projects.py
│   │   ├── conversations.py
│   │   ├── chat.py
│   │   ├── images.py
│   │   ├── memory.py
│   │   └── agents.py
│   ├── services/
│   │   ├── __init__.py
│   │   ├── claude_service.py   # Claude API integration
│   │   ├── gemini_service.py   # Gemini API integration
│   │   ├── image_service.py    # Image generation
│   │   └── agent_service.py    # Background agent
│   ├── agents/
│   │   ├── __init__.py
│   │   └── memory_agent.py     # Memory organization agent
│   └── utils/
│       ├── __init__.py
│       └── helpers.py
├── migrations/
│   └── 001_initial_schema.sql  # Database migrations
├── tests/
│   ├── __init__.py
│   ├── test_auth.py
│   ├── test_projects.py
│   ├── test_chat.py
│   └── test_agent.py
├── .env.example
├── requirements.txt
├── SPEC.md
└── README.md
```

---

## 8. Environment Variables

```env
# Supabase
SUPABASE_URL=
SUPABASE_KEY=
SUPABASE_SERVICE_KEY=

# Anthropic Claude
ANTHROPIC_API_KEY=

# Google Gemini
GEMINI_API_KEY=

# Image Generation (Replicate)
REPLICATE_API_TOKEN=

# Server
HOST=0.0.0.0
PORT=8000
DEBUG=true
```

---

## 9. Acceptance Criteria

### Chat
- [ ] User can create a project and start a conversation
- [ ] Messages are stored in database
- [ ] Claude responds with context from project memory
- [ ] Claude can use tools (read/write memory, analyze images)

### Projects & Briefs
- [ ] User can CRUD projects
- [ ] Projects have briefs with all required fields
- [ ] Briefs are stored in database

### Images
- [ ] User can generate images (real or mock)
- [ ] Images are stored and linked to projects
- [ ] Claude can analyze images using Gemini

### Memory
- [ ] Memory is scoped per project
- [ ] Claude checks memory before responding
- [ ] Claude can write new memories

### Agent
- [ ] Agent can be triggered via API
- [ ] Agent execution status is trackable
- [ ] Agent organizes project data into structured memory

### Code Quality
- [ ] Clean project structure
- [ ] Type hints throughout
- [ ] Error handling
- [ ] API documentation with OpenAPI
