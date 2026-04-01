# AI Project Assistant - Setup with FREE AI

## Quick Start (Using Free Ollama)

### Step 1: Install Ollama (FREE - Runs Locally)

1. Go to https://ollama.com
2. Download and install Ollama for Windows
3. Open terminal and download a model:
```bash
ollama pull llama3.2
```

### Step 2: Configure Environment

Create `.env` file:
```env
# Supabase (create free account at supabase.com)
SUPABASE_URL=https://your-project.supabase.co
SUPABASE_KEY=your-anon-key
SUPABASE_SERVICE_KEY=your-service-key

# FREE AI - Ollama (no API key needed!)
OLLAMA_MODEL=llama3.2

# Optional: Gemini for image analysis (free tier available)
GEMINI_API_KEY=your-gemini-key

# Server
HOST=0.0.0.0
PORT=8000
DEBUG=true
JWT_SECRET_KEY=any-random-secret-key
```

### Step 3: Run

```bash
# Start Ollama (in separate terminal)
ollama serve

# Start the app
pip install -r requirements.txt
uvicorn app.main:app --reload
```

---

## Alternative: Use Groq (FREE API Key)

Get free API key at https://console.groq.com

```env
AI_PROVIDER=groq
GROQ_API_KEY=your-free-key
```

---

## Project Features

- Chat with local AI (no API costs!)
- Project management with briefs
- AI memory that persists across conversations
- Image analysis (with Gemini)
- Background agent for memory organization
