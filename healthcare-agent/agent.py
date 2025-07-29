import os
import datetime
import requests
import google.auth
import google.auth.transport.requests

from callback_logging import log_query_to_model, log_model_response
from google.adk.agents import Agent
from google.adk.tools import VertexAiSearchTool, agent_tool
from dotenv import load_dotenv

# Environment setup
load_dotenv()
model_name = os.getenv("MODEL")
os.environ['GOOGLE_CLOUD_PROJECT'] = os.getenv('GOOGLE_CLOUD_PROJECT')
os.environ['GOOGLE_CLOUD_LOCATION'] = os.getenv('GOOGLE_CLOUD_LOCATION')
os.environ["GOOGLE_GENAI_USE_VERTEXAI"] = os.getenv('GOOGLE_GENAI_USE_VERTEXAI')

# Variables for Healthcare API
PROJECT_ID = os.getenv('GOOGLE_CLOUD_PROJECT')
FHIR_LOCATION = os.getenv('FHIR_LOCATION') 
DATASET_ID = os.getenv('FHIR_DATASET_ID')
FHIR_STORE_ID = os.getenv('FHIR_STORE_ID')
BASE_FHIR_URL = f"https://healthcare.googleapis.com/v1/projects/{PROJECT_ID}/locations/{FHIR_LOCATION}/datasets/{DATASET_ID}/fhirStores/{FHIR_STORE_ID}/fhir"

# Search Tool Setup
vertexai_search_tool = VertexAiSearchTool(
    data_store_id=f"projects/{os.getenv('GOOGLE_CLOUD_PROJECT')}/locations/global/collections/default_collection/dataStores/{os.getenv('DATASTORE_ID')}"
)

search_agent = Agent(
    model= model_name,
    name='SearchAgent',
    instruction="""
    Anda adalah asisten klinis yang siap membantu. Gunakan alat pencarian `vertex_ai_search_tool` untuk menjawab pertanyaan umum dari pasien (seperti jam buka atau lokasi). 
    """,
    tools=[vertexai_search_tool],
)

# Helper Functions for FHIR API
def get_gcp_token():
    """Mendapatkan token autentikasi untuk GCP."""
    credentials, _ = google.auth.default(scopes=["https://www.googleapis.com/auth/cloud-platform"])
    auth_req = google.auth.transport.requests.Request()
    credentials.refresh(auth_req)
    return credentials.token

def get_fhir_resource(resource_path: str):
    """Mengambil resource dari FHIR Datastore."""
    token = get_gcp_token()
    headers = {"Authorization": f"Bearer {token}"}
    try:
        response = requests.get(f"{BASE_FHIR_URL}/{resource_path}", headers=headers)
        response.raise_for_status()  # Akan raise error jika status code bukan 2xx
        return response.json()
    except requests.exceptions.RequestException as e:
        print(f"Error saat mengakses FHIR API: {e}")
        return None

# Functions for Patient Appointment Tools
def dapatkan_pengingat_janji_temu(mrn: str) -> dict:
    """
    Memberikan pengingat janji temu untuk MRN pasien yang diberikan.
    """
    # Mencari pasien berdasarkan identifier (MRN) untuk mendapatkan FHIR ID
    patient_bundle = get_fhir_resource(f"Patient?identifier={mrn}")
    if not patient_bundle or patient_bundle.get("total", 0) == 0:
        return {
            "status": "error",
            "error_message": f"Maaf, pasien dengan MRN '{mrn}' tidak ditemukan.",
        }
    
    id_pasien = patient_bundle["entry"][0]["resource"]["id"]
    
    # Lanjutkan dengan id_pasien untuk mencari janji temu
    query = f"Appointment?actor=Patient/{id_pasien}&status=booked&_sort=date&_count=1&_include=Appointment:patient&_include=Appointment:practitioner"
    bundle = get_fhir_resource(query)

    if not bundle or bundle.get("total", 0) == 0:
        return {
            "status": "error",
            "error_message": f"Maaf, tidak ada janji temu yang akan datang untuk pasien dengan MRN '{mrn}'.",
        }

    appointment, patient, practitioner = None, None, None
    for entry in bundle.get("entry", []):
        resource = entry.get("resource", {})
        resource_type = resource.get("resourceType")
        if resource_type == "Appointment":
            appointment = resource
        elif resource_type == "Patient":
            patient = resource
        elif resource_type == "Practitioner":
            practitioner = resource
    
    if not appointment:
         return {"status": "error", "error_message": "Gagal menemukan detail janji temu di dalam respons."}

    patient_name = patient['name'][0]['given'][0] if patient and 'name' in patient else 'Pasien'
    doctor_name = "Dokter"
    if practitioner and 'name' in practitioner:
        name_info = practitioner['name'][0]
        if 'text' in name_info:
            doctor_name = name_info['text']
        elif 'given' in name_info:
            doctor_name = " ".join(name_info['given'])
            if 'family' in name_info:
                doctor_name += f" {name_info['family']}"
    
    start_time_str = appointment.get("start")
    start_time = datetime.datetime.fromisoformat(start_time_str)
    
    appt_date = start_time.strftime("%A, %d %B %Y")
    appt_time = start_time.strftime("%H:%M")

    return {
        "status": "success",
        "report": f"Halo {patient_name}. Anda memiliki janji temu dengan {doctor_name} pada hari {appt_date} pukul {appt_time}.",
    }

def kirim_kuesioner_pra_kunjungan(id_pasien: str) -> dict:
    """
    Mengirimkan tautan kuesioner setelah memverifikasi keberadaan pasien di FHIR Datastore.
    """
    patient_info = get_fhir_resource(f"Patient/{id_pasien}")

    if patient_info:
        questionnaire_url = "https://example.com/survei-pra-kunjungan?id=123"
        return {
            "status": "success",
            "report": f"Tautan ke kuesioner pra-kunjungan telah dikirim ke metode kontak yang terdaftar untuk pasien ID {id_pasien}. Anda juga bisa mengaksesnya di sini: {questionnaire_url}",
        }
    else:
        return {
            "status": "error",
            "error_message": f"Tidak dapat mengirim kuesioner. Pasien dengan ID '{id_pasien}' tidak ditemukan.",
        }

# Root Agent Configuration
root_agent = Agent(
    name="agen_asisten_klinis",
    model= model_name,
    description=(
        "Agen yang membantu keterlibatan pasien dan perencanaan pra-kunjungan dengan mencari informasi."
    ),
    before_model_callback=log_query_to_model,
    after_model_callback=log_model_response,
    instruction=(
        "Anda adalah asisten klinis yang siap membantu. Gunakan tool `SearchAgent` untuk menjawab pertanyaan umum dari pasien (seperti jam buka atau lokasi). "
        "Gunakan tool `dapatkan_pengingat_janji_temu` untuk memberikan pengingat janji temu dan tool `kirim_kuesioner_pra_kunjungan` untuk mengirim kuesioner pra-kunjungan. "
        "Selalu minta Nomor Rekam Medis (MRN) pasien jika diperlukan. Bersikaplah sopan dan profesional."
    ),
    tools=[
        dapatkan_pengingat_janji_temu, 
        kirim_kuesioner_pra_kunjungan,
        agent_tool.AgentTool(agent=search_agent)
    ],
)