import os
import uvicorn
from google.adk.cli.fast_api import get_fast_api_app
from fastapi import FastAPI, Request
from fastapi.templating import Jinja2Templates
from fastapi.staticfiles import StaticFiles
from dotenv import load_dotenv

load_dotenv()
# --- Konfigurasi ---
# Direktori root tempat main.py berada
ROOT_DIR = os.path.dirname(os.path.abspath(__file__))
# URI untuk layanan sesi (menggunakan SQLite di dalam container)
SESSION_SERVICE_URI = "sqlite:///./sessions.db"
# Asal yang diizinkan untuk CORS
ALLOWED_ORIGINS = ["*"] # Mengizinkan semua untuk kemudahan

ARTIFACT_SERVICE_URI=os.getenv("ARTIFACT_URI")

# --- Inisialisasi Aplikasi ADK ---
# get_fast_api_app akan menemukan folder healthcare-patient secara otomatis
app: FastAPI = get_fast_api_app(
    agents_dir=ROOT_DIR,
    session_service_uri=SESSION_SERVICE_URI,
    allow_origins=ALLOWED_ORIGINS,
    artifact_service_uri=ARTIFACT_SERVICE_URI,
    # Kita tidak menggunakan UI bawaan ADK
    web=False, 
)

templates = Jinja2Templates(directory="templates")
app.mount("/static", StaticFiles(directory="static"), name="static")
@app.get("/")
async def serve_index(request: Request):
    """
    This endpoint serves the index.html file at the root URL.
    """
    return templates.TemplateResponse("chatbot.html", {"request": request})

# --- Jalankan Server ---
if __name__ == "__main__":
    # Menggunakan PORT dari environment variable yang disediakan oleh Cloud Run
    port = int(os.environ.get("PORT", 8080))
    uvicorn.run(app, host="0.0.0.0", port=port)