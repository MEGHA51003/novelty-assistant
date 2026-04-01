**AI Project Assistant**

An AI-powered project assistant where users can chat with AI about their projects, generate and analyze images, and organize project knowledge using AI agents.

**Features**
- Chat with AI - Get AI assistance on your projects with full conversation history
- Project Management - Create and manage projects with briefs (title, description, goals, reference links, tags)
- Image Generation - Generate images from text prompts (stored in database, linked to project)
- Image Analysis - AI can analyze images using Gemini vision API
- Memory System - Project-scoped AI memory that persists across conversations
- Background Agent - Automatically organizes project knowledge into structured memory with status tracking

**Tech Stack**
- Backend: Python 3.11+ with FastAPI
- AI Chat: Ollama (Llama 3.2) - free local AI model
- AI Vision: Google Gemini API
- Image Generation: Placeholder service (can integrate Replicate/OpenAI for production)
- Database: Supabase (PostgreSQL)

**Schema Design Decisions**

**Why This Schema?**
1. Project-Centric Design - Everything revolves around projects. Users can have multiple projects, each with its own context, conversations, and memory.
2. Separate Conversation Model - Allows users to have multiple chat threads per project, keeping discussions organized.
3. Message History - Full conversation history stored in DB for:
   - Context preservation
   - Debugging
   - User reference
4. Images Table - Stores generated/uploaded images with:
   - Link to project and conversation
   - Prompt used for generation
   - Analysis results from Gemini
   - Metadata for the generation
5. Memory as JSONB - Flexible schema for storing AI-organized knowledge:
   - context - Project background and team info
   - decisions - Key decisions made and rationale
   - todos - Action items and tasks
   - facts - Important facts and requirements
   - concepts - Technical concepts and terminology
6. Agent Executions Table - Tracks async background jobs:
   - Status tracking (pending, running, completed, failed)
   - Input/output data for debugging
   - Timestamps for monitoring
   - Project-scoped execution history
   
**API Endpoints**

### Projects
| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/api/projects` | List all projects |
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
| POST | `/api/projects/{id}/memory` | Add memory entry |
| PUT | `/api/memory/{id}` | Update memory entry |
| DELETE | `/api/memory/{id}` | Delete memory entry |

### Agent
| Method | Endpoint | Description |
|--------|----------|-------------|
| POST | `/api/projects/{id}/agents/organize` | Trigger memory organization agent |
| GET | `/api/agents/{id}` | Get agent execution status |
| GET | `/api/projects/{id}/agents` | List project agent executions |

**Agent System**

**Memory Organization Agent**
The background agent processes a project's data and organizes it into structured memory:
1. Triggered via API - POST to /api/projects/{id}/agents/organize
2. Creates execution record - Status starts as "pending"
3. Reads all project data - Brief, conversations, existing memory
4. Analyzes with AI - Organizes into categories:
   - Project context and background
   - Key decisions and their rationale
   - Action items and tasks
   - Important facts and constraints
   - Technical concepts and definitions
5. Saves to memory - Creates memory entries in database
6. Updates status - Marks as "completed" or "failed" 
Agent Flow
[API Trigger] → [pending] → [running] → [completed/failed]
                                      ↓
                           [Creates memory entries]
Tool Loop
The AI has access to tools during conversations:
1. read_memory - Read project memory entries
2. write_memory - Save important information to memory  
3. analyze_image - Analyze images using Gemini
When AI needs to use a tool, it returns a tool call which is executed, and the result is sent back to the AI for final response.
Demo Mode
The application runs in demo mode without authentication:
- All requests are automatically associated with a demo user
- No login required - just start using the app
- Perfect for testing and demonstration
Setup
1. Install Dependencies
pip install -r requirements.txt
2. Configure Environment
Copy .env.example to .env and add your credentials:
# Supabase (required)
SUPABASE_URL=your_supabase_url
SUPABASE_KEY=your_supabase_anon_key
SUPABASE_SERVICE_KEY=your_supabase_service_key
# AI Services (optional - will use mock if not provided)
GEMINI_API_KEY=your_gemini_api_key
REPLICATE_API_TOKEN=your_replicate_token
3. Set Up Database
Create tables in Supabase using the migration file in migrations/001_initial_schema.sql
4. Run Ollama (for AI Chat)
# Install Ollama from https://ollama.ai/
ollama serve
ollama pull llama3.2
5. Run Server
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
6. Run Frontend
Option A - Using Python:
python -m http.server 8080
Then open: http://localhost:8080/chat.html
Option B - Using VS Code Live Server:
Right-click chat.html → Open with Live Server
Project Structure
novelty-assistant/
├── app/
│   ├── main.py              # FastAPI entry point
│   ├── config.py            # Configuration
│   ├── database.py          # Supabase connection
│   ├── schemas/             # Pydantic schemas
│   ├── routers/             # API routes (projects, chat, images, etc.)
│   ├── services/            # External API services (ollama, gemini)
│   └── agents/              # Background agents
├── migrations/             # Database migrations
├── tests/                   # Unit tests
├── chat.html               # Frontend UI
├── .env                    # Environment variables
└── README.md
Known Limitations
1. Tool Loop with Ollama - The free Ollama model may not always follow the tool call format perfectly. Claude API would perform better but requires paid subscription.
2. Image Generation - Currently uses placeholder images. For production, integrate Replicate API or DALL-E with proper API keys.
3. Demo Mode - Runs without authentication. For production, implement proper auth.
License
MIT
