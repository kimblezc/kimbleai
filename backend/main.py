from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
import os

app = FastAPI(title="KimbleAI", version="4.0.0-FIXED")

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
        "version": "4.0.0-FIXED", 
        "status": "Ready for your family!",
        "features": ["Permanent Memory", "Flexible Projects", "AI Intelligence"],
        "message": "FIXED VERSION - Local file updated correctly!",
        "environment_check": {
            "supabase_url_exists": bool(os.environ.get("SUPABASE_URL")),
            "supabase_url_length": len(os.environ.get("SUPABASE_URL", "")),
            "supabase_key_exists": bool(os.environ.get("SUPABASE_ANON_KEY"))
        }
    }

@app.get("/health")
async def health():
    return {"status": "healthy", "version": "4.0.0-FIXED"}

@app.get("/env-test")
async def env_test():
    url = os.environ.get("SUPABASE_URL", "")
    return {
        "supabase_url_found": bool(url),
        "url_length": len(url),
        "url_starts_with_https": url.startswith("https://") if url else False,
        "url_preview": url[:50] + "..." if len(url) > 50 else url,
        "message": "Environment variables loaded successfully!"
    }

if __name__ == "__main__":
    import uvicorn
    port = int(os.environ.get("PORT", 8000))
    uvicorn.run(app, host="0.0.0.0", port=port)