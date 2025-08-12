# from google.adk.agents import LlmAgent, SequentialAgent
# from google.genai import types
# from ...tools import cek_pasien_terdaftar, model_name

# existing_patient_verification_agent = LlmAgent(
#     name="ExistingPatientVerificationAgent",
#     model=model_name,
#     description="Agen yang menampilkan informasi pasien (Nama, Tanggal Lahir, MRN) yang sudah terverifikasi.",
#     instruction=(
#         "Gunakan bahasa: {user_language} setiap memberikan respon.\n"
#         "Anda adalah agen untuk menampilkan informasi pasien yang sudah terverifikasi. "
#         "Tugas Anda adalah sebagai berikut:\n"
#         "1. Berikan respon seperti di bawah ini sesuai bahasa.\n"
#         "2. Jika tidak ada Nama Belakang (Last Name), jangan tampilkan baris tersebut.\n"
#         "   - Bahasa Indonesia:\n"
#         "       Informasi Pasien:\n"
#         "       * Nama Depan: Charles\n"
#         "       * Nama Belakang: Watts\n"
#         "       * Tanggal Lahir: 9 September 1999\n"
#         "       * MRN: 123456789\n"
#         "   - English:\n"
#         "       Patient Information:"
#         "       * First Name: Charles\n"
#         "       * Last Name: Watts\n"
#         "       * Date of Birth: September 9, 1999\n"
#         "       * MRN: 123456789"
#     ),
#     tools=[cek_pasien_terdaftar],
#     output_key="verified_patient_resource",
#     generate_content_config=types.GenerateContentConfig(
#         temperature=0.2
#     )
# )

# service_info_agent  = LlmAgent(
#     name="ServiceInfoAgent",
#     model="gemini-2.5-flash-lite",
#     instruction=(
#         "Anda adalah agen yang bertugas untuk:\n"
#         "1. Gunakan bahasa: {user_language} setiap memberikan respon.\n"
#         "2. Memberikan respon layanan yang ada seperti contoh di bawah ini:\n"
#         "   - Bahasa Indonesia:\n"
#         "       'Anda dapat menggunakan layanan kami untuk:\n"
#         "       - **Mendapatkan saran medis**\n"
#         "       - **Mencari dokter spesialis**\n"
#         "       - **Membuat janji temu**\n"
#         "       - **Mengecek jadwal janji temu**\n"
#         "       - **Mengecek hasil pemeriksaan terakhir**\n"
#         "       - **Mencari informasi umum** (seperti lokasi, jam operasional, atau daftar dokter)\n\n"
#         "       Untuk informasi lebih lengkap dapat hubungi **(021) 123-4568**'\n"
#         "   - English:\n"
#         "       'You can use our services for:\n"
#         "       - **Get medical advice**\n"
#         "       - **Find a specialist doctor**\n"
#         "       - **Make an appointment**\n"
#         "       - **Check appointment schedule**\n"
#         "       - **Check latest examination results**\n"
#         "       - **Find general information** (such as location, opening hours, or doctor list)\n\n"
#         "       For more information, please contact **(021) 123-4568**'"
#     ),
#     description="Agen yang memberikan daftar layanan yang tersedia kepada pengguna dalam bahasa yang diminta.",
#     generate_content_config=types.GenerateContentConfig(
#         temperature=0.1
#     )
# )

# existing_patient_service_workflow = SequentialAgent(
#     name="ExistingPatientServiceWorkflow",
#     description="Workflow yang memverifikasi data pasien lama dan menampilkan informasi layanan yang tersedia.",
#     sub_agents=[
#         existing_patient_verification_agent,
#         service_info_agent
#     ]
# )
