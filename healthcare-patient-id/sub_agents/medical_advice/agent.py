import os
from google.adk.agents import LlmAgent, SequentialAgent
from google.genai import types
from dotenv import load_dotenv
from ...tools import model_name, model_pro
from ..general_search.agent import general_search_tool

load_dotenv()

# Search Agent 1: Google Search for General Medical Information
medical_advice_agent = LlmAgent(
    name="MedicalAdviceAgent",
    model=model_pro,
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
    5. Setelah memberikan saran, tentukan jenis dokter atau spesialis yang relevan dengan keluhan pasien.
    6. Selalu akhiri respon dengan kalimat:
       "Jika keluhan berlanjut atau memburuk, segera konsultasikan dengan dokter."
       dan lanjutkan dengan tawaran:
       "\n Saya bisa membantu mencarikan dokter **jenis_dokter** yang sesuai untuk Anda di RS Sehat Selalu. Apakah Anda ingin melanjutkan?"
    7. Gunakan alat `general_search_tool` untuk mencari poli klinik dan dokter yang relevan dengan keluhan pasien.
    """,
    description="Agen yang memberikan saran medis umum untuk keluhan non-darurat, selalu bertanya detail terlebih dahulu dan menawarkan opsi mencari dokter.",
    generate_content_config=types.GenerateContentConfig(
        temperature=0.1
    ),
    tools=[
        general_search_tool
    ]
)

