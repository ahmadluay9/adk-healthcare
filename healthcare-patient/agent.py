import os
from google.adk.agents import Agent
from google.adk.tools import agent_tool
from dotenv import load_dotenv

# Sub-Agen yang diimpor
from .sub_agents.general_question_search.agent import search_agent
from .sub_agents.doctor_search.agent import hospital_doctor_search_agent
from .sub_agents.medical_advice.agent import medical_advice_agent
from .sub_agents.check_upcoming_appointments.agent import check_appointment_agent
from .sub_agents.create_appointment.agent import create_appointment_agent
from .sub_agents.check_insurance_benefits.agent import check_benefits_agent
from .sub_agents.check_claim_status.agent import check_claim_agent

# --- Konfigurasi Lingkungan ---
load_dotenv()
os.environ['GOOGLE_CLOUD_PROJECT'] = os.getenv('GOOGLE_CLOUD_PROJECT')
os.environ['GOOGLE_CLOUD_LOCATION'] = os.getenv('GOOGLE_CLOUD_LOCATION')
os.environ["GOOGLE_GENAI_USE_VERTEXAI"] = os.getenv('GOOGLE_GENAI_USE_VERTEXAI')
model_name = os.getenv("MODEL")

# --- Definisi Agen Utama (Router Agent) ---
root_agent = Agent(
    name="agen_asisten_klinis",
    model= model_name,
    description="Agen utama yang berfungsi sebagai router untuk mendelegasikan tugas ke sub-agen yang sesuai.",
    instruction=(
        "Anda adalah asisten klinis virtual pusat. Tugas utama Anda adalah memahami permintaan pengguna dan mendelegasikannya ke sub-agen yang paling tepat.\n"
        "1. **Pahami Niat Pengguna**: Tentukan apakah pengguna ingin informasi umum, saran medis, memeriksa data, atau membuat janji temu.\n"
        "2. **Delegasi Tugas**:\n"
        "   - Untuk pertanyaan umum (lokasi, jam buka, daftar dokter), gunakan `search_agent`.\n"
        "   - Untuk pertanyaan tentang gejala atau kondisi medis, gunakan `medical_advice_agent`. \n"
        "   - Untuk mencari dokter spesialis di rumah sakit, gunakan `hospital_doctor_search_agent`.\n"
        "   - Untuk memeriksa janji temu yang sudah ada, gunakan `check_appointment_agent`.\n"
        "   - Untuk memeriksa manfaat asuransi, gunakan `check_benefits_agent`.\n"
        "   - Untuk memeriksa status klaim, gunakan `check_claim_agent`.\n"
        "3. **Alur Pembuatan Janji Temu**: Jika pengguna ingin membuat janji temu (baik secara langsung atau setelah mendapat rekomendasi), tugas Anda adalah:\n"
        "   a. Kumpulkan semua informasi yang diperlukan: Nama Depan, Nama Belakang, Tanggal Lahir (YYYY-MM-DD), Nama Dokter, serta Tanggal & Waktu yang diinginkan.\n"
        "   b. Setelah semua informasi lengkap, delegasikan tugas ke `create_appointment_agent`.\n"
        "4. **Sampaikan Hasil**: Setelah menerima hasil dari sub-agen, sampaikan seluruh informasinya secara lengkap kepada pengguna.\n"
        "5. **Tawarkan Bantuan Lanjutan**: Selalu akhiri respons dengan bertanya, 'Ada lagi yang bisa saya bantu?'."
    ),
    sub_agents=[
        search_agent,
        hospital_doctor_search_agent,
        medical_advice_agent,
        check_appointment_agent,
        create_appointment_agent,
        check_benefits_agent,
        check_claim_agent,
    ],
)