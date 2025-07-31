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

def make_fhir_request(method: str, resource_path: str, payload: dict = None):
    """Membuat permintaan GET atau POST ke FHIR Datastore."""
    token = get_gcp_token()
    headers = {"Authorization": f"Bearer {token}", "Content-Type": "application/fhir+json"}
    url = f"{BASE_FHIR_URL}/{resource_path}"
    try:
        if method.upper() == 'GET':
            response = requests.get(url, headers=headers)
        elif method.upper() == 'POST':
            response = requests.post(url, headers=headers, json=payload)
        else:
            raise ValueError("Metode HTTP tidak didukung.")
        
        response.raise_for_status()
        return response.json()
    except requests.exceptions.RequestException as e:
        print(f"Error saat mengakses FHIR API: {e}")
        if e.response is not None:
            print(f"Response Body: {e.response.text}")
        return None

# Functions to Handle Patient Appointment Tools
def buat_janji_temu_baru(mrn: str, tanggal_lahir: str, nama_dokter: str, tanggal_dan_waktu: str) -> dict:
    """
    Membuat janji temu baru setelah memverifikasi identitas pasien dan ketersediaan dokter.
    """
    patient_bundle = make_fhir_request('GET', f"Patient?identifier={mrn}")
    if not patient_bundle or patient_bundle.get("total", 0) == 0:
        return {"status": "error", "error_message": f"Pasien dengan MRN '{mrn}' tidak ditemukan."}

    patient_resource = patient_bundle["entry"][0]["resource"]
    if patient_resource.get("birthDate") != tanggal_lahir:
        return {"status": "error", "error_message": "Verifikasi gagal. Tanggal lahir tidak cocok."}
    id_pasien = patient_resource["id"]

    practitioner_bundle = make_fhir_request('GET', f"Practitioner?name={nama_dokter}")
    if not practitioner_bundle or practitioner_bundle.get("total", 0) == 0:
        return {"status": "error", "error_message": f"Dokter dengan nama '{nama_dokter}' tidak ditemukan."}
    id_dokter = practitioner_bundle["entry"][0]["resource"]["id"]

    try:
        start_time = datetime.datetime.fromisoformat(tanggal_dan_waktu).astimezone(datetime.timezone.utc)
        end_time = start_time + datetime.timedelta(minutes=30)
    except ValueError:
        return {"status": "error", "error_message": "Format tanggal dan waktu tidak valid. Gunakan format YYYY-MM-DDTHH:MM:SS."}

    appointment_body = {
        "resourceType": "Appointment", "status": "booked",
        "start": start_time.isoformat(), "end": end_time.isoformat(),
        "participant": [
            {"actor": {"reference": f"Patient/{id_pasien}"}, "status": "accepted"},
            {"actor": {"reference": f"Practitioner/{id_dokter}"}, "status": "accepted"}
        ]
    }
    
    new_appointment = make_fhir_request('POST', 'Appointment', payload=appointment_body)
    if new_appointment:
        return {"status": "success", "report": f"Janji temu baru dengan {nama_dokter} pada {start_time.strftime('%d %B %Y pukul %H:%M')} berhasil dibuat."}
    else:
        return {"status": "error", "error_message": "Gagal membuat janji temu di sistem."}
    
# Functions to Handle Appointment Reminders and Questionnaires
def periksa_janji_temu_dan_kirim_kuesioner(mrn: str, tanggal_lahir: str) -> dict:
    """
    Memberikan pengingat janji temu dan tautan kuesioner setelah memverifikasi MRN dan tanggal lahir pasien.
    """
    patient_bundle = make_fhir_request('GET', f"Patient?identifier={mrn}")
    if not patient_bundle or patient_bundle.get("total", 0) == 0:
        return {"status": "error", "error_message": f"Pasien dengan MRN '{mrn}' tidak ditemukan."}
    
    patient_resource = patient_bundle["entry"][0]["resource"]
    if patient_resource.get("birthDate") != tanggal_lahir:
        return {"status": "error", "error_message": "Verifikasi gagal. Tanggal lahir tidak cocok."}
    
    id_pasien = patient_resource["id"]
    
    query = f"Appointment?actor=Patient/{id_pasien}&status=booked&_sort=date&_count=1&_include=Appointment:patient&_include=Appointment:practitioner"
    bundle = make_fhir_request('GET', query)

    if not bundle or bundle.get("total", 0) == 0:
        return {"status": "error", "error_message": f"Tidak ada janji temu yang akan datang untuk pasien dengan MRN '{mrn}'."}

    appointment, patient, practitioner = None, None, None
    for entry in bundle.get("entry", []):
        resource = entry.get("resource", {})
        if resource.get("resourceType") == "Appointment": appointment = resource
        elif resource.get("resourceType") == "Patient": patient = resource
        elif resource.get("resourceType") == "Practitioner": practitioner = resource
    
    if not appointment: return {"status": "error", "error_message": "Gagal menemukan detail janji temu."}

    patient_name = patient['name'][0]['given'][0] if patient and 'name' in patient else 'Pasien'
    doctor_name = practitioner['name'][0]['text'] if practitioner and 'name' in practitioner and 'text' in practitioner['name'][0] else 'Dokter'
    start_time = datetime.datetime.fromisoformat(appointment.get("start"))
    
    reminder_text = f"Halo {patient_name}. Anda memiliki janji temu dengan {doctor_name} pada hari {start_time.strftime('%A, %d %B %Y')} pukul {start_time.strftime('%H:%M')}."
    questionnaire_text = f"Silakan isi kuesioner pra-kunjungan di sini: https://example.com/survei?id=123"

    return {"status": "success", "report": f"{reminder_text}\n{questionnaire_text}"}

# Root Agent Configuration
root_agent = Agent(
    name="agen_asisten_klinis", model=model_name,
    description="Agen yang membantu pasien memeriksa dan membuat janji temu.",
    before_model_callback=log_query_to_model, after_model_callback=log_model_response,
    instruction=(
        "Anda adalah asisten klinis virtual yang efisien dan ramah. Tugas utama Anda adalah membantu pasien.\n"
        "1. Untuk pertanyaan umum (jam buka, lokasi, daftar dokter), gunakan `SearchAgent`.\n"
        "2. Untuk memeriksa jadwal yang sudah ada, gunakan alat `periksa_janji_temu_dan_kirim_kuesioner`.\n"
        "3. Untuk membuat janji temu baru, gunakan alat `buat_janji_temu_baru`.\n"
        "4. PENTING: Sebelum memeriksa atau membuat janji temu, Anda WAJIB meminta Nomor Rekam Medis (MRN) dan tanggal lahir pasien (format YYYY-MM-DD) untuk verifikasi.\n"
        "5. Jika pasien bertanya tentang dokter tertentu, konfirmasi dulu ketersediaannya dengan `SearchAgent`, lalu tawarkan untuk memeriksa atau membuat janji temu.\n"
        "6. Setelah berhasil menyelesaikan permintaan, selalu akhiri respons dengan bertanya, 'Ada lagi yang bisa saya bantu?'."
    ),
    tools=[
        periksa_janji_temu_dan_kirim_kuesioner,
        buat_janji_temu_baru,
        agent_tool.AgentTool(agent=search_agent)
    ],
)