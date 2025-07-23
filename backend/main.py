from fastapi import FastAPI, HTTPException, Depends, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from pydantic import BaseModel
import openai
import os
import jwt
from datetime import datetime, timedelta
from typing import Optional, List

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

# Initialize OpenAI
openai.api_key = os.getenv("OPENAI_API_KEY")
JWT_SECRET = os.getenv("JWT_SECRET_KEY", "kimbleai-jwt-2025")

security = HTTPBearer()

# In-memory storage (temporary replacement for Supabase)
USERS = {
    "zach@kimbleai.com": {"id": "user1", "name": "Zach Kimble", "role": "admin"},
    "family@kimbleai.com": {"id": "user2", "name": "Family User", "role": "user"}
}

PROJECTS = []
CONVERSATIONS = []

# Data models
class LoginRequest(BaseModel):
    email: str

class ChatRequest(BaseModel):
    message: str
    project_id: Optional[str] = None

class ProjectRequest(BaseModel):
    name: str
    description: str = ""
    color: str = "#3b82f6"

# Authentication functions
def create_token(email: str) -> str:
    payload = {
        "email": email,
        "exp": datetime.utcnow() + timedelta(days=30)
    }
    return jwt.encode(payload, JWT_SECRET, algorithm="HS256")

def verify_token(credentials: HTTPAuthorizationCredentials = Depends(security)) -> str:
    try:
        payload = jwt.decode(credentials.credentials, JWT_SECRET, algorithms=["HS256"])
        return payload["email"]
    except jwt.ExpiredSignatureError:
        raise HTTPException(status_code=401, detail="Token expired")
    except jwt.JWTError:
        raise HTTPException(status_code=401, detail="Invalid token")

# Routes
@app.get("/")
async def root():
    return {
        "app": "🧠 KimbleAI",
        "version": "2.0.0",
        "status": "Ready for your family!",
        "features": ["Permanent Memory", "Flexible Projects", "AI Intelligence", "User Authentication"],
        "message": "Now with full AI capabilities! (Demo mode - no database)"
    }

@app.get("/health")
async def health():
    return {"status": "healthy", "message": "KimbleAI backend with AI features (demo mode)"}

@app.post("/auth/login")
async def login(request: LoginRequest):
    # Check if user exists in our demo users
    if request.email not in USERS:
        raise HTTPException(status_code=404, detail="User not found")
    
    user = USERS[request.email]
    token = create_token(request.email)
    
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
async def get_projects(email: str = Depends(verify_token)):
    # Return user's projects from in-memory storage
    user_projects = [p for p in PROJECTS if p.get("user_email") == email]
    return user_projects

@app.post("/projects")
async def create_project(request: ProjectRequest, email: str = Depends(verify_token)):
    # Create project in memory
    project = {
        "id": f"project_{len(PROJECTS) + 1}",
        "user_email": email,
        "name": request.name,
        "description": request.description,
        "color": request.color,
        "created_at": datetime.utcnow().isoformat()
    }
    
    PROJECTS.append(project)
    return project

@app.post("/chat")
async def chat(request: ChatRequest, email: str = Depends(verify_token)):
    try:
        # Create AI response using OpenAI
        response = openai.chat.completions.create(
            model="gpt-4o-mini",
            messages=[
                {
                    "role": "system", 
                    "content": "You are KimbleAI, a family AI assistant with permanent memory. You help with document analysis, project management, and family organization. Be helpful, concise, and remember context from previous conversations. Currently running in demo mode."
                },
                {"role": "user", "content": request.message}
            ],
            max_tokens=500
        )
        
        ai_response = response.choices[0].message.content
        
        # Store conversation in memory
        conversation = {
            "user_email": email,
            "project_id": request.project_id,
            "messages": [
                {"role": "user", "content": request.message, "timestamp": datetime.utcnow().isoformat()},
                {"role": "assistant", "content": ai_response, "timestamp": datetime.utcnow().isoformat()}
            ],
            "created_at": datetime.utcnow().isoformat()
        }
        
        CONVERSATIONS.append(conversation)
        
        return {
            "response": ai_response,
            "message_stored": True,
            "project_id": request.project_id,
            "mode": "demo"
        }
        
    except Exception as e:
        return {
            "response": f"I'm experiencing some technical difficulties. Error: {str(e)}",
            "message_stored": False
        }

if __name__ == "__main__":
    import uvicorn
    port = int(os.environ.get("PORT", 8000))
    uvicorn.run(app, host="0.0.0.0", port=port)