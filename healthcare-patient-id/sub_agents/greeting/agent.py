from google.adk.agents import LlmAgent
from ...tools import model_name, dapatkan_waktu_sekarang
from .prompts import services_id

# Inisialisasi agen sapaan
greeting_agent = LlmAgent(
    name="GreetingAgent",
    model=model_name,
    instruction=f"""
    Gunakan alat `dapatkan_waktu_sekarang` untuk mengetahui waktu saat ini.
    Berdasarkan jam sekarang, tentukan salam yang tepat:

    Aturan salam:
    - 04:00–10:59 → "Selamat Pagi"
    - 11:00–14:59 → "Selamat Siang"
    - 15:00–18:59 → "Selamat Sore"
    - 19:00–03:59 → "Selamat Malam"

    Format respon:
    "Selamat Pagi/Siang/Sore/Malam! Selamat datang di Asisten Klinis Virtual. \n\n{services_id}\n"
    """,
    description="Menyapa pengguna sesuai waktu setempat.",
    tools=[dapatkan_waktu_sekarang]
)

