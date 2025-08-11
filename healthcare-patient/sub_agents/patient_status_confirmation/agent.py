from google.adk.agents import LlmAgent, SequentialAgent
from google.genai import types
from ...tools import model_name

patient_status_confirmation_agent = LlmAgent(
    name="PatientStatusConfirmationAgent",
    model=model_name,
    instruction="""   
    Anda adalah agen yang bertugas sebagai berikut:
    1. Gunakan bahasa: {user_language} setiap memberikan respon.
    2. Mengkonfirmasi status pasien dengan respon dibawah ini
        - Bahasa Indonesia:
            - Untuk pasien baru: "Melanjutkan ke proses verifikasi identitas pasien baru."
            - Untuk pasien lama: "Melanjutkan ke proses verifikasi identitas."
        - English:
            - For new patient: "Proceeding to identity verification process for new patient."
            - For existing patient: "Proceeding to identity verification process."
    3. Bila "**Pasien Baru** dipilih." atau "**New Patient** selected." Lanjutkan ke proses verifikasi identitas menggunakan agen `new_patient_verification_agent`.
    4. Bila "**Pasien Lama** dipilih." atau "**Existing Patient** selected." Lanjutkan ke proses verifikasi identitas menggunakan agen `patient_verification_workflow `.
    """,
    description="Konfirmasi status pasien dan menyimpan status tersebut ke state.",
    generate_content_config=types.GenerateContentConfig(
        temperature=0.1
    ),
)

# patient_status_confirmation_agent = LlmAgent(
#     name="PatientStatusConfirmationAgent",
#     model=model_name,
#     instruction="""   
#     Anda adalah agen yang bertugas sebagai berikut:
#     1. Gunakan bahasa: {user_language} setiap memberikan respon.
#     1. Mengkonfirmasi status pasien dengan respon dibawah ini
#         - Bahasa Indonesia: "**Pasien Baru** dipilih." atau "**Pasien Lama** dipilih."
#         - English: "**New Patient** selected." or "**Existing Patient** selected."
#     """,
#     description="Konfirmasi status pasien dan menyimpan status tersebut ke state.",
#     generate_content_config=types.GenerateContentConfig(
#         temperature=0.1
#     ),
#     output_key="patient_status"
# )

# ask_patient_verification_agent = LlmAgent(
#     name="AskPatientVerificationAgent",
#     model="gemini-2.5-flash-lite",
#     instruction="""  
#     Anda adalah agen yang bertugas untuk:
#     1. Gunakan bahasa: {user_language} setiap memberikan respon.
#     2. Lanjutkan ke proses verifikasi identitas menggunakan agen `patient_verification_agent` dengan memberikan respon seperti dibawah ini:
#         - Bahasa Indonesia: 'Apakah Anda ingin melanjutkan ke proses verifikasi identitas?'
#         - English: 'Would you like to proceed to the identity verification process?'
#     """,
#     description="Agen yang menanyakan kepada pengguna apakah ingin melanjutkan proses pendaftaran atau verifikasi identitas, berdasarkan status pasien baru atau pasien lama.",
#     generate_content_config=types.GenerateContentConfig(
#         temperature=0.1
#     )
# )

# patient_status_workflow = SequentialAgent(
#     name="PatientStatusWorkflow",
#     description="Mengonfirmasi pemilihan status pasien dan mengarahkan ke langkah selanjutnya.",
#     sub_agents=[
#         patient_status_confirmation_agent,
#         ask_patient_verification_agent
#     ]
# )