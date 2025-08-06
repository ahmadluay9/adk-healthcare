import os
from google.adk.agents import LlmAgent, SequentialAgent
from google.adk.tools import google_search
from google.genai import types
from dotenv import load_dotenv
from ...tools import model_name

load_dotenv()

# Search Agent 1: Google Search for General Medical Information
medical_search_agent = LlmAgent(
    name="GeneralMedicalSearcher",
    model= model_name,
    instruction="""
    Anda adalah asisten riset medis. Telusuri informasi medis umum dan saran penanganan pertama untuk gejala yang diberikan pengguna menggunakan alat Google Search. Ringkas temuan Anda dalam 1-2 kalimat. \n
    """,
    description="Mencari informasi medis umum di internet.",
    generate_content_config=types.GenerateContentConfig(
        temperature=0.1
    ),
    output_key="general_medical_result"
)

# Search Agent 2: Medical Advice Agent
advice_agent = LlmAgent(
    name="AdviceAgent",
    model="gemini-2.5-flash-lite",
    instruction="""
    Anda adalah asisten AI yang bertugas menyarankan mengunjungi dokter terkait keluhan pasien. Kemudian anda menawarkan untuk mencarikan dokter spesialis di RS Sehat Selalu sesuai dengan keluhan pasien. \n
    Contoh jawaban: 'Untuk mendapatkan diagnosis yang akurat dan penanganan yang tepat, sangat disarankan untuk berkonsultasi dengan dokter. \n \n 
    Apakah Anda ingin saya bantu carikan dokter spesialis yang tepat di **RS Sehat Selalu** untuk mendapatkan diagnosis dan penanganan lebih lanjut?'. \n
    """,
    description="Menawarkan hasil pencarian medis dan menawarkan langkah selanjutnya.",
    generate_content_config=types.GenerateContentConfig(
        temperature=0.2
    ),
)

# Main Medical Advice Agent that orchestrates the sub-agents
medical_advice_agent = SequentialAgent(
    name="MedicalAdviceAgent",
    sub_agents=[medical_search_agent, advice_agent],
    description="Agen yang memberikan saran medis umum untuk keluhan non-darurat dan merekomendasikan dokter spesialis yang relevan."
)