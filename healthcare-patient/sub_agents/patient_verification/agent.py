from google.adk.agents import LlmAgent, SequentialAgent
from google.genai import types
from ...tools import verifikasi_pasien, model_name

# --- Definisi Sub-Agen Verifikasi Pasien ---
verification_agent = LlmAgent(
    name="VerificationAgent",
    model=model_name,
    description="Agen yang menyapa pengguna dan memverifikasi identitas mereka sebelum memberikan akses ke layanan lain.",
    instruction=(
        "Anda adalah gerbang depan layanan klinis. Tugas Anda adalah sebagai berikut:\n"
        "1. Sapa pengguna dengan ramah.\n"
        "2. Minta Nama Depan, Nama Belakang, dan Tanggal Lahir pasien.\n"
        "3. PENTING: Sebelum memanggil alat, Anda WAJIB mengubah input tanggal lahir dari pengguna (misalnya '20 Mei 1985', '20/05/1985', dll.) menjadi format YYYY-MM-DD yang ketat (contoh: '1985-05-20').\n"
        "4. Panggil alat `verifikasi_pasien` dengan data yang telah Anda format ulang.\n"
        "5. Jika verifikasi gagal karena data tidak ditemukan atau duplikat, minta Nomor Rekam Medis (MRN) dan Tanggal Lahir sebagai verifikasi cadangan, lalu panggil kembali alat `verifikasi_pasien` (pastikan format tanggal lahir tetap YYYY-MM-DD).\n"
        "6. Setelah verifikasi berhasil, sampaikan pesan konfirmasi keberhasilan. Contoh: 'Verifikasi berhasil! Selamat datang, **Charles Watts** \n **MRN: 123456789**'\n"
    ),
    tools=[verifikasi_pasien],
    # Simpan hasil verifikasi ke dalam session state untuk digunakan oleh agen selanjutnya
    output_key="verified_patient_resource",
    generate_content_config=types.GenerateContentConfig(
        temperature=0.1
    )
)

suggestion_agent = LlmAgent(
    name="SuggestionAgent",
    model="gemini-2.5-flash-lite",
    instruction="""
    Anda adalah Asisten Klinis Virtual yang bertugas untuk menjelaskan layanan apa saja yang bisa dilakukan di RS Sehat Selalu.
    Contoh Jawaban: 'Anda dapat menggunakan layanan kami untuk:\n
    - Mengecek jadwal janji temu \n
    - Mengecek manfaat asuransi \n
    - Mengecek status klaim asuransi \n
    - Mencari informasi umum (seperti lokasi, jam operasional, atau daftar dokter) \n
    - Mendapatkan saran medis \n
    - Mencari dokter spesialis \n
    - Membuat janji temu baru \n
    Ada lagi yang bisa saya bantu?'
    """,
    description="Menawarkan hasil pencarian medis dan menawarkan langkah selanjutnya.",
    generate_content_config=types.GenerateContentConfig(
        temperature=0.2
    ),
)

patient_verification_agent = SequentialAgent(
    name="PatientVerificationAgent",
    sub_agents=[verification_agent, suggestion_agent],
    description="Agen yang memverifikasi identitas pasien sebelum memberikan akses ke layanan lain.",
)