import os
import datetime
import requests
import google.auth
import google.auth.transport.requests
from urllib.parse import quote
from typing import Optional
from dotenv import load_dotenv
import re

# Environment Configuration
load_dotenv()
model_name = os.getenv("MODEL")
model_lite = os.getenv("MODEL_LITE")
model_pro = os.getenv("MODEL_PRO")
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

# Function to select language based on user input
def pilih_bahasa(bahasa: str) -> dict:
    """Mengonfirmasi pilihan bahasa pengguna dan menyimpannya ke dalam state."""
    if bahasa.lower() in ["english", "en"]:
        pilihan = "English"
        konfirmasi = "Great, we will continue in English."
    else:
        pilihan = "Bahasa Indonesia"
        konfirmasi = "Baik, kita akan melanjutkan dalam Bahasa Indonesia."
    
    return {
        "status": "success",
        "language_choice": pilihan,
        "report": konfirmasi
    }

def dapatkan_tanggal_hari_ini() -> dict:
    """Mengembalikan tanggal hari ini dalam format Bahasa Indonesia."""
    nama_hari = {
        0: "Senin",
        1: "Selasa",
        2: "Rabu",
        3: "Kamis",
        4: "Jumat",
        5: "Sabtu",
        6: "Minggu"
    }
    
    nama_bulan = {
        1: "Januari",
        2: "Februari",
        3: "Maret",
        4: "April",
        5: "Mei",
        6: "Juni",
        7: "Juli",
        8: "Agustus",
        9: "September",
        10: "Oktober",
        11: "November",
        12: "Desember"
    }

    # Tentukan zona waktu Waktu Indonesia Barat (WIB), yaitu UTC+7
    zona_waktu_wib = datetime.timezone(datetime.timedelta(hours=7))

    # Dapatkan tanggal dan waktu saat ini secara spesifik untuk zona waktu WIB
    sekarang = datetime.datetime.now(zona_waktu_wib)
    
    # Dapatkan nama hari dan bulan dari pemetaan
    # .weekday() mengembalikan angka (Senin=0, Selasa=1, ...)
    hari_ini = nama_hari[sekarang.weekday()]
    bulan_ini = nama_bulan[sekarang.month]
    
    # Susun string tanggal yang lengkap
    tanggal_format = f"{hari_ini}, {sekarang.day} {bulan_ini} {sekarang.year}"
    
    laporan = f"Hari ini adalah hari {tanggal_format}."
    
    return {"status": "success", "report": laporan}

def dapatkan_waktu_sekarang() -> dict:
    """
    Mengembalikan waktu saat ini dalam format Bahasa Indonesia
    dengan zona waktu yang benar (WIB/UTC+7).
    """
    # Tentukan zona waktu Waktu Indonesia Barat (WIB), yaitu UTC+7
    zona_waktu_wib = datetime.timezone(datetime.timedelta(hours=7))

    # Dapatkan tanggal dan waktu saat ini secara spesifik untuk zona waktu WIB
    sekarang = datetime.datetime.now(zona_waktu_wib)
    
    # Format waktu ke dalam string "Jam:Menit:Detik"
    # %H untuk format 24 jam, %I untuk format 12 jam dengan %p (AM/PM)
    waktu_format = sekarang.strftime("%H:%M:%S")
    
    laporan = f"Sekarang pukul {waktu_format} WIB."
    
    return {"status": "success", "report": laporan}

# Function to make FHIR API requests
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
def verifikasi_pasien(nama_depan: Optional[str] = None, nama_belakang: Optional[str] = None, tanggal_lahir: Optional[str] = None, mrn: Optional[str] = None, email: Optional[str] = None, nomor_telepon: Optional[str] = None):
    """Memverifikasi identitas pasien menggunakan email, nomor telepon, MRN, atau kombinasi nama dan tanggal lahir."""
    
    print("\n--- DEBUG: Memulai verifikasi_pasien ---")
    print(f"Input: nama_depan='{nama_depan}', nama_belakang='{nama_belakang}', tanggal_lahir='{tanggal_lahir}', mrn='{mrn}', email='{email}', nomor_telepon='{nomor_telepon}'")
    
    if email:
        print(f"DEBUG: Melakukan verifikasi menggunakan Email: {email}")
        query_path = f"Patient?email={quote(email)}"
        patient_bundle = make_fhir_request('GET', query_path)
        if not patient_bundle or patient_bundle.get("total", 0) == 0:
            return None, {"status": "error", "error_message": f"Pasien dengan email '{email}' tidak ditemukan."}
        if patient_bundle.get("total", 0) > 1:
            return None, {"status": "error", "error_message": "Ditemukan lebih dari satu pasien dengan email tersebut. Mohon gunakan metode verifikasi lain."}
        return patient_bundle["entry"][0]["resource"], None
    
    if nomor_telepon:
        print(f"DEBUG: Melakukan verifikasi menggunakan Nomor Telepon: {nomor_telepon}")
        query_path = f"Patient?telecom={quote(nomor_telepon)}"
        patient_bundle = make_fhir_request('GET', query_path)
        if not patient_bundle or patient_bundle.get("total", 0) == 0:
            return None, {"status": "error", "error_message": f"Pasien dengan nomor telepon '{nomor_telepon}' tidak ditemukan."}
        if patient_bundle.get("total", 0) > 1:
            return None, {"status": "error", "error_message": "Ditemukan lebih dari satu pasien dengan nomor telepon tersebut. Mohon gunakan metode verifikasi lain."}
        return patient_bundle["entry"][0]["resource"], None

    if mrn and tanggal_lahir:
        print("DEBUG: Melakukan verifikasi menggunakan MRN dan Tanggal Lahir.")
        query_path = f"Patient?identifier={mrn}&birthdate={tanggal_lahir}"
        print(f"DEBUG: URL Permintaan: {BASE_FHIR_URL}/{query_path}")
        patient_bundle = make_fhir_request('GET', query_path)
        print(f"DEBUG: Respons dari server: {patient_bundle}")
        
        if not patient_bundle or patient_bundle.get("total", 0) == 0:
            return None, {"status": "error", "error_message": f"Pasien dengan MRN '{mrn}' dan tanggal lahir '{tanggal_lahir}' tidak ditemukan."}
        return patient_bundle["entry"][0]["resource"], None

    elif nama_depan and tanggal_lahir:
        print("DEBUG: Melakukan verifikasi menggunakan Nama Depan dan Tanggal Lahir.")
        encoded_given_name = quote(nama_depan)
        query_path = f"Patient?given={encoded_given_name}&birthdate={tanggal_lahir}"
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

def dapatkan_data_pasien(email: Optional[str] = None, nomor_telepon: Optional[str] = None) -> dict:
    """Mendapatkan detail data pasien (nama, tanggal lahir, MRN) berdasarkan alamat email atau nomor Telepon."""
    
    print(f"\n--- DEBUG: Memulai dapatkan_data_pasien ---")
    print(f"Input: email='{email}', nomor_telepon='{nomor_telepon}'")

    if not email and not nomor_telepon:
        return {"status": "error", "error_message": "Mohon berikan email atau nomor Telepon untuk mencari data pasien."}

    # Memanggil verifikasi_pasien dengan data yang diberikan
    patient_resource, error = verifikasi_pasien(email=email, nomor_telepon=nomor_telepon)
    
    if error:
        print(f"DEBUG: Verifikasi gagal: {error}")
        return error

    if patient_resource:
        print("DEBUG: Pasien ditemukan.")
        # Ekstrak data yang diperlukan
        nama_depan = patient_resource.get("name", [{}])[0].get("given", ["(tidak ada)"])[0]
        nama_belakang = patient_resource.get("name", [{}])[0].get("family", "(tidak ada)")
        tanggal_lahir = patient_resource.get("birthDate", "(tidak ada)")
        
        mrn_value = "(tidak ada)"
        if "identifier" in patient_resource:
            for identifier in patient_resource["identifier"]:
                if identifier.get("type", {}).get("text") == "MRN":
                    mrn_value = identifier.get("value", "(tidak ada)")
                    break
        
        input_type = f"email {email}" if email else f"nomor Telepon {nomor_telepon}"
        report = (
            f"Data untuk pasien dengan {input_type} berhasil ditemukan:\n"
            f"- Nama Depan: {nama_depan}\n"
            f"- Nama Belakang: {nama_belakang}\n"
            f"- Tanggal Lahir: {tanggal_lahir}\n"
            f"- MRN: {mrn_value}"
        )
        print(f"DEBUG: Laporan akhir: {report}")
        return {
            "status": "success",
            "nama_depan": nama_depan,
            "nama_belakang": nama_belakang,
            "tanggal_lahir": tanggal_lahir,
            "mrn": mrn_value,
            "report": report
        }
    
    return {"status": "error", "error_message": "Gagal memproses permintaan."}
   
def cek_pasien_terdaftar(nama_depan: str, nama_belakang: str, tanggal_lahir: str) -> dict:
    """Memeriksa apakah pasien dengan nama dan tanggal lahir yang diberikan sudah terdaftar di sistem."""
    
    print("\n--- DEBUG: Memulai cek_pasien_terdaftar ---")
    print(f"Input: nama_depan='{nama_depan}', nama_belakang='{nama_belakang}', tanggal_lahir='{tanggal_lahir}'")

    patient_resource, error = verifikasi_pasien(nama_depan=nama_depan, nama_belakang=nama_belakang, tanggal_lahir=tanggal_lahir)
    
    if error:
        print(f"DEBUG: Verifikasi gagal, pasien dianggap belum terdaftar. Error: {error}")
        return {"status": "success", "is_registered": False, "report": "Pasien dengan data tersebut belum terdaftar. Anda bisa melanjutkan proses pendaftaran."}

    if patient_resource:
        print("DEBUG: Pasien ditemukan.")
        existing_mrn = "tidak ditemukan"
        if "identifier" in patient_resource:
            for identifier in patient_resource["identifier"]:
                if identifier.get("type", {}).get("text") == "MRN":
                    existing_mrn = identifier.get("value", "tidak ditemukan")
                    break
        report = f"Pasien dengan nama dan tanggal lahir tersebut sudah terdaftar dengan Nomor Rekam Medis (MRN): {existing_mrn}"
        print(f"DEBUG: Laporan akhir: {report}")
        return {"status": "success", "is_registered": True, "report": report}
    
    return {"status": "success", "is_registered": False, "report": "Pasien dengan data tersebut belum terdaftar. Anda bisa melanjutkan proses pendaftaran."}

# Function to get the next MRN
def get_next_mrn():
    """Mencari MRN terakhir dan menaikkannya satu."""
    # Mencari pasien terakhir berdasarkan ID (asumsi ID terakhir adalah yang terbaru)
    # Catatan: Di produksi, gunakan sistem sekuens yang lebih andal.
    patient_bundle = make_fhir_request('GET', 'Patient?_sort=-_lastUpdated&_count=1')
    if not patient_bundle or patient_bundle.get("total", 0) == 0:
        return "MRN000001" # MRN pertama jika database kosong

    last_patient = patient_bundle["entry"][0]["resource"]
    if "identifier" in last_patient:
        for identifier in last_patient["identifier"]:
            if identifier.get("type", {}).get("text") == "MRN":
                last_mrn = identifier.get("value", "MRN000000")
                try:
                    numeric_part = int(last_mrn.replace("MRN", ""))
                    new_numeric_part = numeric_part + 1
                    return f"MRN{new_numeric_part:06d}"
                except ValueError:
                    continue # Lanjutkan jika format MRN tidak terduga
    return "MRN000001" # Fallback

def registrasi_pasien_baru(
    nama_depan: str,
    nomor_telepon: str,
    alamat: str,
    jenis_identitas: str,
    nomor_identitas: str,
    kewarganegaraan: str,
    agama: str,
    status_perkawinan: str,
    tempat_lahir: str,
    pendidikan: str,
    tanggal_lahir: str,
    jenis_kelamin: str,
    pekerjaan: str,
    golongan_darah: str,
    nama_tengah: Optional[str] = None,
    nama_belakang: Optional[str] = None,
    email: Optional[str] = None,
) -> dict:
    """Mendaftarkan pasien baru dengan validasi nomor Telepon dan email."""
    
    print("\n--- DEBUG: Memulai registrasi_pasien_baru ---")
    print(f"Input Diterima: nama_depan='{nama_depan}', nomor_telepon='{nomor_telepon}', email='{email}'")

    # 1. Validasi Nomor Telepon
    existing_patient_by_phone = make_fhir_request('GET', f"Patient?telecom={quote(nomor_telepon)}")
    if existing_patient_by_phone and existing_patient_by_phone.get("total", 0) > 0:
        return {"status": "error", "error_message": f"Nomor Telepon '{nomor_telepon}' sudah terdaftar di sistem."}

    # 2. Validasi Email (jika ada)
    if email:
        existing_patient_by_email = make_fhir_request('GET', f"Patient?email={quote(email)}")
        if existing_patient_by_email and existing_patient_by_email.get("total", 0) > 0:
            return {"status": "error", "error_message": f"Email '{email}' sudah terdaftar di sistem."}

    new_mrn = get_next_mrn()
    print(f"DEBUG: MRN baru yang dibuat: {new_mrn}")

    name_list = [{"given": [nama_depan], "family": nama_belakang, "use": "official"}]
    if nama_tengah:
        name_list[0]["given"].insert(1, nama_tengah) # Menyisipkan nama tengah di antara nama depan dan belakang

    telecom_list = [{"system": "phone", "value": nomor_telepon, "use": "mobile"}]
    if email:
        telecom_list.append({"system": "email", "value": email})

    patient_body = {
        "resourceType": "Patient",
        "identifier": [
            {"use": "usual", "type": {"text": "MRN"}, "value": new_mrn},
            {"use": "official", "type": {"text": jenis_identitas}, "value": nomor_identitas}
        ],
        "name": name_list,
        "gender": jenis_kelamin.lower(), # Pastikan formatnya lowercase (male, female, other, unknown)
        "birthDate": tanggal_lahir,
        "telecom": telecom_list,
        "address": [{"text": alamat, "use": "home", "extension": [{"url": "http://hl7.org/fhir/StructureDefinition/patient-address-birthPlace", "valueString": tempat_lahir}]}],
        "extension": [
            {"url": "http://example.info/extension/agama", "valueString": agama},
            {"url": "http://example.info/extension/pendidikan", "valueString": pendidikan},
            {"url": "http://example.info/extension/pekerjaan", "valueString": pekerjaan},
            {"url": "http://example.info/extension/golongan_darah", "valueString": golongan_darah},
            {"url": "http://hl7.org/fhir/StructureDefinition/patient-nationality", "valueCode": kewarganegaraan},
        ],
        "maritalStatus": {"text": status_perkawinan},
    }
    
    print(f"DEBUG: Body JSON yang akan dikirim ke FHIR API:\n{patient_body}")

    response = make_fhir_request('POST', 'Patient', payload=patient_body)
    print(f"DEBUG: Respons dari server FHIR: {response}")
    
    if response and response.get("id"):
        full_name = nama_depan
        if nama_tengah:
            full_name += f" {nama_tengah}"
        if nama_belakang:
            full_name += f" {nama_belakang}"
        return {"status": "success", "report": f"Pendaftaran berhasil! Pasien '{full_name}' telah terdaftar dengan Nomor Rekam Medis (MRN): {new_mrn}"}
    else:
        return {"status": "error", "error_message": "Gagal mendaftarkan pasien baru ke dalam sistem."}

# Function to search for doctor's schedule
def cari_jadwal_dokter(nama_dokter: Optional[str] = None, nama_poli: Optional[str] = None) -> dict:
    """Mencari jadwal praktik dokter dan menampilkan tanggal praktik dalam 30 hari ke depan dalam Bahasa Indonesia."""
    print(f"\n--- DEBUG: Memulai cari_jadwal_dokter ---")
    print(f"Input: nama_dokter='{nama_dokter}', nama_poli='{nama_poli}'")

    if not nama_dokter and not nama_poli:
        return {"status": "error", "error_message": "Mohon berikan nama dokter atau nama poli untuk memulai pencarian."}

    # Pemetaan untuk nama hari dan bulan dalam Bahasa Indonesia
    nama_hari_map = {
        "mon": "Senin", "tue": "Selasa", "wed": "Rabu", "thu": "Kamis",
        "fri": "Jumat", "sat": "Sabtu", "sun": "Minggu"
    }
    nama_bulan_map = {
        1: "Januari", 2: "Februari", 3: "Maret", 4: "April", 5: "Mei", 6: "Juni",
        7: "Juli", 8: "Agustus", 9: "September", 10: "Oktober", 11: "November", 12: "Desember"
    }

    # Dapatkan tanggal hari ini (dengan timezone yang benar)
    zona_waktu_wib = datetime.timezone(datetime.timedelta(hours=7))
    hari_ini = datetime.datetime.now(zona_waktu_wib).date()

    # --- LOGIKA PENCARIAN BERDASARKAN NAMA DOKTER ---
    if nama_dokter:
        practitioner_bundle = make_fhir_request('GET', f"Practitioner?name:contains={quote(nama_dokter)}")
        if not practitioner_bundle or practitioner_bundle.get("total", 0) == 0:
            return {"status": "error", "error_message": f"Dokter dengan nama '{nama_dokter}' tidak ditemukan."}
        
        practitioner = practitioner_bundle["entry"][0]["resource"]
        id_dokter = practitioner["id"]
        
        doctor_name_parts = practitioner.get("name", [{}])[0]
        prefix = " ".join(doctor_name_parts.get("prefix", []))
        given = " ".join(doctor_name_parts.get("given", []))
        family = doctor_name_parts.get("family", "")
        suffix = ", ".join(doctor_name_parts.get("suffix", []))
        doctor_full_name = " ".join(part for part in [prefix, given, family, suffix] if part).strip()

        role_query = f"PractitionerRole?practitioner=Practitioner/{id_dokter}"
        if nama_poli:
            role_query += f"&specialty:text={quote(nama_poli)}"
        
        role_bundle = make_fhir_request('GET', role_query)
        if not role_bundle or role_bundle.get("total", 0) == 0:
            return {"status": "error", "error_message": f"Tidak ditemukan jadwal praktik untuk {doctor_full_name}."}

        report_parts = [f"Berikut adalah jadwal praktik untuk **{doctor_full_name}**:"]
        for role_entry in role_bundle.get("entry", []):
            role = role_entry.get("resource", {})
            poli = role.get("specialty", [{}])[0].get("text", "Poli Umum")
            jadwal_poli = f"\n**{poli}**:"
            jadwal_ditemukan = False
            if "availableTime" in role:
                for slot in role.get("availableTime", []):
                    days_of_week_abbr = slot.get("daysOfWeek", [])
                    days = [nama_hari_map.get(day.lower(), day) for day in days_of_week_abbr]
                    start, end = slot.get("availableStartTime", ""), slot.get("availableEndTime", "")
                    if days and start and end:
                        jadwal_poli += f"\n- **Jadwal Rutin**: {', '.join(days)} ({start} - {end})"
                        jadwal_ditemukan = True
                    tanggal_praktik_list = []
                    if days_of_week_abbr:
                        for i in range(30):
                            tanggal_cek = hari_ini + datetime.timedelta(days=i)
                            if tanggal_cek.strftime('%a').lower() in days_of_week_abbr:
                                tanggal_format = f"{nama_hari_map[tanggal_cek.strftime('%a').lower()]}, {tanggal_cek.day} {nama_bulan_map[tanggal_cek.month]} {tanggal_cek.year}"
                                tanggal_praktik_list.append(tanggal_format)
                    if tanggal_praktik_list:
                        jadwal_poli += f"\n- **Tanggal Praktik Terdekat**:"
                        for tanggal in tanggal_praktik_list:
                            jadwal_poli += f"\n    - {tanggal}"
            if jadwal_ditemukan:
                report_parts.append(jadwal_poli)
        return {"status": "success", "report": "".join(report_parts)}

    # --- LOGIKA PENCARIAN BERDASARKAN NAMA POLI ---
    elif nama_poli:
        query = f"PractitionerRole?specialty:text={quote(nama_poli)}&_include=PractitionerRole:practitioner"
        bundle = make_fhir_request('GET', query)
        if not bundle or bundle.get("total", 0) == 0:
            return {"status": "error", "error_message": f"Tidak ditemukan dokter atau jadwal di {nama_poli}."}

        practitioners = {f'Practitioner/{p["resource"]["id"]}': p["resource"] for p in bundle.get("entry", []) if p.get("resource", {}).get("resourceType") == "Practitioner"}
        roles = [r["resource"] for r in bundle.get("entry", []) if r.get("resource", {}).get("resourceType") == "PractitionerRole"]
        
        schedules_by_doctor = {}
        for role in roles:
            practitioner_ref = role.get("practitioner", {}).get("reference")
            if practitioner_ref not in schedules_by_doctor:
                schedules_by_doctor[practitioner_ref] = []
            schedules_by_doctor[practitioner_ref].append(role)

        if not schedules_by_doctor:
            return {"status": "error", "error_message": f"Tidak ditemukan jadwal dokter di {nama_poli}."}

        report_parts = [f"Berikut adalah jadwal dokter yang tersedia di **{nama_poli}**:"]
        for practitioner_ref, doctor_roles in schedules_by_doctor.items():
            practitioner = practitioners.get(practitioner_ref)
            if not practitioner: continue

            name_parts = practitioner.get("name", [{}])[0]
            prefix = " ".join(name_parts.get("prefix", []))
            given = " ".join(name_parts.get("given", []))
            family = name_parts.get("family", "")
            suffix = ", ".join(name_parts.get("suffix", []))
            doctor_full_name = " ".join(part for part in [prefix, given, family, suffix] if part).strip()
            report_parts.append(f"\n\n**{doctor_full_name}**:")

            for role in doctor_roles:
                jadwal_poli = ""
                jadwal_ditemukan = False
                if "availableTime" in role:
                    for slot in role.get("availableTime", []):
                        days_of_week_abbr = slot.get("daysOfWeek", [])
                        days = [nama_hari_map.get(day.lower(), day) for day in days_of_week_abbr]
                        start, end = slot.get("availableStartTime", ""), slot.get("availableEndTime", "")
                        if days and start and end:
                            jadwal_poli += f"\n- **Jadwal Rutin**: {', '.join(days)} ({start} - {end})"
                            jadwal_ditemukan = True
                        tanggal_praktik_list = []
                        if days_of_week_abbr:
                            for i in range(30):
                                tanggal_cek = hari_ini + datetime.timedelta(days=i)
                                if tanggal_cek.strftime('%a').lower() in days_of_week_abbr:
                                    tanggal_format = f"{nama_hari_map[tanggal_cek.strftime('%a').lower()]}, {tanggal_cek.day} {nama_bulan_map[tanggal_cek.month]} {tanggal_cek.year}"
                                    tanggal_praktik_list.append(tanggal_format)
                        if tanggal_praktik_list:
                            jadwal_poli += f"\n- **Tanggal Praktik Terdekat**:"
                            for tanggal in tanggal_praktik_list:
                                jadwal_poli += f"\n    - {tanggal}"
                if jadwal_ditemukan:
                    report_parts.append(jadwal_poli)
        
        return {"status": "success", "report": "".join(report_parts)}
    
    return {"status": "error", "error_message": "Terjadi kesalahan yang tidak terduga."}

def daftar_semua_dokter() -> dict:
    """Mengambil dan menampilkan daftar semua dokter beserta poli tempat mereka praktik."""
    
    print("\n--- DEBUG: Memulai daftar_semua_dokter ---")
    
    # 1. Minta data PractitionerRole dan sertakan data Practitioner terkait
    query = "PractitionerRole?_include=PractitionerRole:practitioner&_count=100"
    bundle = make_fhir_request('GET', query)
    
    if not bundle or bundle.get("total", 0) == 0:
        return {"status": "error", "error_message": "Tidak ada data dokter atau jadwal praktik yang ditemukan."}

    # 2. Pisahkan data Practitioner dan PractitionerRole untuk diproses
    practitioners = {
        f'Practitioner/{p["resource"]["id"]}': p["resource"] 
        for p in bundle.get("entry", []) 
        if p.get("resource", {}).get("resourceType") == "Practitioner"
    }
    roles = [
        r["resource"] 
        for r in bundle.get("entry", []) 
        if r.get("resource", {}).get("resourceType") == "PractitionerRole"
    ]

    # 3. Kelompokkan poli berdasarkan dokter
    doctor_specialties = {}
    for role in roles:
        practitioner_ref = role.get("practitioner", {}).get("reference")
        specialty = role.get("specialty", [{}])[0].get("text", "Tidak ada spesialisasi")
        
        if practitioner_ref not in doctor_specialties:
            doctor_specialties[practitioner_ref] = []
        
        # Hindari duplikasi poli untuk dokter yang sama
        if specialty not in doctor_specialties[practitioner_ref]:
            doctor_specialties[practitioner_ref].append(specialty)

    if not doctor_specialties:
        return {"status": "error", "error_message": "Gagal memproses data jadwal dokter."}

    # 4. Susun laporan akhir
    report_parts = ["Berikut adalah daftar semua dokter yang terdaftar beserta polinya:"]
    for practitioner_ref, specialties in doctor_specialties.items():
        practitioner = practitioners.get(practitioner_ref)
        if practitioner:
            name_parts = practitioner.get("name", [{}])[0]
            prefix = " ".join(name_parts.get("prefix", []))
            given = " ".join(name_parts.get("given", []))
            family = name_parts.get("family", "")
            suffix = ", ".join(name_parts.get("suffix", []))
            doctor_full_name = " ".join(part for part in [prefix, given, family, suffix] if part).strip()
            
            specialties_text = ", ".join(specialties)
            report_parts.append(f"- **{doctor_full_name}**: {specialties_text}")

    return {"status": "success", "report": "\n".join(report_parts)}

# Function to check upcoming appointments and send reminders    
def periksa_janji_temu(nama_depan: Optional[str] = None, nama_belakang: Optional[str] = None, tanggal_lahir: Optional[str] = None, mrn: Optional[str] = None) -> dict:
    """Memberikan pengingat janji temu."""
    patient_resource, error = verifikasi_pasien(nama_depan=nama_depan, nama_belakang=nama_belakang, tanggal_lahir=tanggal_lahir, mrn=mrn)
    if error: return error
    
    id_pasien = patient_resource["id"]
    
    # Dapatkan tanggal hari ini dalam format YYYY-MM-DD untuk filter kueri
    zona_waktu_wib = datetime.timezone(datetime.timedelta(hours=7))
    tanggal_hari_ini = datetime.datetime.now(zona_waktu_wib).strftime('%Y-%m-%d')

    # Tambahkan filter 'date=ge...' untuk hanya mencari janji temu mulai hari ini (ge = greater or equal)
    query = f"Appointment?actor=Patient/{id_pasien}&status=booked&date=ge{tanggal_hari_ini}&_sort=date&_count=1&_include=Appointment:patient&_include=Appointment:practitioner"
    bundle = make_fhir_request('GET', query)

    if not bundle or bundle.get("total", 0) == 0: return {"status": "error", "error_message": f"Tidak ada janji temu yang akan datang untuk pasien ini."}

    appointment, patient, practitioner = None, None, None
    for entry in bundle.get("entry", []):
        resource = entry.get("resource", {})
        if resource.get("resourceType") == "Appointment": appointment = resource
        elif resource.get("resourceType") == "Patient": patient = resource
        elif resource.get("resourceType") == "Practitioner": practitioner = resource
    if not appointment: return {"status": "error", "error_message": "Gagal menemukan detail janji temu. Pastikan data pasien sudah benar."}

    patient_name = patient['name'][0]['given'][0] if patient and 'name' in patient else 'Pasien'
    
    doctor_name = "Dokter"
    if practitioner and 'name' in practitioner:
        name_parts = practitioner['name'][0]
        prefix = " ".join(name_parts.get("prefix", []))
        given = " ".join(name_parts.get("given", []))
        family = name_parts.get("family", "")
        suffix = ", ".join(name_parts.get("suffix", []))
        
        # Gabungkan semua bagian menjadi satu string
        full_name_parts = [prefix, given, family, suffix]
        doctor_name = " ".join(part for part in full_name_parts if part).strip()
    
    start_time = datetime.datetime.fromisoformat(appointment.get("start"))

    # Logic to get Poli Name
    practitioner_id = practitioner["id"]
    role_bundle = make_fhir_request('GET', f"PractitionerRole?practitioner=Practitioner/{practitioner_id}")
    nama_poli = "Poli Umum" # Default
    if role_bundle and role_bundle.get("total", 0) > 0:
        role = role_bundle["entry"][0]["resource"]
        if "specialty" in role and len(role["specialty"]) > 0:
            nama_poli = role["specialty"][0].get("text", nama_poli)

    # Logic to get Daily Appointments
    appointment_date_str = start_time.strftime('%Y-%m-%d')
    daily_appointments_bundle = make_fhir_request('GET', f"Appointment?actor=Practitioner/{practitioner_id}&date={appointment_date_str}&_sort=date")
    
    queue_number = 0
    if daily_appointments_bundle and daily_appointments_bundle.get("total", 0) > 0:
        for i, app_entry in enumerate(daily_appointments_bundle.get("entry", [])):
            if app_entry.get("resource", {}).get("id") == appointment.get("id"):
                queue_number = i + 1
                break
    
    nama_hari = {0: "Senin", 1: "Selasa", 2: "Rabu", 3: "Kamis", 4: "Jumat", 5: "Sabtu", 6: "Minggu"}
    nama_bulan = {1: "Januari", 2: "Februari", 3: "Maret", 4: "April", 5: "Mei", 6: "Juni", 7: "Juli", 8: "Agustus", 9: "September", 10: "Oktober", 11: "November", 12: "Desember"}

    # Dapatkan nama hari dan bulan dari objek start_time
    hari_janji_temu = nama_hari[start_time.weekday()]
    bulan_janji_temu = nama_bulan[start_time.month]

    # Susun string tanggal lengkap dalam format Bahasa Indonesia
    tanggal_format_indonesia = f"{hari_janji_temu}, {start_time.day} {bulan_janji_temu} {start_time.year}"
    
    # Gunakan format tanggal yang baru di dalam pesan pengingat
    reminder_text = f"Halo **{patient_name}**. Anda memiliki janji temu di **{nama_poli}** dengan **{doctor_name}** pada **{tanggal_format_indonesia}** pukul **{start_time.strftime('%H:%M')}**."

    queue_text = f"Nomor antrian Anda adalah **{queue_number}**."
    return {"status": "success", "report": f"{reminder_text}\n{queue_text}\n \n Ada lagi yang bisa saya bantu?"}

# Function to create a new appointment after verification
def buat_janji_temu(nama_dokter: str, nama_poli: str, tanggal_dan_waktu: str, nama_depan: Optional[str] = None, nama_belakang: Optional[str] = None, tanggal_lahir: Optional[str] = None, mrn: Optional[str] = None) -> dict:
    """Membuat janji temu baru setelah verifikasi."""
    # 1. Verifikasi Pasien
    print(f"Input Diterima: nama_dokter='{nama_dokter}', nama_poli='{nama_poli}', tanggal_dan_waktu='{tanggal_dan_waktu}', nama_depan='{nama_depan}', nama_belakang='{nama_belakang}', tanggal_lahir='{tanggal_lahir}', mrn='{mrn}'")
    patient_resource, error = verifikasi_pasien(nama_depan=nama_depan, nama_belakang=nama_belakang, tanggal_lahir=tanggal_lahir, mrn=mrn)
    if error: 
        return error
    id_pasien = patient_resource["id"]

    # 2. Cari Dokter berdasarkan nama (misal: nama belakang)
    practitioner_bundle = make_fhir_request('GET', f"Practitioner?name:contains={quote(nama_dokter)}")
    
    if not practitioner_bundle or practitioner_bundle.get("total", 0) == 0:
        return {"status": "error", "error_message": f"Dokter dengan nama yang mengandung '{nama_dokter}' tidak ditemukan."}
    
    # Ambil resource dokter pertama yang ditemukan
    practitioner_resource = practitioner_bundle["entry"][0]["resource"]
    id_dokter = practitioner_resource["id"]
    
    # --- BAGIAN BARU: Menyusun Nama Lengkap Dokter ---
    name_data = practitioner_resource.get("name", [{}])[0]
    prefix = " ".join(name_data.get("prefix", []))
    given = " ".join(name_data.get("given", []))
    family = name_data.get("family", "")
    suffix = ", ".join(name_data.get("suffix", []))
    
    # Gabungkan semua bagian nama, bersihkan spasi berlebih
    parts = [prefix, given, family, suffix]
    nama_lengkap_dokter = " ".join(part for part in parts if part).strip()
    print(f"DEBUG: Nama lengkap dokter ditemukan: '{nama_lengkap_dokter}' dengan ID: {id_dokter}")


    # 3. Validasi Jadwal, Poli, dan Ketersediaan Dokter
    try:
        start_time = datetime.datetime.fromisoformat(tanggal_dan_waktu).astimezone(datetime.timezone.utc)
        end_time = start_time + datetime.timedelta(minutes=30)
    except ValueError:
        return {"status": "error", "error_message": "Format tanggal dan waktu tidak valid. Gunakan format YYYY-MM-DDTHH:MM:SS."}

    zona_waktu_wib = datetime.timezone(datetime.timedelta(hours=7))
    sekarang = datetime.datetime.now(zona_waktu_wib)

    # Cek apakah tanggal janji temu sebelum tanggal hari ini
    # Kita hanya membandingkan bagian tanggalnya saja (mengabaikan jam)
    if start_time.date() < sekarang.date():
        return {"status": "error", "error_message": "Anda tidak dapat membuat janji temu untuk tanggal yang sudah lewat. Silakan pilih tanggal hari ini atau setelahnya."}
    
    role_bundle = make_fhir_request('GET', f"PractitionerRole?practitioner=Practitioner/{id_dokter}&specialty:text={quote(nama_poli)}")
    
    if not role_bundle or role_bundle.get("total", 0) == 0:
        return {"status": "error", "error_message": f"Dokter {nama_lengkap_dokter} tidak ditemukan praktik di {nama_poli}."}

    is_available = False
    for role_entry in role_bundle.get("entry", []):
        role = role_entry.get("resource", {})
        for available in role.get("availableTime", []):
            day_of_week = [d[:3] for d in available.get("daysOfWeek", [])]
            start_hour = available.get("availableStartTime", "00:00")
            end_hour = available.get("availableEndTime", "23:59")
            
            if start_time.strftime('%a').lower() in day_of_week and start_hour <= start_time.strftime('%H:%M:%S') < end_hour:
                is_available = True
                break
        if is_available:
            break
    
    if not is_available:
        return {"status": "error", "error_message": f"Dokter {nama_lengkap_dokter} tidak tersedia pada jadwal yang Anda minta di {nama_poli}."}

    # 4. Hitung Nomor Antrian
    appointment_date_str = start_time.strftime('%Y-%m-%d')
    daily_appointments_bundle = make_fhir_request('GET', f"Appointment?actor=Practitioner/{id_dokter}&date={appointment_date_str}")
    queue_number = 1
    if daily_appointments_bundle and daily_appointments_bundle.get("total", 0) > 0:
        queue_number = daily_appointments_bundle.get("total", 0) + 1

    # 5. Buat Resource Appointment
    appointment_body = {
        "resourceType": "Appointment", "status": "booked",
        "start": start_time.isoformat(timespec='seconds'), "end": end_time.isoformat(timespec='seconds'),
        "participant": [
            {"actor": {"reference": f"Patient/{id_pasien}"}, "status": "accepted"},
            {"actor": {"reference": f"Practitioner/{id_dokter}"}, "status": "accepted"}
        ]
    }
    
    new_appointment = make_fhir_request('POST', 'Appointment', payload=appointment_body)
    
    if new_appointment and new_appointment.get("id"):

        # Pemetaan untuk nama hari dan bulan dalam Bahasa Indonesia
        nama_hari = {0: "Senin", 1: "Selasa", 2: "Rabu", 3: "Kamis", 4: "Jumat", 5: "Sabtu", 6: "Minggu"}
        nama_bulan = {1: "Januari", 2: "Februari", 3: "Maret", 4: "April", 5: "Mei", 6: "Juni", 7: "Juli", 8: "Agustus", 9: "September", 10: "Oktober", 11: "November", 12: "Desember"}

        # Dapatkan nama hari dan bulan dari objek start_time
        hari_janji_temu = nama_hari[start_time.weekday()]
        bulan_janji_temu = nama_bulan[start_time.month]

        # Susun string tanggal lengkap dalam format Bahasa Indonesia
        tanggal_format_indonesia = f"{hari_janji_temu}, {start_time.day} {bulan_janji_temu} {start_time.year}"
        
        # Gunakan format tanggal yang baru di dalam laporan
        return {
            "status": "success",
            "report": f"Janji temu baru di **{nama_poli}** dengan **{nama_lengkap_dokter}** pada **{tanggal_format_indonesia} pukul {start_time.strftime('%H:%M')}** berhasil dibuat. Nomor antrian Anda adalah **{queue_number}**."
        }
    return {"status": "error", "error_message": "Gagal membuat janji temu di sistem."}

# Function to check insurance benefits after verification
# def cek_program_asuransi(nama_depan: Optional[str] = None, nama_belakang: Optional[str] = None, tanggal_lahir: Optional[str] = None, mrn: Optional[str] = None) -> dict:
#     """Memeriksa program asuransi pasien setelah verifikasi."""
#     patient_resource, error = verifikasi_pasien(nama_depan=nama_depan, nama_belakang=nama_belakang, tanggal_lahir=tanggal_lahir, mrn=mrn)
#     if error: return error
#     id_pasien = patient_resource["id"]

#     coverage_bundle = make_fhir_request('GET', f"Coverage?beneficiary=Patient/{id_pasien}")
#     if not coverage_bundle or coverage_bundle.get("total", 0) == 0:
#         return {"status": "error", "error_message": "Informasi asuransi (coverage) tidak ditemukan untuk pasien ini."}
    
#     coverage = coverage_bundle["entry"][0]["resource"]
#     plan_name = coverage.get("type", {}).get("coding", [{}])[0].get("display", "Reguler")
#     return {"status": "success", "report": f"Anda terdaftar dalam program asuransi **'{plan_name}'**."}

# # Function to check insurance benefits after verification
# def cek_manfaat_asuransi(nama_depan: Optional[str] = None, nama_belakang: Optional[str] = None, tanggal_lahir: Optional[str] = None, mrn: Optional[str] = None) -> dict:
#     """Memeriksa manfaat asuransi pasien setelah verifikasi."""
#     patient_resource, error = verifikasi_pasien(nama_depan=nama_depan, nama_belakang=nama_belakang, tanggal_lahir=tanggal_lahir, mrn=mrn)
#     if error: return error
#     id_pasien = patient_resource["id"]

#     coverage_bundle = make_fhir_request('GET', f"Coverage?beneficiary=Patient/{id_pasien}")
#     if not coverage_bundle or coverage_bundle.get("total", 0) == 0:
#         return {"status": "error", "error_message": "Informasi asuransi (coverage) tidak ditemukan untuk pasien ini."}
    
#     coverage = coverage_bundle["entry"][0]["resource"]
#     plan_name = coverage.get("type", {}).get("coding", [{}])[0].get("display", "Reguler")
#     status = coverage.get("status", "tidak diketahui")
#     return {"status": "success", "report": f"Anda terdaftar dalam program asuransi '{plan_name}' dengan status '{status}'. Untuk detail manfaat lebih lanjut, silakan hubungi penyedia asuransi Anda."}

# # Function to check insurance claim status after verification
# def cek_status_klaim(nama_depan: Optional[str] = None, nama_belakang: Optional[str] = None, tanggal_lahir: Optional[str] = None, mrn: Optional[str] = None) -> dict:
#     """Memeriksa status klaim asuransi terakhir pasien setelah verifikasi."""
#     patient_resource, error = verifikasi_pasien(nama_depan=nama_depan, nama_belakang=nama_belakang, tanggal_lahir=tanggal_lahir, mrn=mrn)
#     if error: return error
#     id_pasien = patient_resource["id"]

#     claim_bundle = make_fhir_request('GET', f"Claim?patient=Patient/{id_pasien}&_sort=-created&_count=1")
#     if not claim_bundle or claim_bundle.get("total", 0) == 0:
#         return {"status": "error", "error_message": "Tidak ada riwayat klaim yang ditemukan untuk pasien ini."}

#     claim = claim_bundle["entry"][0]["resource"]
#     status = claim.get("status", "tidak diketahui")
#     total_value = claim.get("total", {}).get("value", "N/A")
#     currency = claim.get("total", {}).get("currency", "")
#     created_date = datetime.datetime.fromisoformat(claim.get("created")).strftime('%d %B %Y')
#     return {"status": "success", "report": f"Klaim terakhir Anda pada tanggal {created_date} sebesar {total_value} {currency} saat ini memiliki status '{status}'."}

# # Function to check last diagnosis
# def cek_diagnosis_terakhir(nama_depan: Optional[str] = None, nama_belakang: Optional[str] = None, tanggal_lahir: Optional[str] = None, mrn: Optional[str] = None) -> dict:
#     """Memeriksa diagnosis terakhir pasien dari riwayat kunjungan setelah verifikasi."""
#     patient_resource, error = verifikasi_pasien(nama_depan=nama_depan, nama_belakang=nama_belakang, tanggal_lahir=tanggal_lahir, mrn=mrn)
#     if error: return error
#     id_pasien = patient_resource["id"]

#     # Mencari Encounter (kunjungan) terakhir
#     encounter_bundle = make_fhir_request('GET', f"Encounter?patient=Patient/{id_pasien}&_sort=-date&_count=1")
#     if not encounter_bundle or encounter_bundle.get("total", 0) == 0:
#         return {"status": "error", "error_message": "Tidak ditemukan riwayat kunjungan untuk pasien ini."}

#     encounter = encounter_bundle["entry"][0]["resource"]

#     diagnosis_text = "Diagnosis tidak tercatat."
#     # Prioritas 1: Cek kolom 'diagnosis' (standar)
#     if "diagnosis" in encounter and len(encounter["diagnosis"]) > 0:
#         condition_ref = encounter["diagnosis"][0].get("condition", {}).get("reference")
#         if condition_ref:
#             condition_resource = make_fhir_request('GET', condition_ref)
#             if condition_resource and "code" in condition_resource:
#                 diagnosis_text = condition_resource["code"].get("text", diagnosis_text)
#     # Prioritas 2: Jika tidak ada, cek kolom 'reasonCode' (alternatif)
#     elif "reasonCode" in encounter and len(encounter["reasonCode"]) > 0:
#         diagnosis_text = encounter["reasonCode"][0].get("text", diagnosis_text)

#     patient_name = patient_resource.get("name", [{}])[0].get("given", ["Pasien"])[0]
    
#     return {"status": "success", "report": f"Halo {patient_name}. Berdasarkan kunjungan terakhir Anda, diagnosis yang tercatat adalah: {diagnosis_text}."}