# from google.adk.agents import LlmAgent, SequentialAgent
# from google.genai import types
# from ...tools import dapatkan_data_pasien_dari_email, dapatkan_waktu_sekarang, dapatkan_tanggal_hari_ini, model_name, model_lite, model_pro
# from ..patient_verification.prompts import instruction_greeting, instruction_greeting_v1, verification_agent_instruction_v1
# from ..general_search.agent import general_search_tool
# from ..medical_advice.agent import medical_advice_agent
# from ..check_upcoming_appointments.agent import check_appointment_agent
# from ..create_appointment.agent import create_appointment_agent
# # from ..new_patient_registration.agent import new_patient_registration_agent

# verify_patient_identity_agent = LlmAgent(
#     name="VerifyPatientIdentityAgent",
#     model=model_lite,
#     description="Agen yang bertugas menyampaikan pesan sebelum proses verifikasi identitas pasien.",
#     instruction=("""
#         Tugas Anda adalah sebagai berikut:
#         1. Sampaikan pesan berikut kepada pengguna:
#         "Saya akan melakukan verifikasi identitas anda terlebih dahulu."
#     """),
#     generate_content_config=types.GenerateContentConfig(
#         temperature=0.2
#     )
# )

# verification_status_agent = LlmAgent(
#     name="VerificationStatusAgent",
#     model=model_name,
#     description="Agen yang bertugas memverifikasi identitas pasien.",
#     instruction=("""
#         Tugas Anda adalah adalah sebagai berikut:\n
#         1. Gunakan email yang dimasukan pengguna untuk mendapatkan data pasien.\n
#         2. Panggil alat `dapatkan_data_pasien_dari_email` untuk mendapatkan data pasien.
#         3. Berdasarkan hasil dari pengecekan data pasien tersebut:\n
#             a. Sampaikan respon dibawah ini jika pasien sudah terdaftar: \n
#               - 'Terima kasih, **nama_lengkap_pasien**. **Anda sudah terverifikasi**.'\n
#             b. Sampaikan respon dibawah ini jika pasien belum terdaftar: \n
#               - '**Anda belum terdaftar**.'\n
#     """),
#     generate_content_config=types.GenerateContentConfig(
#         temperature=0.2
#     ),
#     output_key="verification_status",
#     tools=[dapatkan_data_pasien_dari_email]
# )

# patient_info_agent  = LlmAgent(
#     name="PatientInfoAgent",
#     model=model_lite,
#     description="Agen yang menampilkan informasi identitas pasien (Nama, Tanggal Lahir, MRN).",
#     instruction=("""
#         Tugas Anda adalah sebagai berikut:\n
#         1. Bila {verification_status} bernilai 'terverifikasi': 
#             - Berikan respon dengan format berikut:\n
#                 * Nama Depan:  \n
#                 * Nama Belakang:  \n
#                 * Tanggal Lahir: hari bulan tahun\n
#                 * MRN: \n
#             - Jangan tampilkan baris field yang kosong.
#         2. Jika {verification_status} bernilai 'belum terdaftar', sampaikan kepada pengguna data anda tidak ditemukan.
#     """),
#     output_key="patient_info",
#     generate_content_config=types.GenerateContentConfig(
#         temperature=0.2
#     )
# )

# greeting_agent = LlmAgent(
#     name="GreetingAgent",
#     model=model_name,
#     instruction=instruction_greeting_v1,
#     description="Menyapa pengguna sesuai waktu setempat dan menjelaskan layanan apa saja yang bisa dilakukan.",
#     tools=[dapatkan_waktu_sekarang]
# )

# patient_verification_workflow = SequentialAgent(
#     name="PatientVerificationWorkflow",
#     sub_agents=[
#         verify_patient_identity_agent, 
#         verification_status_agent, 
#         patient_info_agent, 
#         greeting_agent
#         ],
#     description="Workflow untuk memverifikasi identitas pasien.",
# )

# verification_agent = LlmAgent(
#     name="VerificationAgent",
#     model=model_pro,
#     instruction=verification_agent_instruction_v1,
#     description="Agen untuk verifikasi identitas pasien.",
#     tools=[
#         dapatkan_waktu_sekarang,
#         dapatkan_tanggal_hari_ini,
#         general_search_tool
#         ],
#     sub_agents=[
#         # new_patient_registration_agent,
#         patient_verification_workflow,
#         medical_advice_agent,
#         create_appointment_agent,
#         check_appointment_agent
#     ]
# )