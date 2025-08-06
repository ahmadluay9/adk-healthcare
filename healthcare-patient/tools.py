import os
import datetime
import requests
import google.auth
import google.auth.transport.requests
from urllib.parse import quote
from typing import Optional
from dotenv import load_dotenv

# Environment Configuration
load_dotenv()
model_name = os.getenv("MODEL")
PROJECT_ID = os.getenv('GOOGLE_CLOUD_PROJECT')
FHIR_LOCATION = os.getenv('FHIR_LOCATION')
FHIR_DATASET_ID = os.getenv('FHIR_DATASET_ID')
FHIR_STORE_ID = os.getenv('FHIR_STORE_ID')
BASE_FHIR_URL = f"https://healthcare.googleapis.com/v1/projects/{PROJECT_ID}/locations/{FHIR_LOCATION}/datasets/{FHIR_DATASET_ID}/fhirStores/{FHIR_STORE_ID}/fhir"

# Function to get the FHIR resource URL
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
    
# Function to verify patient identity using MRN or name and birthdate
def verifikasi_pasien(nama_depan: Optional[str] = None, nama_belakang: Optional[str] = None, tanggal_lahir: Optional[str] = None, mrn: Optional[str] = None):
    """Memverifikasi identitas pasien menggunakan MRN (prioritas) atau kombinasi nama belakang dan tanggal lahir."""
    
    print("\n--- DEBUG: Memulai verifikasi_pasien ---")
    print(f"Input: nama_depan='{nama_depan}', nama_belakang='{nama_belakang}', tanggal_lahir='{tanggal_lahir}', mrn='{mrn}'")

    if mrn and tanggal_lahir:
        print("DEBUG: Melakukan verifikasi menggunakan MRN dan Tanggal Lahir.")
        query_path = f"Patient?identifier={mrn}&birthdate={tanggal_lahir}"
        print(f"DEBUG: URL Permintaan: {BASE_FHIR_URL}/{query_path}")
        patient_bundle = make_fhir_request('GET', query_path)
        print(f"DEBUG: Respons dari server: {patient_bundle}")
        
        if not patient_bundle or patient_bundle.get("total", 0) == 0:
            return None, {"status": "error", "error_message": f"Pasien dengan MRN '{mrn}' dan tanggal lahir '{tanggal_lahir}' tidak ditemukan."}
        return patient_bundle["entry"][0]["resource"], None

    elif nama_belakang and tanggal_lahir:
        print("DEBUG: Melakukan verifikasi menggunakan Nama Belakang dan Tanggal Lahir.")
        encoded_family_name = quote(nama_belakang)
        query_path = f"Patient?family={encoded_family_name}&birthdate={tanggal_lahir}"
        print(f"DEBUG: URL Permintaan: {BASE_FHIR_URL}/{query_path}")
        patient_bundle = make_fhir_request('GET', query_path)
        print(f"DEBUG: Respons dari server: {patient_bundle}")
        
        if not patient_bundle or patient_bundle.get("total", 0) == 0:
            return None, {"status": "error", "error_message": f"Pasien tidak ditemukan dengan data tersebut. Silakan coba verifikasi menggunakan Nomor Rekam Medis (MRN) dan tanggal lahir Anda."}
        
        if patient_bundle.get("total", 0) > 1:
            return None, {"status": "error", "error_message": "Ditemukan data duplikat. Mohon berikan Nomor Rekam Medis (MRN) dan tanggal lahir Anda untuk melanjutkan."}
        
        return patient_bundle["entry"][0]["resource"], None
    
    else:
        print("DEBUG: Gagal verifikasi karena informasi tidak lengkap.")
        return None, {"status": "error", "error_message": "Informasi tidak lengkap. Mohon berikan data verifikasi yang diperlukan."}

# Function to check upcoming appointments and send reminders    
def periksa_janji_temu_dan_kirim_kuesioner(nama_depan: Optional[str] = None, nama_belakang: Optional[str] = None, tanggal_lahir: Optional[str] = None, mrn: Optional[str] = None) -> dict:
    """Memberikan pengingat janji temu dan tautan kuesioner setelah verifikasi."""
    patient_resource, error = verifikasi_pasien(nama_depan=nama_depan, nama_belakang=nama_belakang, tanggal_lahir=tanggal_lahir, mrn=mrn)
    if error: return error
    
    id_pasien = patient_resource["id"]
    query = f"Appointment?actor=Patient/{id_pasien}&status=booked&_sort=date&_count=1&_include=Appointment:patient&_include=Appointment:practitioner"
    bundle = make_fhir_request('GET', query)

    if not bundle or bundle.get("total", 0) == 0: return {"status": "error", "error_message": f"Tidak ada janji temu yang akan datang untuk pasien ini."}

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

# Function to create a new appointment after verification
def buat_janji_temu_baru(nama_dokter: str, tanggal_dan_waktu: str, nama_depan: Optional[str] = None, nama_belakang: Optional[str] = None, tanggal_lahir: Optional[str] = None, mrn: Optional[str] = None) -> dict:
    """Membuat janji temu baru setelah verifikasi."""
    patient_resource, error = verifikasi_pasien(nama_depan=nama_depan, nama_belakang=nama_belakang, tanggal_lahir=tanggal_lahir, mrn=mrn)
    if error: return error
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

    appointment_body = { "resourceType": "Appointment", "status": "booked", "start": start_time.isoformat(), "end": end_time.isoformat(), "participant": [{"actor": {"reference": f"Patient/{id_pasien}"}, "status": "accepted"}, {"actor": {"reference": f"Practitioner/{id_dokter}"}, "status": "accepted"}] }
    new_appointment = make_fhir_request('POST', 'Appointment', payload=appointment_body)
    if new_appointment:
        return {"status": "success", "report": f"Janji temu baru dengan {nama_dokter} pada {start_time.strftime('%d %B %Y pukul %H:%M')} berhasil dibuat."}
    return {"status": "error", "error_message": "Gagal membuat janji temu di sistem."}

# Function to check insurance benefits after verification
def cek_manfaat_asuransi(nama_depan: Optional[str] = None, nama_belakang: Optional[str] = None, tanggal_lahir: Optional[str] = None, mrn: Optional[str] = None) -> dict:
    """Memeriksa manfaat asuransi pasien setelah verifikasi."""
    patient_resource, error = verifikasi_pasien(nama_depan=nama_depan, nama_belakang=nama_belakang, tanggal_lahir=tanggal_lahir, mrn=mrn)
    if error: return error
    id_pasien = patient_resource["id"]

    coverage_bundle = make_fhir_request('GET', f"Coverage?beneficiary=Patient/{id_pasien}")
    if not coverage_bundle or coverage_bundle.get("total", 0) == 0:
        return {"status": "error", "error_message": "Informasi asuransi (coverage) tidak ditemukan untuk pasien ini."}
    
    coverage = coverage_bundle["entry"][0]["resource"]
    plan_name = coverage.get("type", {}).get("coding", [{}])[0].get("display", "Tidak ada nama program")
    status = coverage.get("status", "tidak diketahui")
    return {"status": "success", "report": f"Anda terdaftar dalam program asuransi '{plan_name}' dengan status '{status}'. Untuk detail manfaat lebih lanjut, silakan hubungi penyedia asuransi Anda."}

# Function to check insurance claim status after verification
def cek_status_klaim(nama_depan: Optional[str] = None, nama_belakang: Optional[str] = None, tanggal_lahir: Optional[str] = None, mrn: Optional[str] = None) -> dict:
    """Memeriksa status klaim asuransi terakhir pasien setelah verifikasi."""
    patient_resource, error = verifikasi_pasien(nama_depan=nama_depan, nama_belakang=nama_belakang, tanggal_lahir=tanggal_lahir, mrn=mrn)
    if error: return error
    id_pasien = patient_resource["id"]

    claim_bundle = make_fhir_request('GET', f"Claim?patient=Patient/{id_pasien}&_sort=-created&_count=1")
    if not claim_bundle or claim_bundle.get("total", 0) == 0:
        return {"status": "error", "error_message": "Tidak ada riwayat klaim yang ditemukan untuk pasien ini."}

    claim = claim_bundle["entry"][0]["resource"]
    status = claim.get("status", "tidak diketahui")
    total_value = claim.get("total", {}).get("value", "N/A")
    currency = claim.get("total", {}).get("currency", "")
    created_date = datetime.datetime.fromisoformat(claim.get("created")).strftime('%d %B %Y')
    return {"status": "success", "report": f"Klaim terakhir Anda pada tanggal {created_date} sebesar {total_value} {currency} saat ini memiliki status '{status}'."}
