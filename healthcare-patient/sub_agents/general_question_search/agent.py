import os
from google.adk.agents import LlmAgent, SequentialAgent
from google.adk.tools import VertexAiSearchTool
from google.genai import types
from dotenv import load_dotenv
from ...tools import model_name

load_dotenv()

# --- Alat Pencarian ---
vertexai_search_tool = VertexAiSearchTool(
    data_store_id=f"projects/{os.getenv('GOOGLE_CLOUD_PROJECT')}/locations/global/collections/default_collection/dataStores/{os.getenv('DATASTORE_ID')}"
)

# --- Definisi Sub-Agen ---
general_search_agent = LlmAgent(
    model= model_name,
    name='GeneralSearchAgent',
    description="Agen untuk menjawab pertanyaan umum tentang rumah sakit seperti jam buka, lokasi, atau daftar dokter yang tersedia.",
    instruction="""
    Gunakan bahasa: {user_language} setiap memberikan respon. \n
    Anda adalah asisten pencari informasi. Gunakan `vertex_ai_search_tool` untuk menjawab pertanyaan umum dari pengguna.
    """,
    tools=[vertexai_search_tool],
    generate_content_config=types.GenerateContentConfig(
        temperature=0.1
    ),
    output_key="general_search_result"
)

search_advice_agent = LlmAgent(
    name="SearchAdviceAgent",
    model="gemini-2.5-flash-lite",
    instruction="""
    Gunakan bahasa: {user_language} setiap memberikan respon. \n
    Anda adalah asisten AI yang bertugas menanyakan kepada pasien apakah mereka perlu bantuan lainnya.
    """,
    description="Menanyakan apakah ada yang bisa dibantu lebih lanjut.",
    generate_content_config=types.GenerateContentConfig(
        temperature=0.2
    ),
)

search_agent = SequentialAgent(
    name="SearchAgent",
    sub_agents=[general_search_agent, search_advice_agent],
    description="Agen yang mencari informasi umum tentang rumah sakit berdasarkan pertanyaan pengguna.",
)