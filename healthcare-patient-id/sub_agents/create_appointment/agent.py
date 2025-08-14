
# import os
from google.adk.agents import LlmAgent
from google.genai import types
# from google.adk.tools import VertexAiSearchTool
# from google.adk.tools.agent_tool import AgentTool
from ..general_search.agent import general_search_tool
from ...tools import buat_janji_temu, dapatkan_tanggal_hari_ini, model_name
from ..create_appointment.prompts import appointment_instruction
# from dotenv import load_dotenv

# load_dotenv()
# # --- Alat Pencarian ---
# vertexai_search_tool = VertexAiSearchTool(
#     data_store_id=f"projects/{os.getenv('GOOGLE_CLOUD_PROJECT')}/locations/global/collections/default_collection/dataStores/{os.getenv('DATASTORE_ID')}"
# )

# # --- Definisi Sub-Agen ---
# doctor_search_agent = LlmAgent(
#     model= model_name,
#     name='DoctorSearchAgent',
#     description="Agen untuk menjawab pertanyaan tentang daftar poli atau jadwal dokter yang tersedia.",
#     instruction="""
#     Anda adalah asisten pencari informasi. 
#     Aturan:
#     1. Gunakan `vertex_ai_search_tool` untuk menjawab pertanyaan dari pengguna. \n
#     2. Apabila pengguna menanyakan tentang dokter atau poli, selalu sampaikan nama poli, nama dokter lengkap dengan jadwal praktiknya. \n
#     """,
#     tools=[vertexai_search_tool],
#     generate_content_config=types.GenerateContentConfig(
#         temperature=0.1
#     ),
# )

# doctor_search_tool = AgentTool(agent=doctor_search_agent)

create_appointment_agent = LlmAgent(
    model = model_name,
    name='CreateAppointmentAgent',
    description="Agen untuk membuat janji temu baru untuk pasien dengan dokter tertentu.",
    instruction=appointment_instruction,
    tools=[
        buat_janji_temu, 
        dapatkan_tanggal_hari_ini,
        general_search_tool
        ],
    output_key="appointment_confirmation",
    generate_content_config=types.GenerateContentConfig(
        temperature=0.1
    )
)
