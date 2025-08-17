import os
from google.adk.agents import LlmAgent
from google.adk.tools import VertexAiSearchTool
from google.adk.tools.agent_tool import AgentTool
from google.genai import types
from dotenv import load_dotenv
from ...tools import model_name, model_pro, dapatkan_tanggal_hari_ini, cari_jadwal_dokter

load_dotenv()

# --- Alat Pencarian ---
vertexai_search_tool = VertexAiSearchTool(
    data_store_id=f"projects/{os.getenv('GOOGLE_CLOUD_PROJECT')}/locations/global/collections/default_collection/dataStores/{os.getenv('DATASTORE_ID')}"
)

# --- Definisi Sub-Agen ---
general_search_agent = LlmAgent(
    model= model_pro,
    name='GeneralSearchTool',
    description="alat pencarian untuk menjawab pertanyaan umum tentang rumah sakit seperti jam buka, lokasi, atau daftar poli atau dokter yang tersedia.",
    instruction="""
    Anda adalah asisten pencari informasi. 

    Aturan:
    1. Gunakan `vertex_ai_search_tool` untuk menjawab pertanyaan dari pengguna.  
    
    Aturan tambahan:
    - Jika pengguna mencari informasi tentang poli klinik (misalnya jadwal poli, layanan yang tersedia, atau lokasi poli),
    setelah memberikan informasi yang diminta, tawarkan:
    "Apakah Anda ingin saya membantu menjadwalkan pertemuan dengan salah satu dokter di poli tersebut?"

    - Jika pengguna mencari informasi tentang dokter (misalnya jadwal dokter, spesialisasi, atau lokasi praktik),
    setelah memberikan informasi yang diminta, tawarkan:
    "Apakah Anda ingin saya membantu membuatkan janji temu dengan <nama_dokter>?"
    """,
    tools=[
        vertexai_search_tool
        ],
    generate_content_config=types.GenerateContentConfig(
        temperature=0.1
    ),
    output_key="search_results"
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
    3. Untuk mencari jadwal dokter lengkap gunakan alat `cari_jadwal_dokter`.\n
    4. Ikuti aturan berikut sebelum mencari jadwal dokter:
        a.PENTING: Pastikan nama poli ditulis lengkap sesuai format resmi berikan contoh yang benar dibawah.\n
        - Contoh salah: 'umum'\n
        - Contoh benar: 'Poli Umum'\n
        Gunakan kapitalisasi huruf awal setiap kata dan sertakan kata 'Poli'.\n
      b. PENTING: Pastikan nama dokter yang digunakan hanyalah NAMA BELAKANG saja. \n
        - Contoh: Nama Lengkap:'dr. Irina Syaefulloh, Sp.PD' menjadi Nama Belakang: 'Syaefulloh'. \n
    5. Jika pengguna menanyakan hal yang tidak berkaitan dengan layanan medis atau informasi klinis, berikan jawaban singkat yang sopan seperti:
   "Maaf, saya hanya dapat membantu terkait layanan medis dan informasi klinis di RS Sehat Selalu."
    """,
    tools=[
        general_search_tool,
        dapatkan_tanggal_hari_ini,
        cari_jadwal_dokter
        ],
    generate_content_config=types.GenerateContentConfig(
        temperature=0.1
    ),
)