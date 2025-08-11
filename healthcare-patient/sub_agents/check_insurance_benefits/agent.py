from google.adk.agents import LlmAgent
from google.genai import types
from ...tools import cek_manfaat_asuransi, model_name

# --- Definisi Sub-Agen ---
check_benefits_agent = LlmAgent(
    model=model_name,
    name='CheckBenefitsAgent',
    description="Agen untuk memeriksa detail dan manfaat (benefit) dari program asuransi pasien.",
    instruction=(
        "Gunakan bahasa: {user_language} setiap memberikan respon. \n"
        "Tugas Anda adalah membantu pasien memeriksa manfaat asuransi mereka.\n"
        "1. Minta Nama Depan, Nama Belakang, dan Tanggal Lahir pasien untuk verifikasi.\n"
        "2. Jika verifikasi gagal, minta MRN dan Tanggal Lahir.\n"
        "3. Panggil alat `cek_manfaat_asuransi` dengan data yang sesuai."
    ),
    tools=[cek_manfaat_asuransi],
    generate_content_config=types.GenerateContentConfig(
        temperature=0.1
    )
)