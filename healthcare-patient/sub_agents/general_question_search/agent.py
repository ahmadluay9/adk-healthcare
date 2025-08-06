import os
from google.adk.agents import LlmAgent
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
search_agent = LlmAgent(
    model= model_name,
    name='SearchAgent',
    description="Agen untuk menjawab pertanyaan umum tentang rumah sakit seperti jam buka, lokasi, atau daftar dokter yang tersedia.",
    instruction="""
    Anda adalah asisten pencari informasi. Gunakan `vertex_ai_search_tool` untuk menjawab pertanyaan umum dari pengguna.
    """,
    tools=[vertexai_search_tool],
    generate_content_config=types.GenerateContentConfig(
        temperature=0.1
    ),
)