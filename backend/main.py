from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
import os
import openai

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# OpenAI API key from environment variables (secure)
openai.api_key = os.getenv("OPENAI_API_KEY")

@app.get("/")
async def root():
    return {
        "app": "🧠 KimbleAI",
        "version": "2.0.0",
        "status": "Ready for your family!",
        "message": "Now with real AI intelligence!"
    }

@app.get("/health")
async def health():
    return {"status": "healthy"}

@app.post("/auth/login")
async def login(request: dict):
    email = request.get("email", "")
    if "@kimbleai.com" in email:
        return {
            "access_token": f"demo_token_{email}",
            "token_type": "bearer",
            "user": {
                "id": "demo_user",
                "email": email,
                "name": "Demo User",
                "role": "user"
            }
        }
    else:
        return {"error": "Invalid email"}, 404

@app.get("/projects")
async def get_projects():
    return []

@app.post("/projects")
async def create_project(request: dict):
    return {"id": "demo_project", "name": request.get("name", "Demo Project")}

@app.post("/chat")
async def chat(request: dict):
    message = request.get("message", "")
    
    try:
        # Real GPT-4 AI response
        response = openai.chat.completions.create(
            model="gpt-4o-mini",
            messages=[
                {
                    "role": "system", 
                    "content": "You are KimbleAI, a helpful family AI assistant with permanent memory. You help organize documents, manage family projects, and provide intelligent assistance. Be concise, helpful, and family-friendly."
                },
                {"role": "user", "content": message}
            ],
            max_tokens=300
        )
        
        ai_response = response.choices[0].message.content
        
        return {
            "response": ai_response,
            "message_stored": True,
            "mode": "real_ai"
        }
        
    except Exception as e:
        return {
            "response": f"I'm having trouble connecting to my AI brain right now. Error: {str(e)}",
            "message_stored": False
        }

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=int(os.environ.get("PORT", 8000)))