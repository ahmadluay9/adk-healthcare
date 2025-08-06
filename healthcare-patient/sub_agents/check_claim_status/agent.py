from google.adk.agents import LlmAgent
from google.genai import types
from ...tools import cek_status_klaim, model_name

# --- Definisi Sub-Agen ---
check_claim_agent = LlmAgent(
    model=model_name,
    name='CheckClaimAgent',
    description="Agen untuk memeriksa status klaim asuransi terakhir yang diajukan oleh pasien.",
    instruction=(
        "Tugas Anda adalah membantu pasien memeriksa status klaim asuransi mereka.\n"
        "1. Minta Nama Depan, Nama Belakang, dan Tanggal Lahir pasien untuk verifikasi.\n"
        "2. Jika verifikasi gagal, minta MRN dan Tanggal Lahir.\n"
        "3. Panggil alat `cek_status_klaim` dengan data yang sesuai."
    ),
    tools=[cek_status_klaim],
    generate_content_config=types.GenerateContentConfig(
        temperature=0.1
    )
)