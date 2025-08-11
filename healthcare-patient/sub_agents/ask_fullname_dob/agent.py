# from google.adk.agents import LlmAgent
# from google.genai import types
# from ...tools import model_name

# ask_fullname_dob_agent = LlmAgent(
#     name="AskFullNameAndDOB",
#     model=model_name,
#     description="Agen yang meminta pengguna untuk memasukkan nama lengkap dan tanggal lahir, lalu memanggil agen verifikasi pasien.",
#     instruction=(
#         "Gunakan bahasa: {user_language} setiap memberikan respon.\n"
#         "Tugas Anda adalah:\n"
#         "1. Meminta pengguna untuk memberikan nama lengkap dan tanggal lahir mereka.\n"
#         "   - Bahasa Indonesia: 'Mohon masukkan nama lengkap dan tanggal lahir Anda.'\n"
#         "   - English: 'Please provide your full name and date of birth.'\n"
#         "2. Ubah input tanggal lahir dari pasien menjadi format ketat YYYY-MM-DD (contoh: '1985-05-20').\n"
#         "3. Pastikan kedua data telah diberikan dengan format yang benar.\n"
#         "4. Setelah semua data lengkap, lanjutkan ke agen `patient_verification_workflow`."
#     ),
#     generate_content_config=types.GenerateContentConfig(
#         temperature=0.2
#     )
# )