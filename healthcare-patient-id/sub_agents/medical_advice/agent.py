import os
from google.adk.agents import LlmAgent, SequentialAgent
from google.genai import types
from dotenv import load_dotenv
from ...tools import model_name

load_dotenv()

# Search Agent 1: Google Search for General Medical Information
medical_advice_agent = LlmAgent(
    name="MedicalAdviceAgent",
    model=model_name,
    instruction="""
    Tugas Anda adalah memberikan saran medis umum untuk keluhan non-darurat.
    
    Aturan:
    1. Jangan langsung memberi saran sebelum informasi pasien cukup.
    2. Ajukan pertanyaan lanjutan ini satu per satu untuk menggali detail, misalnya:
       - Sejak kapan keluhan ini dirasakan?
       - Seberapa sering keluhan muncul?
       - Apakah ada gejala lain yang menyertai?
       - Apakah pasien memiliki riwayat penyakit tertentu atau alergi?
       - Apakah sudah mencoba pengobatan atau penanganan sebelumnya?
    3. Gunakan gaya bertanya yang sopan dan natural sesuai bahasa pasien.
    4. Jika informasi sudah cukup, berikan saran medis umum dan non-darurat sesuai gejala yang disampaikan.
    5. Selalu akhiri respon dengan kalimat:
       "Jika keluhan berlanjut atau memburuk, segera hubungi dokter."
       dan tawarkan:
       "Apakah Anda tertarik untuk saya carikan dokter yang relevan dengan keluhan Anda di RS Sehat Selalu?"
    """,
    description="Agen yang memberikan saran medis umum untuk keluhan non-darurat, selalu bertanya detail terlebih dahulu dan menawarkan opsi mencari dokter.",
    generate_content_config=types.GenerateContentConfig(
        temperature=0.1
    ),
)

