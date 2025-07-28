import os
from callback_logging import log_query_to_model, log_model_response
import datetime

from google.adk.agents import Agent
from google.adk.tools import VertexAiSearchTool, agent_tool

from dotenv import load_dotenv

load_dotenv()
model_name = os.getenv("MODEL")
os.environ['GOOGLE_CLOUD_PROJECT'] = os.getenv('GOOGLE_CLOUD_PROJECT')
os.environ['GOOGLE_CLOUD_LOCATION'] = os.getenv('GOOGLE_CLOUD_LOCATION')
os.environ["GOOGLE_GENAI_USE_VERTEXAI"] = os.getenv('GOOGLE_GENAI_USE_VERTEXAI')

vertexai_search_tool = VertexAiSearchTool(
    data_store_id=f"projects/{os.getenv('GOOGLE_CLOUD_PROJECT')}/locations/global/collections/default_collection/dataStores/{os.getenv('DATASTORE_ID')}"
)

search_agent = Agent(
    model='gemini-2.0-flash',
    name='SearchAgent',
    instruction="""
    Anda adalah asisten klinis yang siap membantu. Gunakan alat pencarian `vertex_ai_search_tool` untuk menjawab pertanyaan umum dari pasien (seperti jam buka atau lokasi). 
    """,
    tools=[vertexai_search_tool],
)

# --- Database Tiruan ---
# Dalam aplikasi nyata, data ini akan berasal dari database yang aman atau sistem Rekam Medis Elektronik (RME).
mock_patient_appointments = {
    "pasien_1234": {
        "nama": "Budi Santoso",
        "waktu_janji_temu": datetime.datetime.now() + datetime.timedelta(days=3),
        "dokter": "Dr. Lestari",
    }
}

# --- Alat untuk Studi Kasus 2: Perencanaan Pra-Kunjungan ---
def dapatkan_pengingat_janji_temu(id_pasien: str) -> dict:
    """
    Memberikan pengingat janji temu untuk ID pasien yang diberikan.

    Alat ini menangani aspek 'Pengingat janji temu' dari 'Perencanaan pra-kunjungan'.

    Args:
        id_pasien (str): Nomor identifikasi unik untuk pasien.

    Returns:
        dict: Dictionary dengan status dan pesan pengingat atau pesan kesalahan.
    """
    if id_pasien in mock_patient_appointments:
        appointment = mock_patient_appointments[id_pasien]
        # Mengatur locale untuk nama hari dan bulan dalam Bahasa Indonesia
        # Ini memerlukan setup tambahan di lingkungan Anda. Untuk sederhana, kita gunakan format standar.
        appt_date = appointment["waktu_janji_temu"].strftime("%A, %d %B") # e.g., Sunday, 27 July
        appt_time = appointment["waktu_janji_temu"].strftime("%H:%M")
        return {
            "status": "success",
            "report": (
                f"Halo {appointment['nama']}. Anda memiliki janji temu dengan "
                f"{appointment['dokter']} pada hari {appt_date} pukul {appt_time}."
            ),
        }
    else:
        return {
            "status": "error",
            "error_message": f"Maaf, saya tidak dapat menemukan janji temu untuk ID pasien '{id_pasien}'.",
        }

def kirim_kuesioner_pra_kunjungan(id_pasien: str) -> dict:
    """
    Mengirimkan tautan ke kuesioner pra-kunjungan untuk seorang pasien.

    Alat ini menangani aspek 'kuesioner pra-kunjungan' dari 'Perencanaan pra-kunjungan'.

    Args:
        id_pasien (str): Nomor identifikasi unik untuk pasien.

    Returns:
        dict: Dictionary dengan status dan pesan konfirmasi.
    """
    if id_pasien in mock_patient_appointments:
        # Dalam sistem nyata, ini akan memicu pengiriman email atau SMS.
        questionnaire_url = "https://example.com/survei-pra-kunjungan?id=123"
        return {
            "status": "success",
            "report": (
                f"Tautan ke kuesioner pra-kunjungan telah dikirim ke metode kontak yang terdaftar untuk ID pasien {id_pasien}. "
                f"Anda juga bisa mengaksesnya di sini: {questionnaire_url}"
            ),
        }
    else:
        return {
            "status": "error",
            "error_message": f"Tidak dapat mengirim kuesioner. Tidak ada janji temu yang ditemukan untuk ID pasien '{id_pasien}'.",
        }


# --- Definisi Agen yang Diperbarui ---
# Agen sekarang dikonfigurasi untuk menjadi asisten klinis menggunakan alat-alat baru.
root_agent = Agent(
    name="agen_asisten_klinis",
    model="gemini-2.0-flash",
    description=(
        "Agen yang membantu keterlibatan pasien dan perencanaan pra-kunjungan dengan mencari informasi."
    ),
    before_model_callback=log_query_to_model,
    after_model_callback=log_model_response,
    instruction=(
        "Anda adalah asisten klinis yang siap membantu. Gunakan alat pencarian `vertex_ai_search_tool` untuk menjawab pertanyaan umum dari pasien (seperti jam buka atau lokasi). "
        "Gunakan alat lain untuk memberikan pengingat janji temu dan mengirim kuesioner pra-kunjungan. "
        "ID pasien untuk pengujian adalah 'pasien_1234'. Bersikaplah sopan dan profesional."
    ),
    tools=[
        dapatkan_pengingat_janji_temu, 
        kirim_kuesioner_pra_kunjungan,
        agent_tool.AgentTool(agent=search_agent)
    ],
)