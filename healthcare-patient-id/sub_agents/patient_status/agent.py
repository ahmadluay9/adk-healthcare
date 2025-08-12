from google.adk.agents import LlmAgent, SequentialAgent
from google.genai import types
from ...tools import model_name

# patient_status_agent = LlmAgent(
#     name="PatientStatusAgent",
#     model=model_name,
#     instruction="""   
#     Anda adalah agen yang bertugas sebagai berikut:
#     1. Gunakan bahasa: {user_language} setiap memberikan respon.
#     2. Tanyakan apakah pengguna merupakan **Pasien Baru** atau **Pasien Lama**.
#         - Tanyakan: "Apakah Anda **Pasien Baru** atau **Pasien Lama**?"
#     3. Teruskan ke agen 'patient_status_workflow' untuk mengkonfirmasi status pasien.
#     """,
#     description="Menanyakan status pasien",
#     generate_content_config=types.GenerateContentConfig(
#         temperature=0.1
#     ),
# )

# patient_status_confirmation = LlmAgent(
#     name="PatientStatusConfirmation",
#     model=model_name,
#     instruction="""   
#     Anda adalah agen yang bertugas sebagai berikut:
#     1. Gunakan bahasa: {user_language} setiap memberikan respon.
#     2. Mengkonfirmasi status pasien.
#         - Respon Anda: "**Pasien Baru** dipilih." atau "**Pasien Lama** dipilih."
#     """,
#     description="Konfirmasi status pasien dan menyimpan status tersebut ke state.",
#     generate_content_config=types.GenerateContentConfig(
#         temperature=0.1
#     ),
#     output_key="patient_status"
# )

# ask_patient_verification_agent = LlmAgent(
#     name="AskPatientVerificationAgent",
#     model=model_name,
#     instruction="""  
#     Anda adalah agen yang bertugas untuk:
#     1. Gunakan bahasa: {user_language} setiap memberikan respon.
#     2. Jika {patient_status} adalah **Pasien Baru**:
#          - Respon Anda:: "Anda adalah **Pasien Baru**.\n Apakah Anda ingin mendaftar sebagai pasien baru?"
#     3. Jika {patient_status} adalah **Pasien Lama**:
#          - Respon Anda:: "Anda adalah **Pasien Lama**.\n Apakah Anda ingin melanjutkan proses verifikasi identitas?"
#     """,
#     description="",
#     generate_content_config=types.GenerateContentConfig(
#         temperature=0.1
#     )
# )

# patient_status_workflow = SequentialAgent(
#     name="PatientStatusWorkflow",
#     description="Memandu pengguna melalui pemilihan status pasien.",
#     sub_agents=[
#         patient_status_agent,
#         patient_status_confirmation,
#         ask_patient_verification_agent
#     ]
# )

# patient_status_agent = LlmAgent(
#     name="PatientStatus",
#     model= model_name,
#     instruction="""
#     Anda adalah agen yang bertugas sebagai berikut:
#     1. Gunakan Bahasa: {user:language}.
#     2. Tanyakan apakah pengguna merupakan **Pasien Baru** atau **Pasien Lama**.
#         - Tanyakan: "Apakah Anda **Pasien Baru** atau **Pasien Lama**?"
#     3. Jika pengguna memilih **Pasien Baru**:
#         - Tanyakan: "Anda adalah **Pasien Baru**.\n Apakah Anda ingin mendaftar sebagai pasien baru?"
#     4. Jika pengguna memilih **Pasien Lama**:
#         - Tanyakan: "Anda adalah **Pasien Lama**.\n Apakah Anda ingin melanjutkan proses verifikasi identitas?"
#     """,
#     description="Menanyakan status pasien (baru atau lama), lalu menindaklanjuti dengan pertanyaan pendaftaran atau verifikasi sesuai pilihan pengguna, dengan contoh respons untuk konsistensi.",
#     generate_content_config=types.GenerateContentConfig(
#         temperature=0.1
#     ),
#     output_key="patient_status"
# )