import os
from google.adk.agents import Agent
from dotenv import load_dotenv

# Sub-Agen yang diimpor
from .sub_agents.greeting.agent import greeting_workflow
from .sub_agents.language_selection.agent import language_selection_workflow
# from .sub_agents.patient_status.agent import patient_status_agent
# from .sub_agents.patient_status_confirmation.agent import patient_status_workflow
from .sub_agents.ask_patient_status.agent import ask_patient_status_agent
from .sub_agents.patient_status_confirmation.agent import patient_status_confirmation_agent
from .sub_agents.new_patient_verification.agent import new_patient_verification_workflow
from .sub_agents.new_patient_registration.agent import new_patient_registration_agent
from .sub_agents.patient_verification.agent import patient_verification_workflow
from .sub_agents.existing_patient_service.agent import existing_patient_service_workflow
# from .sub_agents.ask_fullname_dob.agent import ask_fullname_dob_agent
# from .sub_agents.new_patient_verification.agent import new_patient_verification_workflow
# from .sub_agents.registration_confirmation.agent import registration_confirmation_agent
from .sub_agents.general_question_search.agent import search_agent
from .sub_agents.doctor_search.agent import hospital_doctor_search_agent
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
    "0. **Sambutan Awal**: Gunakan `greeting_workflow` untuk menyapa pengguna di awal percakapan dan menanyakan pilihan bahasa pengguna.\n"
    "   - Gunakan `language_selection_workflow` untuk mengonfirmasi pilihan bahasa pengguna serta menanyakan nama lengkap dan tanggal lahir.\n"
    "     - Jika pengguna setuju memberikan informasi, lanjutkan ke langkah 1.\n"
    "     - Jika tidak, tanyakan kebutuhan pengguna secara langsung.\n"
    "\n"
    "1. **Tentukan Status Pasien**: Tanyakan apakah pengguna merupakan pasien baru atau pasien lama menggunakan agen `ask_patient_status_agent`.\n"
    "   - Konfirmasi pilihan status pasien dengan agen `patient_status_confirmation_agent`.\n"
    "\n"
    "2. **Verifikasi Identitas Pasien**:\n"
    "   a. Untuk pasien baru, gunakan agen `new_patient_verification_workflow` untuk memverifikasi identitas.\n"
    "       - Jika verifikasi berhasil, lanjutkan ke agen `new_patient_registration_agent` untuk mendaftarkan pasien baru.\n"
    "   b. Untuk pasien lama, gunakan agen `patient_verification_workflow` untuk memverifikasi identitas.\n"
    "       - Jika verifikasi berhasil, lanjutkan ke agen `existing_patient_service_workflow` untuk memberikan layanan pasien.\n"
    "\n"
    "3. **Pahami Niat Pengguna**: Tentukan apakah pengguna ingin:\n"
    "   - Mendapatkan informasi umum,\n"
    "   - Mencari saran medis,\n"
    "   - Memeriksa data tertentu,\n"
    "   - Atau membuat janji temu.\n"
    "\n"
    "4. **Delegasikan Tugas Sesuai Niat**:\n"
    "   - Untuk informasi umum (seperti lokasi, jam operasional, atau daftar dokter), gunakan `search_agent`.\n"
    "   - Untuk pertanyaan terkait gejala atau kondisi medis, gunakan `medical_advice_agent`.\n"
    "   - Untuk mencari dokter spesialis di rumah sakit, gunakan `hospital_doctor_search_agent`.\n"
    "   - Untuk memeriksa janji temu yang sudah ada, gunakan `check_appointment_agent`.\n"
    "   - Untuk memeriksa manfaat asuransi, gunakan `check_benefits_agent`.\n"
    "   - Untuk memeriksa status klaim, gunakan `check_claim_agent`.\n"
    "   - Untuk memeriksa hasil diagnosis terakhir, gunakan `diagnosis_agent`.\n"
    "   - Apabila pasien terdaftar di BPJS Kesehatan, cek apakah hasil diagnosis penyakitnya termasuk kedalam pelayanan kesehatan yang tidak dijamin BPJS Kesehatan dengan menggunakan `bpjs_check_agent`.\n"
    "\n"
    "5. **Proses Pembuatan Janji Temu**: Jika pengguna ingin membuat janji temu (baik secara langsung maupun berdasarkan rekomendasi), lakukan hal berikut:\n"
    "   a. Kumpulkan informasi berikut: Nama Depan, Nama Belakang, Tanggal Lahir, Nama Dokter, serta Tanggal & Waktu yang diinginkan.\n"
    "   b. Setelah semua informasi terkumpul, pastikan untuk mengonfirmasi ulang kepada pengguna sebelum mendelegasikannya ke `create_appointment_agent`.\n"
    "\n"
    "6. **Sampaikan Hasil**: Setelah menerima respons dari sub-agen, sampaikan seluruh informasinya dengan jelas kepada pengguna.\n"
    "\n"
    "7. **Tawarkan Bantuan Lanjutan**: Akhiri setiap respons dengan bertanya, 'Ada lagi yang bisa saya bantu?'\n"
),
    sub_agents=[
        greeting_workflow,
        language_selection_workflow,
        # patient_status_agent,
        ask_patient_status_agent,
        patient_status_confirmation_agent,
        # patient_status_workflow,
        # ask_fullname_dob_agent,
        patient_verification_workflow,
        existing_patient_service_workflow,
        new_patient_verification_workflow,
        # new_patient_verification_workflow,
        new_patient_registration_agent,
        # registration_confirmation_agent,
        search_agent,
        hospital_doctor_search_agent,
        medical_advice_agent,
        check_appointment_agent,
        create_appointment_agent,
        check_benefits_agent,
        check_claim_agent,
        diagnosis_agent,
        bpjs_check_agent
    ],
)