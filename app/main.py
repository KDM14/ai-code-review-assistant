from fastapi import FastAPI
from dotenv import load_dotenv
from app.api.webhooks import router as webhook_router
import os

# Load environment variables
load_dotenv()

app = FastAPI(
    title="AI Code Review Assistant",
    description="An intelligent code review system that provides actionable suggestions",
    version="1.0.0",
    docs_url="/docs"
)

# Include webhook routes - THIS IS THE KEY LINE!
app.include_router(webhook_router, prefix="/api/v1")

@app.get("/")
async def root():
    return {
        "message": "🚀 AI Code Review Assistant API is running!",
        "status": "active",
        "version": "1.0.0",
        "webhook": "/api/v1/webhook/github"
    }

@app.get("/health")
async def health_check():
    return {"status": "healthy"}

@app.get("/api/v1/info")
async def api_info():
    return {
        "name": "AI Code Review Assistant",
        "description": "Provides intelligent code review suggestions using AI",
        "features": [
            "GitHub integration",
            "AI-powered code analysis", 
            "Real-time PR reviews",
            "Security vulnerability detection"
        ],
        "endpoints": {
            "health": "/health",
            "webhook": "/api/v1/webhook/github",
            "docs": "/docs"
        }
    }

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8001, reload=True)