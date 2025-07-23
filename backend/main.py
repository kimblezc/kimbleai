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

@app.get("/")
async def root():
    return {
        "app": "🧠 KimbleAI",
        "version": "3.0.0",
        "status": "Ready for your family!",
        "message": "Clean OpenAI integration"
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

@app.post("/chat")
async def chat(request: dict):
    message = request.get("message", "")
    
    # Set API key directly (this is the pattern that works)
    openai.api_key = os.getenv("OPENAI_API_KEY")
    
    if not openai.api_key:
        return {
            "response": "OpenAI API key not configured. Please add it to Railway environment variables.",
            "message_stored": False
        }
    
    try:
        # Use the stable v0.28 pattern
        response = openai.ChatCompletion.create(
            model="gpt-3.5-turbo",
            messages=[
                {"role": "system", "content": "You are KimbleAI, a helpful family AI assistant."},
                {"role": "user", "content": message}
            ],
            max_tokens=400
        )
        
        return {
            "response": response.choices[0].message.content,
            "message_stored": True
        }
        
    except Exception as e:
        return {
            "response": f"AI processing error: {str(e)}",
            "message_stored": False
        }

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=int(os.environ.get("PORT", 8000)))