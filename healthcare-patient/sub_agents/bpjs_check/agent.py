import os
from google.adk.agents import LlmAgent, SequentialAgent
from google.genai import types
from google.adk.tools import VertexAiSearchTool
from ...tools import model_name
from dotenv import load_dotenv

load_dotenv()
bpjs_search_tool = VertexAiSearchTool(
    data_store_id=f"projects/{os.getenv('GOOGLE_CLOUD_PROJECT')}/locations/global/collections/default_collection/dataStores/healthcare-bpjs"
)

# --- Definisi Sub-Agen Cek Manfaat dan Diagnosis ---
bpjs_diagnosis_check_agent = LlmAgent(
    name="BPJSDiagnosisCheckAgent",
    model=model_name,
    description="Agen untuk memeriksa diagnosis pasien termasuk Penyakit yang Tak Ditanggung BPJS Kesehatan.",
    instruction=(
        "Gunakan alat `bpjs_search_tool` untuk memeriksa hasil diagnosis pasien apakah termasuk kedalam Pelayanan Kesehatan yang Tidak Dijamin BPJS Kesehatan sesuai dengan Peraturan Presiden Nomor 82 Tahun 2018 Pasal 52 tentang Jaminan Kesehatan."
        "Jawab secara singkat apakah penyakit pasien termasuk atau tidak kedalam Pelayanan Kesehatan yang Tidak Dijamin BPJS Kesehatan"
        "Contoh Jawaban: 'Berdasarkan hasil diagnosis Anda, penyakit yang Anda alami **tidak termasuk** dalam Pelayanan Kesehatan yang Tidak Dijamin BPJS Kesehatan.'"
    ),
    tools=[
        bpjs_search_tool
    ],
    generate_content_config=types.GenerateContentConfig(
        temperature=0.1
    )
)

search_advice_agent = LlmAgent(
    name="SearchAdviceAgent",
    model="gemini-2.5-flash-lite",
    instruction="""
    Anda adalah asisten AI yang bertugas menanyakan kepada pasien apakah mereka perlu bantuan lainnya.
    """,
    description="Menanyakan apakah ada yang bisa dibantu lebih lanjut.",
    generate_content_config=types.GenerateContentConfig(
        temperature=0.2
    ),
)

bpjs_check_agent = SequentialAgent(
    name="BPJSCheckAgent",
    sub_agents=[bpjs_diagnosis_check_agent, search_advice_agent],
    description="Agen untuk memeriksa diagnosis pasien apakah termasuk dalam Pelayanan Kesehatan yang Tidak Dijamin BPJS Kesehatan dan menanyakan apakah ada yang bisa dibantu lebih lanjut.",
)

