from google.adk.agents import LlmAgent
from google.genai import types
from ...tools import dapatkan_waktu_sekarang, registrasi_pasien_baru, model_name, model_pro
from .prompts import registration_instruction

new_patient_registration_agent = LlmAgent(
    name="RegistrationAgent",
    model=model_pro,
    description="Agen untuk memandu pengguna melalui proses pendaftaran pasien baru.",
    instruction = registration_instruction,
    tools=[
            registrasi_pasien_baru,
            dapatkan_waktu_sekarang
           ],
    generate_content_config=types.GenerateContentConfig(
        temperature=0.1
    ),
    output_key="registration_result"
)