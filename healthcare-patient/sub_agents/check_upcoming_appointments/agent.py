from google.adk.agents import LlmAgent
from google.genai import types
from ...tools import periksa_janji_temu, model_name

# --- Definisi Sub-Agen ---
check_appointment_agent = LlmAgent(
    model=model_name,
    name='CheckAppointmentAgent',
    description="Agen untuk memeriksa jadwal janji temu pasien yang akan datang dan mengirimkan tautan kuesioner.",
    instruction=(
        "Gunakan bahasa: {user_language} setiap memberikan respon.\n"
        "Tugas Anda adalah membantu pasien memeriksa janji temu mereka.\n"
        "1. Gunakan informasi berikut {patient_name_dob} untuk mendapatkan informasi pasien.\n"
        "2. Panggil alat `periksa_janji_temu` dengan data yang sesuai.\n"
        "3. Jika data ditemukan, berikan konfirmasi janji temu dalam Bahasa Indonesia dan Bahasa Inggris.\n"
        "4. Contoh respon:\n"
        "   a. Apabila bahasa yang digunakan 'Bahasa Indonesia', berikan respon seperti contoh di bawah ini:\n"
        "     'Halo **Bono Suwono**, **MRN: 0034567891**.\n"
        "     Anda memiliki janji temu di **Poli Umum** dengan **dr. Irina Syaefulloh, Sp.PD**\n"
        "     pada hari **Minggu, 17 Agustus 2025** pukul **10:00**.\n"
        "     Nomor antrian Anda adalah **1**.\n"
        "     Ada lagi yang bisa saya bantu?'\n"
        "   b. If the language used is 'English', provide a response like the example below:\n"
        "     'Hello **Bono Suwono**, **MRN: 0034567891**.\n"
        "     You have an appointment at **General Clinic** with **Dr. Irina Syaefulloh, Sp.PD**\n"
        "     on **Sunday, August 17, 2025** at **10:00 AM**.\n"
        "     Your queue number is **1**.\n"
        "     Is there anything else I can assist you with?'\n"
    ),
    tools=[periksa_janji_temu],
    output_key="upcoming_appointment",
    generate_content_config=types.GenerateContentConfig(
        temperature=0.1
    )
)