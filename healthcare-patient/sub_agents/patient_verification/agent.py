from google.adk.agents import LlmAgent, SequentialAgent
from google.genai import types
from ...tools import cek_pasien_terdaftar, model_name

patient_info_display_agent  = LlmAgent(
    name="PatientInfoDisplayAgent",
    model=model_name,
    description="Agen yang menampilkan informasi pasien (Nama, Tanggal Lahir, MRN) yang sudah terverifikasi.",
    instruction=(
        # "Gunakan bahasa: {user_language} setiap memberikan respon.\n"
        "Anda adalah agen untuk menampilkan informasi nama dan tanggal lahir pasien. "
        "Tugas Anda adalah sebagai berikut:\n"
        "1. Apabila bahasa yang digunakan 'Bahasa Indonesia', berikan respon seperti contoh di bawah ini:\n"
        "       Melakukan verifikasi identitas. \n\n"
        "       * Nama Depan:  \n"
        "       * Nama Belakang:  \n"
        "       * Tanggal Lahir: hari bulan tahun\n"
        "2. If the language used is 'English', provide a response like the example below:\n"
        "       Verifying identity. \n\n"
        "       * First Name: \n"
        "       * Last Name: \n"
        "       * Date of Birth: month date, year\n"
        "3. Jika nama belakang tidak ada atau kosong, jangan tampilkan baris nama belakang sama sekali."
    ),
    output_key="patient_name_dob",
    generate_content_config=types.GenerateContentConfig(
        temperature=0.2
    )
)

patient_verification_agent = LlmAgent(
    name="VerificationAgent",
    model="gemini-2.5-pro",
    description="Agen yang bertugas untuk memverifikasi identitas pengguna.",
    instruction=(
        "Tugas Anda adalah memverifkasi data pasien sudah terdaftar apa belum sesuai alur berikut: \n"
        "0. Gunakan bahasa: {user_language} setiap memberikan respon. \n"
        "1. Gunakan informasi dari {patient_name_dob} untuk memverifikasi identitas pengguna.\n"
        "   - Jika tidak ada nama belakang, isi nama belakang dan nama tengah dengan null.\n"
        "   - Saat meminta tanggal lahir, tidak perlu format khusus dari pasien.\n"
        "2. Ubah input tanggal lahir dari pasien menjadi format ketat YYYY-MM-DD (contoh: '1985-05-20').\n"
        "3. Gunakan data tersebut untuk pengecekan data pasien menggunakan alat `cek_pasien_terdaftar`.\n"
        "4. Berdasarkan hasil dari pengecekan tersebut:\n"
        "   a. Sampaikan respon dibawah ini jika pasien sudah terdaftar: \n"
        "      - Bahasa Indonesia: 'Terima kasih. **Anda sudah terdaftar**. Apakah Anda ingin mengetahui layanan kami?'\n"
        "      - English: 'Thank you. **You are already registered**. Would you like to know about our services?'\n"
        "   b. Sampaikan respon dibawah ini jika pasien belum terdaftar: \n"
        "      - Bahasa Indonesia: 'Terima kasih. **Anda belum terdaftar**. Apakah Anda ingin melanjutkan ke proses registrasi pasien baru?'\n"
        "      - English: 'Thank you. **You are not yet registered**. Would you like to proceed to new patient registration?'\n"
        "5. Jika pasien setuju, lanjutkan ke agen yang sesuai (`existing_patient_service_workflow` atau `new_patient_registration_agent`)."
    ),
    tools=[cek_pasien_terdaftar],
    generate_content_config=types.GenerateContentConfig(
        temperature=0.1
    )
)

patient_verification_workflow = SequentialAgent(
    name="PatientVerificationWorkflow",
    sub_agents=[patient_info_display_agent, patient_verification_agent],
    description="Workflow untuk memverifikasi identitas pasien dan menampilkan informasi mereka.",
)

# )
# # --- Definisi Sub-Agen Verifikasi Pasien ---
# patient_verification_agent = LlmAgent(
#     name="VerificationAgent",
#     model=model_name,
#     description="Agen yang menyapa pengguna, memverifikasi identitas mereka, dan menjelaskan layanan klinik.",
#     instruction=(
#         "Gunakan bahasa: {user_language} setiap memberikan respon. \n"
#         "Anda adalah gerbang depan layanan klinis. Tugas Anda adalah sebagai berikut:\n"
#         "1. Periksa **Nama Lengkap**, dan **Tanggal Lahir** pasien.\n"
#         "2. PENTING: Sebelum memanggil alat, Anda WAJIB mengubah input tanggal lahir dari pengguna (misalnya '20 Mei 1985', '20/05/1985', dll.) menjadi format YYYY-MM-DD yang ketat (contoh: '1985-05-20').\n"
#         "3. Panggil alat `cek_pasien_terdaftar` dengan data yang telah Anda format ulang.\n"
#         "4. Jika verifikasi gagal karena data tidak ditemukan atau duplikat, minta Nomor Rekam Medis (MRN) dan Tanggal Lahir sebagai verifikasi cadangan, lalu panggil kembali alat `cek_pasien_terdaftar` (pastikan format tanggal lahir tetap YYYY-MM-DD).\n"
#         "5. Setelah verifikasi berhasil, sampaikan pesan konfirmasi keberhasilan. Contoh: 'Verifikasi berhasil! Selamat datang, **Nama Pasien: Charles Watts**, \n **Tanggal Lahir: 9 September 1999**, \n **MRN: 123456789**.'\n"
#         "6. Setelah konfirmasi, langsung jelaskan layanan yang tersedia di RS Sehat Selalu seperti berikut:\n"
#         "- **Mendapatkan saran medis**\n"
#         "- **Mencari dokter spesialis**\n"
#         "- **Membuat janji temu**\n"
#         "- **Mengecek jadwal janji temu**\n"
#         "- **Mengecek hasil pemeriksaan terakhir**\n"
#         "- **Mencari informasi umum** (lokasi, jam operasional, atau daftar dokter)\n"
#         "7. Tutup dengan menyarankan untuk menghubungi **(021) 123-4568** untuk info lebih lanjut."
#     ),
#     tools=[cek_pasien_terdaftar],
#     output_key="verified_patient_resource",
#     generate_content_config=types.GenerateContentConfig(
#         temperature=0.5
#     )
# )

# suggestion_agent = LlmAgent(
#     name="SuggestionAgent",
#     model=model_name,
#     instruction="""
#     Gunakan selalu bahasa yang dipilih pengguna. Bahasa yang digunakan: {language}. \n
#     Anda adalah Asisten Klinis Virtual yang bertugas untuk menjelaskan layanan apa saja yang bisa dilakukan di RS Sehat Selalu.
#     Contoh Jawaban: 'Anda dapat menggunakan layanan kami untuk:\n
#     - **Mendapatkan saran medis** \n
#     - **Mencari dokter spesialis** \n
#     - **Membuat janji temu** \n
#     - **Mengecek jadwal janji temu** \n
#     - **Mengecek hasil pemeriksaan terakhir** \n
#     - **Mencari informasi umum** (seperti lokasi, jam operasional, atau daftar dokter) \n    
    
#     Untuk informasi lebih lengkap dapat hubungi **(021) 123-4568**'
#     """,
#     description="Menawarkan hasil pencarian medis dan menawarkan langkah selanjutnya.",
#     generate_content_config=types.GenerateContentConfig(
#         temperature=0.2
#     ),
# )

# patient_verification_agent = SequentialAgent(
#     name="PatientVerificationAgent",
#     sub_agents=[verification_agent, suggestion_agent],
#     description="Agen yang memverifikasi identitas pasien sebelum memberikan akses ke layanan lain.",
# )