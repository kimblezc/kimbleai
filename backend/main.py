# DELETE EVERYTHING in main.py and paste this EXACT code:
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
import os

app = FastAPI(title="KimbleAI", version="1.0.0")

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
        "version": "1.0.0", 
        "status": "Ready for your family!",
        "features": ["Permanent Memory", "Flexible Projects", "AI Intelligence"],
        "message": "Simplified backend working!"
    }

@app.get("/health")
async def health():
    return {"status": "healthy"}

if __name__ == "__main__":
    import uvicorn
    port = int(os.environ.get("PORT", 8000))
    uvicorn.run(app, host="0.0.0.0", port=port)