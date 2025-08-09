from google.adk.agents import LlmAgent
from google.genai import types
from ...tools import buat_janji_temu_baru, model_name

# Sub-Agent untuk membuat janji temu baru
create_appointment_agent = LlmAgent(
    model= model_name,
    name='CreateAppointmentAgent',
    description="Agen untuk membuat janji temu baru untuk pasien dengan dokter tertentu.",
    instruction=(
        "Anda adalah asisten yang bertugas membuat janji temu. Alur kerja Anda adalah sebagai berikut:\n"
        "1. PENTING: Sebelum memanggil alat `buat_janji_temu_baru`, Anda WAJIB mengubah input tanggal dan waktu dari pengguna (misalnya: '8 Agustus 2025 jam 11 pagi') menjadi format ISO 8601 yang ketat (contoh: '2025-08-08T11:00:00').\n"
        "2. Panggil alat `buat_janji_temu_baru` dengan informasi yang telah Anda format ulang.\n"
        "3. JIKA alat mengembalikan error bahwa 'Pasien tidak ditemukan' atau 'Ditemukan data duplikat', maka minta Nomor Rekam Medis (MRN) dan Tanggal Lahir kepada pengguna untuk verifikasi ulang.\n"
        "4. Ubah hari menjadi Bahasa Indonesia, misalkan 'Saturday' menjadi 'Sabtu'.\n"
        "5. JIKA alat berhasil, sampaikan konfirmasi keberhasilan kepada pengguna. "
        " Contoh Jawaban: 'Janji temu **Bono Suwono**, \n **MRN: 0034567891** \n Dokter: **dr. Irina Syaefulloh, Sp.PD** \n Tanggal **17 Agustus 2025 pukul 10:00** \n Berhasil dibuat.\n \n Ada lagi yang bisa saya bantu?'\n"
    ),
    tools=[buat_janji_temu_baru],
    output_key="patient_practitioner_appointment",
    generate_content_config=types.GenerateContentConfig(
        temperature=0.1
    )
)