from google.adk.agents import LlmAgent, SequentialAgent
from ...tools import model_name, dapatkan_waktu_sekarang
from .prompts import services_id

# Inisialisasi agen sapaan
# greeting_agent = LlmAgent(
#     name="GreetingAgent",
#     model=model_name,
#     instruction=f"""
#     Gunakan alat `dapatkan_waktu_sekarang` untuk mengetahui waktu saat ini.
#     Berdasarkan jam sekarang, tentukan salam yang tepat:

#     Aturan salam:
#     - 04:00–10:59 → "Selamat Pagi"
#     - 11:00–14:59 → "Selamat Siang"
#     - 15:00–18:59 → "Selamat Sore"
#     - 19:00–03:59 → "Selamat Malam"

#     Format respon:
#     "Selamat Pagi/Siang/Sore/Malam! Selamat datang di Asisten Klinis Virtual. \n\n{services_id}\n"
#     """,
#     description="Menyapa pengguna sesuai waktu setempat.",
#     tools=[dapatkan_waktu_sekarang]
# )

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
    "Selamat Pagi/Siang/Sore/Malam! Selamat datang di Asisten Klinis Virtual. \n"
    """,
    description="Menyapa pengguna sesuai waktu setempat.",
    tools=[dapatkan_waktu_sekarang]
)

email_confirmation_agent = LlmAgent(
    name="EmailConfirmationAgent",
    model=model_name,
    instruction="""
    1. Tanyakan alamat email atau nomor telepon ke pengguna yang sudah terdaftar, Seperti pesan berikut:
    "Saya akan melakukan verifikasi identitas Anda terlebih dahulu. \n 
   Mohon berikan alamat email atau nomor telepon yang terdaftar."
    2. Kemudian setelah pengguna memasukan email atau nomor telepon arahkan ke agen `patient_verification_workflow`.
    """,
    description="Agen yang bertugas menanyakan email atau nomor telepon ke pengguna yang sudah terdaftar kemudian mengarahkan ke proses verifikasi identitas"
)

greeting_workflow = SequentialAgent(
    name="PatientVerificationWorkflow",
    sub_agents=[
        greeting_agent, 
        email_confirmation_agent
        ],
    description="Workflow untuk memverifikasi identitas pasien.",
)