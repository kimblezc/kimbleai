from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import os
import json
from datetime import datetime

# Initialize FastAPI
app = FastAPI(title="KimbleAI", version="2.0.0")

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Simple in-memory storage
USERS = {
    "zach@kimbleai.com": {"id": "user1", "name": "Zach Kimble", "role": "admin"},
    "family@kimbleai.com": {"id": "user2", "name": "Family User", "role": "user"}
}

# Data models
class LoginRequest(BaseModel):
    email: str

class ChatRequest(BaseModel):
    message: str
    project_id: str = None

# Routes
@app.get("/")
async def root():
    return {
        "app": "🧠 KimbleAI",
        "version": "2.0.0",
        "status": "Ready for your family!",
        "features": ["Permanent Memory", "Flexible Projects", "AI Intelligence", "User Authentication"],
        "message": "Now with full AI capabilities! (Demo mode - simplified)"
    }

@app.get("/health")
async def health():
    return {"status": "healthy", "message": "KimbleAI backend simplified"}

@app.post("/auth/login")
async def login(request: LoginRequest):
    # Check if user exists
    if request.email not in USERS:
        raise HTTPException(status_code=404, detail="User not found")
    
    user = USERS[request.email]
    
    # Simple token (just the email for demo)
    token = f"demo_token_{request.email}"
    
    return {
        "access_token": token,
        "token_type": "bearer",
        "user": {
            "id": user["id"],
            "email": request.email,
            "name": user["name"],
            "role": user["role"]
        }
    }

@app.get("/projects")
async def get_projects():
    return []

@app.post("/projects")
async def create_project(request: dict):
    return {"id": "demo_project", "name": request.get("name", "Demo Project")}

@app.post("/chat")
async def chat(request: ChatRequest):
    # Simple AI response without OpenAI for now
    responses = [
        "Hello! I'm KimbleAI, your family AI assistant. I'm currently running in demo mode.",
        "I can help you organize documents, manage projects, and remember important family information.",
        "Once we get the full system running, I'll have access to GPT-4 for more intelligent responses!",
        "Feel free to ask me anything - I'm here to help your family stay organized.",
        "This is a demo response. Soon I'll be powered by advanced AI to give you better answers!"
    ]
    
    # Simple response based on message content
    if "hello" in request.message.lower() or "hi" in request.message.lower():
        ai_response = responses[0]
    elif "document" in request.message.lower():
        ai_response = responses[1]
    elif "project" in request.message.lower():
        ai_response = responses[2]
    else:
        ai_response = responses[3]
    
    return {
        "response": ai_response,
        "message_stored": True,
        "project_id": request.project_id,
        "mode": "demo_simplified"
    }

if __name__ == "__main__":
    import uvicorn
    port = int(os.environ.get("PORT", 8000))
    uvicorn.run(app, host="0.0.0.0", port=port)