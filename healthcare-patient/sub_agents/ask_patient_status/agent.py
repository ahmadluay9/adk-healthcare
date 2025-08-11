from google.adk.agents import LlmAgent
from google.genai import types
from ...tools import model_name

ask_patient_status_agent = LlmAgent(
    name="AskPatientStatusAgent",
    model="gemini-2.5-flash-lite",
    instruction="""  
    Anda adalah agen yang bertugas menanyakan apakah pengguna ingin melanjutkan untuk memeriksa status.
    1. Gunakan bahasa: {user_language} setiap memberikan respon.
    2. Tanyakan kepada pengguna apakah ingin melanjutkan ke langkah selanjutnya:
        - Bahasa Indonesia: "Apakah Anda **Pasien Baru** atau **Pasien Lama**?"
        - English: "Are you a **New Patient** or an **Existing Patient**?"
    3. Jika pengguna setuju, lanjutkan ke agen `patient_status_confirmation_agent`.
    """,
    description="Agen yang menanyakan kepada pengguna apakah mereka pasien baru atau pasien lama, kemudian mengarahkan ke alur kerja pemeriksaan status pasien.",
    generate_content_config=types.GenerateContentConfig(
        temperature=0.1
    )
)
