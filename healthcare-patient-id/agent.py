import os
from google.adk.agents import Agent
from dotenv import load_dotenv

from .sub_agents.new_patient_registration.agent import new_patient_registration_agent
from .sub_agents.general_search.agent import search_agent
from .sub_agents.medical_advice.agent import medical_advice_agent
from .sub_agents.check_upcoming_appointments.agent import check_appointment_root_agent
from .sub_agents.create_appointment.agent import create_appointment_root_agent


from .tools import model_pro, dapatkan_waktu_sekarang, dapatkan_tanggal_hari_ini, cari_jadwal_dokter, daftar_semua_dokter
from .prompts import promp_instruction_v4

# --- Konfigurasi Lingkungan ---
load_dotenv()
os.environ['GOOGLE_CLOUD_PROJECT'] = os.getenv('GOOGLE_CLOUD_PROJECT')
os.environ['GOOGLE_CLOUD_LOCATION'] = os.getenv('GOOGLE_CLOUD_LOCATION')
os.environ["GOOGLE_GENAI_USE_VERTEXAI"] = os.getenv('GOOGLE_GENAI_USE_VERTEXAI')

# --- Definisi Agen Utama (Router Agent) ---
root_agent = Agent(
    name="root_agent",
    model= model_pro,
    description="Agen utama yang berfungsi sebagai router untuk mendelegasikan tugas ke sub-agen yang sesuai.",
    instruction = promp_instruction_v4,
    sub_agents=[
        new_patient_registration_agent,
        medical_advice_agent,
        check_appointment_root_agent,
        create_appointment_root_agent,
        search_agent,
    ],
    tools=[
        dapatkan_waktu_sekarang,
        dapatkan_tanggal_hari_ini,
        cari_jadwal_dokter,
        daftar_semua_dokter
        ]
)