import os
from google.adk.agents import LlmAgent
from google.adk.tools import VertexAiSearchTool
from google.adk.tools.agent_tool import AgentTool
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
    name='GeneralSearchAgent',
    description="Agen untuk menjawab pertanyaan umum tentang rumah sakit seperti jam buka, lokasi, atau daftar poli atau dokter yang tersedia.",
    instruction="""
    Anda adalah asisten pencari informasi. 

    Aturan:
    1. Gunakan `vertex_ai_search_tool` untuk menjawab pertanyaan dari pengguna.
    2. Apabila pertanyaan mengenai poli atau dokter, selalu jawab lengkap:
    - Nama poli
    - Nama dokter yang terkait (jika ada)
    - Jadwal praktiknya

    Aturan tambahan:
    - Jika pengguna mencari informasi tentang poli klinik (misalnya jadwal poli, layanan yang tersedia, atau lokasi poli),
    setelah memberikan informasi yang diminta, tawarkan:
    "Apakah Anda ingin saya membantu menjadwalkan pertemuan dengan salah satu dokter di poli tersebut?"

    - Jika pengguna mencari informasi tentang dokter (misalnya jadwal dokter, spesialisasi, atau lokasi praktik),
    setelah memberikan informasi yang diminta, tawarkan:
    "Apakah Anda ingin saya membantu membuatkan janji temu dengan dokter atau poli tersebut, 
    atau Anda sudah memiliki janji dengan beliau dan ingin saya bantu memeriksanya?"
    """,
    tools=[vertexai_search_tool],
    generate_content_config=types.GenerateContentConfig(
        temperature=0.1
    ),
)

general_search_tool = AgentTool(agent=search_agent)

