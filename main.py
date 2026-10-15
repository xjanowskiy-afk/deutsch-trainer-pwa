import os
import json
import httpx
from fastapi import FastAPI, Request, HTTPException
from fastapi.responses import HTMLResponse, FileResponse, JSONResponse
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.middleware.gzip import GZipMiddleware
from pydantic import BaseModel
from typing import Dict, Any

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DATA_DIR = os.path.join(BASE_DIR, "data")
ASSETS_DIR = os.path.join(BASE_DIR, "assets")
os.makedirs(DATA_DIR, exist_ok=True)
os.makedirs(ASSETS_DIR, exist_ok=True)

SUPABASE_URL = os.environ.get("SUPABASE_URL", "https://tnjhbtrfugrdggqwsygn.supabase.co")
SUPABASE_ANON_KEY = os.environ.get("SUPABASE_ANON_KEY", "sb_publishable_8XggGtraxl1EyLX9zwFyZQ_-vcD3SAQ")

app = FastAPI(title="Deutsch Trainer API & PWA")

app.add_middleware(GZipMiddleware, minimum_size=1000)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.mount("/assets", StaticFiles(directory=ASSETS_DIR), name="assets")

class ProgressPayload(BaseModel):
    user_id: str
    email: str = ""
    sessions: list = []
    stats: Dict[str, Any] = {}

@app.get("/", response_class=HTMLResponse)
async def serve_index():
    file_path = os.path.join(BASE_DIR, "space.html")
    with open(file_path, "r", encoding="utf-8") as f:
        return HTMLResponse(content=f.read())

@app.get("/manifest.json")
async def serve_manifest():
    return FileResponse(os.path.join(BASE_DIR, "manifest.json"), media_type="application/json")

@app.get("/sw.js")
async def serve_sw():
    return FileResponse(os.path.join(BASE_DIR, "sw.js"), media_type="application/javascript")

@app.get("/icon-192.png")
async def serve_icon_192():
    return FileResponse(os.path.join(BASE_DIR, "icon-192.png"), media_type="image/png")

@app.get("/icon-512.png")
async def serve_icon_512():
    return FileResponse(os.path.join(BASE_DIR, "icon-512.png"), media_type="image/png")

@app.get("/apple-touch-icon.png")
async def serve_apple_icon():
    return FileResponse(os.path.join(BASE_DIR, "apple-touch-icon.png"), media_type="image/png")

@app.get("/api/user/{user_id}/progress")
async def get_user_progress(user_id: str):
    user_file = os.path.join(DATA_DIR, f"{user_id}.json")
    if os.path.exists(user_file):
        try:
            with open(user_file, "r", encoding="utf-8") as f:
                return json.load(f)
        except Exception:
            pass
    return {"user_id": user_id, "sessions": [], "stats": {}}

@app.post("/api/user/progress")
async def save_user_progress(payload: ProgressPayload):
    user_file = os.path.join(DATA_DIR, f"{payload.user_id}.json")
    data = {
        "user_id": payload.user_id,
        "email": payload.email,
        "sessions": payload.sessions,
        "stats": payload.stats
    }
    with open(user_file, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)
    return {"status": "ok", "saved": True, "count": len(payload.sessions)}

@app.get("/health")
@app.get("/api/keep-alive")
async def keep_alive():
    supabase_status = "ok"
    try:
        async with httpx.AsyncClient(timeout=4.0) as client:
            resp = await client.get(
                f"{SUPABASE_URL}/auth/v1/settings",
                headers={"apikey": SUPABASE_ANON_KEY}
            )
            if resp.status_code != 200:
                supabase_status = f"code_{resp.status_code}"
    except Exception as e:
        supabase_status = f"err_{str(e)[:30]}"
        
    return {
        "status": "online",
        "app": "Deutsch Trainer PWA",
        "supabase": supabase_status,
        "mode": "24/7 active"
    }

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=int(os.environ.get("PORT", 8000)))
