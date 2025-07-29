import os
import requests
import google.auth
import google.auth.transport.requests
from dotenv import load_dotenv
import datetime
import random
import string
from dotenv import load_dotenv

# --- Konfigurasi Lingkungan ---
load_dotenv()
PROJECT_ID = os.getenv('GOOGLE_CLOUD_PROJECT')
LOCATION = os.getenv('FHIR_LOCATION')  # e.g., us-central1
DATASET_ID = os.getenv('FHIR_DATASET_ID')
FHIR_STORE_ID = os.getenv('FHIR_STORE_ID')
BASE_FHIR_URL = f"https://healthcare.googleapis.com/v1/projects/{PROJECT_ID}/locations/{LOCATION}/datasets/{DATASET_ID}/fhirStores/{FHIR_STORE_ID}/fhir"

# --- Fungsi Pembantu untuk FHIR API ---
def get_gcp_token():
    """Mendapatkan token autentikasi untuk GCP."""
    credentials, _ = google.auth.default(scopes=["https://www.googleapis.com/auth/cloud-platform"])
    auth_req = google.auth.transport.requests.Request()
    credentials.refresh(auth_req)
    return credentials.token

def create_fhir_resource(resource_type: str, resource_body: dict):
    """Membuat resource baru di FHIR Datastore."""
    token = get_gcp_token()
    headers = {
        "Authorization": f"Bearer {token}",
        "Content-Type": "application/fhir+json"
    }
    try:
        print(f"Mengirim data untuk resource: {resource_type}...")
        response = requests.post(f"{BASE_FHIR_URL}/{resource_type}", headers=headers, json=resource_body)
        response.raise_for_status()
        print("Data berhasil dimasukkan!")
        return response.json()
    except requests.exceptions.RequestException as e:
        print(f"Error saat membuat resource FHIR: {e}")
        print(f"Response Body: {e.response.text if e.response else 'No response'}")
        return None

def generate_mrn(length=8):
    """Menghasilkan MRN alfanumerik acak."""
    return ''.join(random.choices(string.ascii_uppercase + string.digits, k=length))

# --- Contoh Data Pasien dalam Format FHIR ---
def create_sample_patient_data():
    """Membuat dan memasukkan data pasien, praktisi, dan janji temu."""
    
    # 1. Buat data Praktisi (Dokter)
    practitioner_body = {
        "resourceType": "Practitioner",
        "name": [{"text": "Dr. Lestari"}]
    }
    practitioner_response = create_fhir_resource("Practitioner", practitioner_body)
    if not practitioner_response:
        print("Gagal membuat data praktisi. Proses dihentikan.")
        return
    practitioner_id = practitioner_response.get("id")
    print(f"Berhasil membuat Praktisi dengan ID: {practitioner_id}")

    # 2. Buat data Pasien
    mrn_value = generate_mrn()
    patient_body = {
        "resourceType": "Patient",
        "identifier": [
            {
                "use": "usual",
                "type": {
                    "coding": [
                        {
                            "system": "http://terminology.hl7.org/CodeSystem/v2-0203",
                            "code": "MR",
                            "display": "Medical Record Number"
                        }
                    ],
                    "text": "MRN"
                },
                "system": f"urn:oid:{os.getenv('MRN_SYSTEM_OID', '1.2.3.4.5.1')}", # Ganti dengan OID sistem MRN rumah sakit Anda
                "value": mrn_value
            }
        ],
        "name": [{"given": ["Budi"], "family": "Santoso"}],
        "gender": "male",
        "birthDate": "1985-05-20"
    }
    patient_response = create_fhir_resource("Patient", patient_body)
    if not patient_response:
        print("Gagal membuat data pasien. Proses dihentikan.")
        return
    patient_id = patient_response.get("id")
    print(f"Berhasil membuat Pasien dengan ID: {patient_id}")
    print("\n--- PENTING ---")
    print(f"Gunakan ID Pasien ini untuk pengujian: {patient_id}")
    print("-----------------\n")

    # 3. Buat data Janji Temu (Appointment)
    start_time = datetime.datetime.now(datetime.timezone.utc) + datetime.timedelta(days=3)
    end_time = start_time + datetime.timedelta(minutes=30)

    appointment_body = {
        "resourceType": "Appointment",
        "status": "booked",
        "description": "Konsultasi Rutin",
        "start": start_time.isoformat(), # Format ISO 8601 dengan timezone
        "end": end_time.isoformat(),     # Format ISO 8601 dengan timezone
        "participant": [
            {
                "actor": {"reference": f"Patient/{patient_id}"},
                "status": "accepted"
            },
            {
                "actor": {"reference": f"Practitioner/{practitioner_id}"},
                "status": "accepted"
            }
        ]
    }
    appointment_response = create_fhir_resource("Appointment", appointment_body)
    if not appointment_response:
        print("Gagal membuat data janji temu.")
        return
    appointment_id = appointment_response.get("id")
    print(f"Berhasil membuat Janji Temu dengan ID: {appointment_id}")

if __name__ == "__main__":
    print("Memulai skrip untuk memasukkan data contoh ke FHIR Datastore...")
    create_sample_patient_data()
    print("\nProses selesai.")