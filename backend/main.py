# REPLACE your entire main.py with this enhanced version:
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

# Supabase setup with error handling
SUPABASE_URL = os.environ.get("SUPABASE_URL")
SUPABASE_KEY = os.environ.get("SUPABASE_ANON_KEY")
supabase = None

try:
    if SUPABASE_URL and SUPABASE_KEY:
        from supabase import create_client, Client
        supabase: Client = create_client(SUPABASE_URL, SUPABASE_KEY)
        print(f"✅ Supabase connected: {SUPABASE_URL[:50]}...")
    else:
        print("⚠️ Supabase credentials not found")
except Exception as e:
    print(f"❌ Supabase connection failed: {e}")
    supabase = None

@app.get("/")
async def root():
    return {
        "app": "🧠 KimbleAI",
        "version": "1.0.0", 
        "status": "Ready for your family!",
        "features": ["Permanent Memory", "Flexible Projects", "AI Intelligence"],
        "message": "Backend with Supabase ready!",
        "database": "connected" if supabase else "not connected"
    }

@app.get("/health")
async def health():
    return {"status": "healthy", "database": bool(supabase)}

@app.get("/db-test")
async def db_test():
    if not supabase:
        return {"error": "Database not connected"}
    
    try:
        # Test Supabase connection
        result = supabase.table("users").select("*").limit(1).execute()
        return {
            "status": "success",
            "message": "Database connection working",
            "users_count": len(result.data) if result.data else 0
        }
    except Exception as e:
        return {"error": f"Database test failed: {str(e)}"}

if __name__ == "__main__":
    import uvicorn
    port = int(os.environ.get("PORT", 8000))
    uvicorn.run(app, host="0.0.0.0", port=port)