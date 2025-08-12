import os
import uvicorn
from google.adk.cli.fast_api import get_fast_api_app
from dotenv import load_dotenv
from fastapi.responses import RedirectResponse
from fastapi.staticfiles import StaticFiles

load_dotenv()
# --- Konfigurasi ---
# Direktori root tempat main.py berada
ROOT_DIR = os.path.dirname(os.path.abspath(__file__))
# Direktori untuk file template seperti HTML
TEMPLATES_DIR = os.path.join(ROOT_DIR, "templates")
# URI untuk layanan sesi (menggunakan SQLite di dalam container)
SESSION_SERVICE_URI = "sqlite:///./sessions.db"
# Asal yang diizinkan untuk CORS
ALLOWED_ORIGINS = ["*"] # Mengizinkan semua untuk kemudahan

ARTIFACT_SERVICE_URI=os.getenv("ARTIFACT_URI")

# --- Inisialisasi Aplikasi ADK ---
# get_fast_api_app akan menemukan folder healthcare-patient secara otomatis
app = get_fast_api_app(
    agents_dir=ROOT_DIR,
    session_service_uri=SESSION_SERVICE_URI,
    allow_origins=ALLOWED_ORIGINS,
    artifact_service_uri=ARTIFACT_SERVICE_URI,
    # Kita tidak menggunakan UI bawaan ADK
    web=False, 
)

# --- Rute untuk mengarahkan ke index.html ---
@app.get("/", include_in_schema=False)
async def read_root():
    """
    Mengarahkan pengguna dari rute root ke halaman index.
    """
    return RedirectResponse(url="/index.html")

# --- Sajikan File Statis dari folder 'templates' ---
# Pastikan direktori 'templates' ada
os.makedirs(TEMPLATES_DIR, exist_ok=True)

# Mount direktori 'templates' untuk menyajikan file seperti index.html
# Ini memungkinkan FastAPI untuk menemukan dan mengirimkan file saat browser memintanya.
app.mount("/", StaticFiles(directory=TEMPLATES_DIR, html=True), name="templates")

# --- Jalankan Server ---
if __name__ == "__main__":
    # Menggunakan PORT dari environment variable yang disediakan oleh Cloud Run
    port = int(os.environ.get("PORT", 8080))
    uvicorn.run(app, host="0.0.0.0", port=port)