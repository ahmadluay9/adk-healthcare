from google.adk.agents import LlmAgent
from google.genai import types
from ...tools import periksa_janji_temu, model_name

# --- Definisi Sub-Agen ---
check_appointment_agent = LlmAgent(
    model=model_name,
    name='CheckAppointmentAgent',
    description="Agen untuk memeriksa jadwal janji temu pasien yang akan datang dan mengirimkan tautan kuesioner.",
    instruction=(
        "Gunakan bahasa: {user_language} setiap memberikan respon. \n"
        "Tugas Anda adalah membantu pasien memeriksa janji temu mereka.\n"
        "1. Gunakan informasi berikut {verified_patient_resource} Untuk mendapatkan informasi pasien.\n"
        "2. Panggil alat `periksa_janji_temu` dengan data yang sesuai."
        "Contoh Jawaban: 'Halo **Bono Suwono**, **MRN: 0034567891**. Anda memiliki janji temu di **Poli Umum** dengan Dokter: **dr. Irina Syaefulloh, Sp.PD** pada hari **Minggu, 17 Agustus 2025** pukul **10:00**.' \n"
        "'Nomor antrian Anda adalah **1**.' \n"
        "'Ada lagi yang bisa saya bantu?' \n"
    ),
    tools=[periksa_janji_temu],
    output_key="upcoming_appointment",
    generate_content_config=types.GenerateContentConfig(
        temperature=0.5
    )
)