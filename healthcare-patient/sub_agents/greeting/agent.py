from google.adk.agents import LlmAgent, SequentialAgent
from ...tools import model_name, model_lite, dapatkan_waktu_sekarang

greeting_agent = LlmAgent(
    name="GreetingAgent",
    model=model_name,
    instruction="""
    Gunakan alat `dapatkan_waktu_sekarang` untuk mengetahui waktu saat ini.
    Berdasarkan jam sekarang, tentukan salam yang tepat dalam Bahasa Indonesia dan Inggris:

    Aturan salam:
    - 04:00–10:59 → "Selamat Pagi" / "Good Morning"
    - 11:00–14:59 → "Selamat Siang" / "Good Afternoon"
    - 15:00–18:59 → "Selamat Sore" / "Good Evening"
    - 19:00–03:59 → "Selamat Malam" / "Good Evening" atau "Good Night"

    Format respon:
    "Selamat Pagi/Siang/Sore/Malam! Selamat datang di Asisten Klinis Virtual. / Good Morning/Afternoon/Evening/Night! Welcome to the Virtual Clinical Assistant."
    """,
    description="Menyapa pengguna dalam Bahasa Indonesia dan Inggris sesuai waktu setempat.",
    tools=[dapatkan_waktu_sekarang]
)

ask_language_agent = LlmAgent(
    name="AskLanguageAgent",
    model=model_lite,
    instruction="""
    Tanyakan preferensi bahasa kepada pengguna dalam dua bahasa:

    "Untuk memulai, silakan pilih bahasa yang Anda inginkan: **Bahasa Indonesia** atau **English**? /
    To get started, please select your preferred language: **Bahasa Indonesia** or **English**?"
    """,
    description="Mengajukan pertanyaan pilihan bahasa kepada pengguna."
)

greeting_workflow = SequentialAgent(
    name="GreetingWorkflow",
    description="Memandu pengguna melalui sapaan dan pertanyaan pilihan bahasa.",
    sub_agents=[
        greeting_agent,
        ask_language_agent
    ]
)
