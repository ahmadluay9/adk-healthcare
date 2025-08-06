import os
from google.adk.agents import LlmAgent, SequentialAgent
from google.adk.tools import VertexAiSearchTool
from google.genai import types
from dotenv import load_dotenv
from ...tools import model_name

load_dotenv()

# Search Tool Setup
vertexai_search_tool = VertexAiSearchTool(
    data_store_id=f"projects/{os.getenv('GOOGLE_CLOUD_PROJECT')}/locations/global/collections/default_collection/dataStores/{os.getenv('DATASTORE_ID')}"
)

# Hospital Doctor Searcher
doctor_search_agent = LlmAgent(
    name="HospitalDoctorSearcher",
    model= model_name,
    instruction="""
    Anda adalah asisten pencari internal rumah sakit. Berdasarkan gejala yang diberikan pengguna, gunakan alat pencarian Vertex AI untuk mencari nama dokter spesialis yang relevan di rumah sakit. \n
    Contoh jawaban: 'Di Rumah Sakit Sehat Selalu, terdapat **dr. Mega Rinindra, Sp.THT-KL** yang merupakan Spesialis Telinga, Hidung, Tenggorokan, Kepala dan Leher dan dapat membantu menangani keluhan Anda. \n '.
    """,
    description="Mencari dokter spesialis yang relevan di dalam data rumah sakit.",
    tools=[vertexai_search_tool],
    generate_content_config=types.GenerateContentConfig(
        temperature=0.1
    ),
    output_key="hospital_doctor_result"
)

# Merger Agent: Combines results and offers next step
appointment_agent = LlmAgent(
    name="AppointmentAgent",
    model=model_name,
    instruction="""
    Anda adalah asisten AI yang bertugas menawarkan untuk membuat janji temu dengan dokter spesialis jika diperlukan. \n
    Contoh jawaban: 'Apakah Anda ingin saya bantu buatkan janji temu dengan **dr. Mega Rinindra, Sp.THT-KL**?. \n '.
    """,
    description="Menawarkan untuk membuat janji temu dengan dokter spesialis.",
    generate_content_config=types.GenerateContentConfig(
        temperature=0.1
    ),
)

# Main Medical Advice Agent that orchestrates the sub-agents
hospital_doctor_search_agent = SequentialAgent(
    name="HospitalDoctorSearchAgent",
    sub_agents=[doctor_search_agent, appointment_agent],
    description="Agen yang mencari dokter spesialis yang relevan di rumah sakit berdasarkan gejala yang diberikan pengguna dan menawarkan untuk membuat janji temu."
)