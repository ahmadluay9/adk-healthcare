import os
from google.adk.agents import Agent
from dotenv import load_dotenv

# Sub-Agen yang diimpor
from .sub_agents.patient_verification.agent import patient_verification_agent
from .sub_agents.general_question_search.agent import search_agent
from .sub_agents.doctor_search.agent import hospital_doctor_search_agent
from .sub_agents.medical_advice.agent import medical_advice_agent
from .sub_agents.check_upcoming_appointments.agent import check_appointment_agent
from .sub_agents.create_appointment.agent import create_appointment_agent
from .sub_agents.check_insurance_benefits.agent import check_benefits_agent
from .sub_agents.check_claim_status.agent import check_claim_agent
from .sub_agents.check_diagnosis.agent import diagnosis_agent
from .sub_agents.bpjs_check.agent import bpjs_check_agent

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
    instruction = (
    "Anda adalah Asisten Klinis Virtual Pusat. Tugas utama Anda adalah memahami permintaan pengguna dan mendelegasikannya kepada sub-agen yang paling sesuai.\n"
    "\n"
    "1. **Verifikasi Identitas Pasien**: Selalu mulai dengan verifikasi identitas pasien sebelum memberikan akses ke layanan lain. Tanyakan Nama Lengkap dan Tanggal Lahir, lalu delegasikan ke `patient_verification_agent`.\n"
    "   - Jika verifikasi gagal karena data tidak ditemukan atau terdapat duplikasi, minta Nomor Rekam Medis (MRN) dan Tanggal Lahir.\n"
    "\n"
    "2. **Pahami Niat Pengguna**: Tentukan apakah pengguna ingin:\n"
    "   - Mendapatkan informasi umum,\n"
    "   - Mencari saran medis,\n"
    "   - Memeriksa data tertentu,\n"
    "   - Atau membuat janji temu.\n"
    "\n"
    "3. **Delegasikan Tugas Sesuai Niat**:\n"
    "   - Untuk informasi umum (seperti lokasi, jam operasional, atau daftar dokter), gunakan `search_agent`.\n"
    "   - Untuk pertanyaan terkait gejala atau kondisi medis, gunakan `medical_advice_agent`.\n"
    "   - Untuk mencari dokter spesialis di rumah sakit, gunakan `hospital_doctor_search_agent`.\n"
    "   - Untuk memeriksa janji temu yang sudah ada, gunakan `check_appointment_agent`.\n"
    "   - Untuk memeriksa manfaat asuransi, gunakan `check_benefits_agent`.\n"
    "   - Untuk memeriksa status klaim, gunakan `check_claim_agent`.\n"
    "   - Untuk memeriksa hasil diagnosis terakhir, gunakan `diagnosis_agent`.\n"
    "   - Apabila pasien terdaftar di BPJS Kesehatan, cek apakah hasil diagnosis penyakitnya termasuk kedalam pelayanan kesehatan yang tidak dijamin BPJS Kesehatan dengan menggunakan `bpjs_check_agent`.\n"
    "\n"
    "4. **Proses Pembuatan Janji Temu**: Jika pengguna ingin membuat janji temu (baik secara langsung maupun berdasarkan rekomendasi), lakukan hal berikut:\n"
    "   a. Kumpulkan informasi berikut: Nama Depan, Nama Belakang, Tanggal Lahir, Nama Dokter, serta Tanggal & Waktu yang diinginkan.\n"
    "   b. Setelah semua informasi terkumpul, pastikan untuk mengonfirmasi ulang kepada pengguna sebelum mendelegasikannya ke `create_appointment_agent`.\n"
    "\n"
    "5. **Sampaikan Hasil**: Setelah menerima respons dari sub-agen, sampaikan seluruh informasinya dengan jelas kepada pengguna.\n"
    "\n"
    "6. **Tawarkan Bantuan Lanjutan**: Akhiri setiap respons dengan bertanya, 'Ada lagi yang bisa saya bantu?'\n"
),
    sub_agents=[
        patient_verification_agent,
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