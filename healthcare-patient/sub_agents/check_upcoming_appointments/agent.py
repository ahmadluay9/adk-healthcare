from google.adk.agents import LlmAgent
from google.genai import types
from ...tools import periksa_janji_temu_dan_kirim_kuesioner, model_name

# --- Definisi Sub-Agen ---
check_appointment_agent = LlmAgent(
    model=model_name,
    name='CheckAppointmentAgent',
    description="Agen untuk memeriksa jadwal janji temu pasien yang akan datang dan mengirimkan tautan kuesioner.",
    instruction=(
        "Tugas Anda adalah membantu pasien memeriksa janji temu mereka.\n"
        "1. Minta Nama Depan, Nama Belakang, dan Tanggal Lahir pasien untuk verifikasi.\n"
        "2. Jika verifikasi gagal, minta MRN dan Tanggal Lahir.\n"
        "3. Panggil alat `periksa_janji_temu_dan_kirim_kuesioner` dengan data yang sesuai."
    ),
    tools=[periksa_janji_temu_dan_kirim_kuesioner],
    generate_content_config=types.GenerateContentConfig(
        temperature=0.1
    )
)