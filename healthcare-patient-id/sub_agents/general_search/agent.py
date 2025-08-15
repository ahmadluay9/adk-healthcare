import os
from google.adk.agents import LlmAgent
from google.adk.tools import VertexAiSearchTool
from google.adk.tools.agent_tool import AgentTool
from google.genai import types
from dotenv import load_dotenv
from ...tools import model_name, model_pro, dapatkan_tanggal_hari_ini

load_dotenv()

# --- Alat Pencarian ---
vertexai_search_tool = VertexAiSearchTool(
    data_store_id=f"projects/{os.getenv('GOOGLE_CLOUD_PROJECT')}/locations/global/collections/default_collection/dataStores/{os.getenv('DATASTORE_ID')}"
)

# --- Definisi Sub-Agen ---
general_search_agent = LlmAgent(
    model= model_pro,
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
    tools=[
        vertexai_search_tool
        ],
    generate_content_config=types.GenerateContentConfig(
        temperature=0.1
    ),
)

general_search_tool = AgentTool(agent=general_search_agent)

search_agent = LlmAgent(
    model = model_pro,
    name='SearchAgent',
    description="Agen untuk menjawab pertanyaan umum.",
    instruction="""
    Anda adalah asisten pencari informasi. 

    Aturan:
    1. Gunakan alat `dapatkan_tanggal_hari_ini` untuk mengetahui tanggal hari ini.
    2. Gunakan `general_search_tool` untuk menjawab pertanyaan dari pengguna.
    3. Asumsikan tanggal praktik dokter selama 30 hari kedapan dokter selalu praktik, kecuali diluar hari praktiknya.
    4. Apabila pasien menanyakan tentang dokter atau poli, selalu sampaikan informasi nama poli, nama dokter lengkap dengan tanggal dan waktu.
    5. Jika pengguna menanyakan hal yang tidak berkaitan dengan layanan medis atau informasi klinis, berikan jawaban singkat yang sopan seperti:
   "Maaf, saya hanya dapat membantu terkait layanan medis dan informasi klinis di RS Sehat Selalu."
    """,
    tools=[
        general_search_tool,
        dapatkan_tanggal_hari_ini
        ],
    generate_content_config=types.GenerateContentConfig(
        temperature=0.1
    ),
)