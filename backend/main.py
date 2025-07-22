from fastapi import FastAPI, HTTPException, UploadFile, File, Depends, Form
from fastapi.middleware.cors import CORSMiddleware
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from supabase import create_client, Client
import openai
import os
import json
from datetime import datetime, timedelta
from typing import Optional
from jose import JWTError, jwt
import logging

# Setup
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

from dotenv import load_dotenv
load_dotenv()

app = FastAPI(title="KimbleAI API", version="1.0.0")

# CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Services
supabase: Client = create_client(
    os.getenv("SUPABASE_URL"),
    os.getenv("SUPABASE_SERVICE_KEY")
)

openai.api_key = os.getenv("OPENAI_API_KEY")
security = HTTPBearer(auto_error=False)
JWT_SECRET = os.getenv("JWT_SECRET_KEY")

def get_current_user(credentials: HTTPAuthorizationCredentials = Depends(security)):
    if not credentials:
        return None
    try:
        payload = jwt.decode(credentials.credentials, JWT_SECRET, algorithms=["HS256"])
        return payload.get("sub")
    except JWTError:
        return None

@app.get("/")
async def root():
    return {
        "app": "🧠 KimbleAI",
        "version": "1.0.0",
        "status": "Ready for your family!",
        "features": ["Permanent Memory", "Flexible Projects", "AI Intelligence"],
        "message": "Clean slate - create your own projects!"
    }

@app.get("/health")
async def health():
    try:
        result = supabase.table('users').select("count", count="exact").execute()
        return {
            "status": "healthy",
            "users": result.count,
            "timestamp": datetime.now().isoformat(),
            "database": "connected"
        }
    except Exception as e:
        return {"status": "error", "message": str(e)}

@app.post("/auth/login")
async def login(email: str = Form(...)):
    try:
        # Find or create user
        result = supabase.table('users').select("*").eq('email', email).execute()
        
        if not result.data:
            name = email.split('@')[0].replace('.', ' ').title()
            insert_result = supabase.table('users').insert({
                "email": email,
                "name": name,
                "role": "admin" if "zach" in email.lower() else "user"
            }).execute()
            user = insert_result.data[0]
        else:
            user = result.data[0]
        
        # Create token
        token = jwt.encode(
            {
                "sub": user['id'],
                "email": user['email'],
                "name": user['name'],
                "exp": datetime.utcnow() + timedelta(days=30)
            },
            JWT_SECRET,
            algorithm="HS256"
        )
        
        return {
            "message": f"Welcome {user['name']}!",
            "access_token": token,
            "user": user
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/projects")
async def create_project(
    name: str = Form(...),
    description: str = Form(""),
    color: str = Form("#3b82f6"),
    user_id: str = Depends(get_current_user)
):
    """Create a new project"""
    if not user_id:
        raise HTTPException(status_code=401, detail="Please log in")
    
    try:
        result = supabase.table('projects').insert({
            "user_id": user_id,
            "name": name,
            "description": description,
            "color": color
        }).execute()
        
        return {
            "message": f"Project '{name}' created!",
            "project": result.data[0]
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/projects")
async def get_projects(user_id: str = Depends(get_current_user)):
    """Get user's projects"""
    if not user_id:
        return {"projects": [], "count": 0}
    
    try:
        result = supabase.table('projects').select("*").eq('user_id', user_id).execute()
        return {"projects": result.data, "count": len(result.data)}
    except Exception as e:
        return {"projects": [], "error": str(e)}

@app.post("/upload")
async def upload_document(
    file: UploadFile = File(...),
    project_id: Optional[str] = Form(None),
    user_id: str = Depends(get_current_user)
):
    """Upload document"""
    if not user_id:
        raise HTTPException(status_code=401, detail="Please log in")
    
    try:
        content = await file.read()
        text_content = content.decode('utf-8', errors='ignore')[:8000]
        
        # Only generate embedding if OpenAI key is present
        embedding = None
        if os.getenv("OPENAI_API_KEY") and os.getenv("OPENAI_API_KEY") != "sk-your-key-here":
            try:
                embedding_response = openai.Embedding.create(
                    model="text-embedding-ada-002",
                    input=f"{file.filename}\n{text_content}"
                )
                embedding = embedding_response['data'][0]['embedding']
            except Exception as e:
                logger.warning(f"OpenAI embedding failed: {e}")
        
        # Store document
        result = supabase.table('documents').insert({
            "project_id": project_id,
            "user_id": user_id,
            "title": file.filename,
            "content": text_content,
            "source_type": "upload",
            "file_size": len(content),
            "embedding": embedding
        }).execute()
        
        return {
            "message": f"✅ Uploaded '{file.filename}'",
            "document_id": result.data[0]['id']
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/chat")
async def chat(
    query: str = Form(...),
    project_id: Optional[str] = Form(None),
    user_id: str = Depends(get_current_user)
):
    """Chat with AI"""
    try:
        if not user_id:
            return {"response": "Hi! I'm KimbleAI. Please log in to access your permanent memory."}
        
        # Check if OpenAI is configured
        if not os.getenv("OPENAI_API_KEY") or os.getenv("OPENAI_API_KEY") == "sk-your-key-here":
            return {
                "response": "KimbleAI is ready! Please add your OpenAI API key to enable AI features. Your documents are being stored and will be searchable once you configure the AI.",
                "sources": [],
                "memory_used": 0
            }
        
        # Generate search embedding
        query_embedding = openai.Embedding.create(
            model="text-embedding-ada-002",
            input=query
        )['data'][0]['embedding']
        
        # Search memory
        search_result = supabase.rpc(
            'search_memory',
            {
                'query_embedding': query_embedding,
                'match_threshold': 0.7,
                'match_count': 5,
                'user_id_filter': user_id,
                'project_id_filter': project_id
            }
        ).execute()
        
        # Build context
        context = ""
        sources = []
        
        if search_result.data:
            for doc in search_result.data[:3]:
                context += f"From '{doc['title']}': {doc['content']}\n\n"
                sources.append(doc['title'])
        
        # Generate AI response
        system_prompt = f"""You are KimbleAI, the family's permanent AI assistant.

{'Context:' + context if context else 'No relevant documents found.'}

Be helpful and reference documents when relevant."""

        response = openai.ChatCompletion.create(
            model="gpt-4",
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": query}
            ],
            max_tokens=500
        )
        
        ai_response = response.choices[0].message.content
        
        # Save conversation
        supabase.table('conversations').insert({
            "project_id": project_id,
            "user_id": user_id,
            "title": query[:100],
            "messages": {"user": query, "ai": ai_response},
            "embedding": query_embedding
        }).execute()
        
        return {
            "response": ai_response,
            "sources": sources,
            "memory_used": len(sources)
        }
        
    except Exception as e:
        return {"response": f"Error: {str(e)}", "sources": []}

@app.get("/stats")
async def stats(user_id: str = Depends(get_current_user)):
    if not user_id:
        return {"error": "Login required"}
    
    try:
        docs = supabase.table('documents').select("count", count="exact").eq('user_id', user_id).execute()
        projects = supabase.table('projects').select("count", count="exact").eq('user_id', user_id).execute()
        
        return {
            "documents": docs.count or 0,
            "projects": projects.count or 0,
            "status": "Clean slate - ready for your projects!"
        }
    except Exception as e:
        return {"error": str(e)}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)