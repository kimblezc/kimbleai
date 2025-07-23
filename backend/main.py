from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

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
        "version": "2.0.0",
        "status": "Ready for your family!",
        "message": "Ultra-simple working version!"
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
    return {
        "response": f"Hello! You said: '{message}'. I'm KimbleAI in demo mode - working perfectly!",
        "message_stored": True,
        "mode": "ultra_simple"
    }

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=int(os.environ.get("PORT", 8000)))