from google.adk.agents import LlmAgent
from google.genai import types
from ...tools import model_name, model_lite

patient_status_confirmation_agent = LlmAgent(
    name="PatientStatusConfirmationAgent",
    model=model_name,
    instruction="""   
    Anda adalah agen yang bertugas sebagai berikut:
    1. Gunakan bahasa: {user_language} setiap memberikan respon.
    2. Mengkonfirmasi status pasien dengan respon dibawah ini
        - Bahasa Indonesia:
            - Untuk pasien baru: "Pengecekan status pendaftaran."
            - Untuk pasien lama: "Melanjutkan ke proses verifikasi identitas."
        - English:
            - For new patient: "Proceeding to identity verification process for new patient."
            - For existing patient: "Proceeding to identity verification process."
    3. Bila "**Pasien Baru** dipilih." atau "**New Patient** selected." Lanjutkan ke proses pengecekan status pendaftaran menggunakan agen `new_patient_verification_agent`.
    4. Bila "**Pasien Lama** dipilih." atau "**Existing Patient** selected." Lanjutkan ke proses verifikasi identitas menggunakan agen `patient_verification_workflow `.
    """,
    description="Konfirmasi status pasien dan menyimpan status tersebut ke state.",
    generate_content_config=types.GenerateContentConfig(
        temperature=0.1
    ),
)

