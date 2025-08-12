import os
from google.adk.agents import Agent
from dotenv import load_dotenv

# Sub-Agen yang diimpor
from .sub_agents.greeting.agent import greeting_agent
# from .sub_agents.language_selection.agent import language_selection_workflow
# from .sub_agents.patient_status.agent import patient_status_agent
# from .sub_agents.patient_status_confirmation.agent import patient_status_workflow
# from .sub_agents.ask_patient_status.agent import ask_patient_status_agent
# from .sub_agents.patient_status_confirmation.agent import patient_status_confirmation_agent
# from .sub_agents.new_patient_verification.agent import new_patient_verification_workflow
# from .sub_agents.new_patient_registration.agent import new_patient_registration_agent
# from .sub_agents.patient_verification.agent import patient_verification_workflow
# from .sub_agents.existing_patient_service.agent import existing_patient_service_workflow
# from .sub_agents.ask_fullname_dob.agent import ask_fullname_dob_agent
# from .sub_agents.new_patient_verification.agent import new_patient_verification_workflow
# from .sub_agents.registration_confirmation.agent import registration_confirmation_agent
# from .sub_agents.general_search.agent import search_agent
from .sub_agents.general_search.agent import general_search_tool
# from .sub_agents.doctor_search.agent import hospital_doctor_search_agent
# from .sub_agents.doctor_search.agent import hospital_doctor_search_tool
from .sub_agents.medical_advice.agent import medical_advice_agent
from .sub_agents.check_upcoming_appointments.agent import check_appointment_agent
from .sub_agents.create_appointment.agent import create_appointment_agent
from .sub_agents.check_insurance_benefits.agent import check_benefits_agent
from .sub_agents.check_claim_status.agent import check_claim_agent
from .sub_agents.check_diagnosis.agent import diagnosis_agent
from .sub_agents.bpjs_check.agent import bpjs_check_agent

from .tools import model_name

# --- Konfigurasi Lingkungan ---
load_dotenv()
os.environ['GOOGLE_CLOUD_PROJECT'] = os.getenv('GOOGLE_CLOUD_PROJECT')
os.environ['GOOGLE_CLOUD_LOCATION'] = os.getenv('GOOGLE_CLOUD_LOCATION')
os.environ["GOOGLE_GENAI_USE_VERTEXAI"] = os.getenv('GOOGLE_GENAI_USE_VERTEXAI')

# --- Definisi Agen Utama (Router Agent) ---
root_agent = Agent(
    name="agen_asisten_klinis",
    model= model_name,
    description="Agen utama yang berfungsi sebagai router untuk mendelegasikan tugas ke sub-agen yang sesuai.",
    instruction = (
    "Anda adalah Asisten Klinis Virtual. Tugas utama Anda adalah memahami permintaan pengguna dan mendelegasikannya kepada sub-agen yang paling sesuai.\n"
    "\n"
    "0. **Sambutan Awal**: Gunakan `greeting_agent` untuk menyapa pengguna dan menyampaikan layanan di awal percakapan.\n"
    "\n"
    "1. **Pahami Niat Pengguna**: Tentukan apakah pengguna ingin:\n"
    "   - Mendapatkan informasi umum,\n"
    "   - Mencari saran medis,\n"
    "   - Memeriksa data tertentu,\n"
    "   - Atau membuat janji temu.\n"
    "\n"
    "2. **Delegasikan Tugas Sesuai Niat**:\n"
    "   - Untuk informasi umum (seperti lokasi, jam operasional, daftar dokter, atau daftar poli yang tersedia), gunakan alat `general_search_tool`.\n"
    "   - Untuk pertanyaan terkait gejala atau kondisi medis, gunakan `medical_advice_agent`.\n"
    "   - Untuk membuat janji temu dengan dokter, gunakan `create_appointment_agent`.\n"
    "   - Untuk memeriksa janji temu yang sudah ada, gunakan `check_appointment_agent`.\n"
    "   - Untuk memeriksa manfaat asuransi, gunakan `check_benefits_agent`.\n"
    "   - Untuk memeriksa status klaim, gunakan `check_claim_agent`.\n"
    "   - Untuk memeriksa hasil diagnosis terakhir, gunakan `diagnosis_agent`.\n"
    "   - Apabila pasien terdaftar di BPJS Kesehatan, cek apakah hasil diagnosis penyakitnya termasuk kedalam pelayanan kesehatan yang tidak dijamin BPJS Kesehatan dengan menggunakan `bpjs_check_agent`.\n"
    "\n"
    "3. **Sampaikan Hasil**: Setelah menerima respons dari sub-agen, sampaikan seluruh informasinya dengan jelas kepada pengguna.\n"
    "\n"
    "4. **Tawarkan Bantuan Lanjutan**: Akhiri setiap respons dengan bertanya, 'Ada lagi yang bisa saya bantu?'\n"
),
    sub_agents=[
        greeting_agent,
        # language_selection_workflow,
        # patient_status_agent,
        # ask_patient_status_agent,
        # patient_status_confirmation_agent,
        # patient_status_workflow,
        # ask_fullname_dob_agent,
        # patient_verification_workflow,
        # existing_patient_service_workflow,
        # new_patient_verification_workflow,
        # new_patient_verification_workflow,
        # new_patient_registration_agent,
        # registration_confirmation_agent,
        # search_agent,
        # hospital_doctor_search_agent,
        medical_advice_agent,
        check_appointment_agent,
        create_appointment_agent,
        check_benefits_agent,
        check_claim_agent,
        diagnosis_agent,
        bpjs_check_agent
    ],
    tools=[general_search_tool]
)