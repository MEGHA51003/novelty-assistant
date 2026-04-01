from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.config import settings
from app.routers import auth, projects, conversations, chat, memory, images, agents
app = FastAPI(
    title="AI Project Assistant",
    description="An AI-powered project assistant with chat, image generation, and memory",
    version="1.0.0"
)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000", "http://localhost:8000", "http://127.0.0.1:5500", "file://", "*"],
    allow_credentials=True,
    allow_methods=["GET", "POST", "PUT", "DELETE", "OPTIONS"],
    allow_headers=["*"],
    expose_headers=["*"],
)
app.include_router(auth.router)
app.include_router(projects.router)
app.include_router(conversations.router)
app.include_router(chat.router)
app.include_router(memory.router)
app.include_router(images.router)
app.include_router(agents.router)
@app.get("/")
async def root():
    return {
        "name": "AI Project Assistant",
        "version": "1.0.0",
        "docs": "/docs"
    }
@app.get("/health")
async def health():
    return {"status": "healthy"}
if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "app.main:app",
        host=settings.HOST,
        port=settings.PORT,
        reload=settings.DEBUG
    )