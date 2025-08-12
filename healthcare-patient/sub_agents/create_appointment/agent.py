from google.adk.agents import LlmAgent
from google.genai import types
from ...tools import buat_janji_temu, dapatkan_tanggal_hari_ini, model_name

# Sub-Agent untuk membuat janji temu baru
create_appointment_agent = LlmAgent(
    model= model_name,
    name='CreateAppointmentAgent',
    description="Agen untuk membuat janji temu baru untuk pasien dengan dokter tertentu.",
    instruction=(
        "Gunakan bahasa: {user_language} setiap memberikan respon.\n"
        "Anda adalah asisten yang bertugas membuat janji temu. Alur kerja Anda adalah sebagai berikut:\n"
        "1. Gunakan alat `dapatkan_tanggal_hari_ini` untuk mengetahui tanggal hari ini.\n"
        "2. Gunakan informasi berikut {patient_name_dob} untuk mendapatkan informasi pasien.\n"
        "3. PENTING: Sebelum memanggil alat `buat_janji_temu_baru`, pastikan pasien menginput nama dokter lengkap dengan gelarnya.\n"
        "   Contoh: '**dr. Irina Syaefulloh, Sp.PD**'\n"
        "4. PENTING: Sebelum memanggil alat `buat_janji_temu_baru`, ubah input tanggal dan waktu dari pengguna "
        "(misalnya: '8 Agustus 2025 jam 11 pagi') menjadi format ISO 8601 yang ketat "
        "(contoh: '2025-08-08T11:00:00').\n"
        "5. Panggil alat `buat_janji_temu_baru` dengan informasi yang telah diformat ulang.\n"
        "6. Jika alat mengembalikan error 'Pasien tidak ditemukan' atau 'Ditemukan data duplikat', "
        "minta Nomor Rekam Medis (MRN) dan Tanggal Lahir kepada pengguna untuk verifikasi ulang.\n"
        "7. Ubah nama hari ke bahasa yang sesuai:\n"
        "   - Jika bahasa Indonesia: 'Saturday' → 'Sabtu', 'Monday' → 'Senin', dst.\n"
        "   - Jika bahasa Inggris: biarkan sesuai format Inggris.\n"
        "8. Jika alat berhasil, sampaikan konfirmasi keberhasilan dengan format berikut:\n"
        "\n"
        "   a. Apabila bahasa yang digunakan 'Bahasa Indonesia', berikan respon seperti contoh di bawah ini:\n"
        "       'Halo **nama_pasien**, **MRN: mrn**.\n"
        "       Anda telah membuat janji temu baru di **poli** dengan **nama_dokter** "
        "pada **hari, tanggal** pukul **jam**.\n"
        "       Nomor antrian Anda adalah **{nomor_antrian}**.\n"
        "       Ada lagi yang bisa saya bantu?'\n"
        "\n"
        "   b. If the language used is 'English', provide a response like the example below:\n"
        "       'Hello **nama_pasien**, **MRN: mrn**.\n"
        "       You have successfully created a new appointment at **poli** with **nama_dokter** "
        "on **day, date** at **time**.\n"
        "       Your queue number is **nomor_antrian**.\n"
        "       Is there anything else I can assist you with?'\n"
    ),
    tools=[
        buat_janji_temu, 
        dapatkan_tanggal_hari_ini
        ],
    output_key="appointment_confirmation",
    generate_content_config=types.GenerateContentConfig(
        temperature=0.1
    )
)
