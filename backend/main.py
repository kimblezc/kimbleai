from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
import os

app = FastAPI(title="KimbleAI", version="6.0.0-FORCE-RESTART")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Supabase setup with URL validation
supabase = None
supabase_error = None

try:
    SUPABASE_URL = os.environ.get("SUPABASE_URL", "")
    SUPABASE_KEY = os.environ.get("SUPABASE_ANON_KEY", "")
    
    # Fix URL if missing "h"
    if SUPABASE_URL.startswith("ttps://"):
        SUPABASE_URL = "h" + SUPABASE_URL
        print(f"🔧 Fixed URL: {SUPABASE_URL}")
    
    if SUPABASE_URL and SUPABASE_KEY:
        from supabase import create_client, Client
        supabase: Client = create_client(SUPABASE_URL, SUPABASE_KEY)
        supabase_error = "Connected successfully!"
        print(f"✅ Supabase connected to: {SUPABASE_URL}")
    else:
        supabase_error = "Environment variables missing"
except Exception as e:
    supabase_error = f"Connection failed: {str(e)}"
    print(f"❌ Supabase error: {e}")

@app.get("/")
async def root():
    return {
        "app": "🧠 KimbleAI",
        "version": "6.0.0-FORCE-RESTART", 
        "status": "Ready for your family!",
        "features": ["Permanent Memory", "Flexible Projects", "AI Intelligence"],
        "message": "Backend restarted - fresh database connection!",
        "database_connected": bool(supabase),
        "database_status": supabase_error
    }

@app.get("/health")
async def health():
    return {"status": "healthy", "database": bool(supabase)}

@app.get("/db-test")
async def db_test():
    if not supabase:
        return {"error": "Database not connected", "details": supabase_error}
    
    try:
        # Test actual database connection
        result = supabase.table("users").select("*").limit(1).execute()
        return {
            "status": "success",
            "message": "Database connection working!",
            "users_table_accessible": True,
            "data_count": len(result.data) if result.data else 0
        }
    except Exception as e:
        return {"error": f"Database query failed: {str(e)}"}

@app.get("/env-test")
async def env_test():
    url = os.environ.get("SUPABASE_URL", "")
    fixed_url = "h" + url if url.startswith("ttps://") else url
    return {
        "original_url": url,
        "fixed_url": fixed_url,
        "url_valid": fixed_url.startswith("https://"),
        "message": "URL fix applied in code!"
    }

if __name__ == "__main__":
    import uvicorn
    port = int(os.environ.get("PORT", 8000))
    uvicorn.run(app, host="0.0.0.0", port=port)