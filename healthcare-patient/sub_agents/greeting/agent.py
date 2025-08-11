from google.adk.agents import LlmAgent, SequentialAgent, BaseAgent
from google.adk.events import Event, EventActions
from google.adk.agents.invocation_context import InvocationContext
from google.genai import types
from typing import AsyncGenerator
from ...tools import model_name, pilih_bahasa

# language_selection_tool = FunctionTool(func=pilih_bahasa)

greeting_agent = LlmAgent(
    name="GreetingAgent",
    model=model_name,
    instruction="""
    Sapa pengguna dalam dua bahasa dengan pesan ini:
    "Halo! Selamat datang di Asisten Klinis Virtual. / Hello! Welcome to the Virtual Clinical Assistant."
    """,
    description="Menyapa pengguna dalam Bahasa Indonesia dan Inggris."
)

ask_language_agent = LlmAgent(
    name="AskLanguageAgent",
    model=model_name,
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

# --- 2. Agen Pemilihan Bahasa (Disederhanakan) ---
# Tugasnya hanya menanyakan dan mendapatkan nama bahasa.
# language_selection_agent = LlmAgent(
#     name="LanguageSelectionAgent",
#     model=model_name,
#     instruction="""
#     Tanyakan preferensi bahasa kepada pengguna: "Untuk memulai, silakan pilih bahasa yang Anda inginkan: **Bahasa Indonesia** atau **English**?"

#     PENTING: Respons AKHIR Anda HARUS HANYA nama bahasa yang mereka pilih.
#     Contoh output yang benar: 'Bahasa Indonesia' atau 'English'.
#     Jangan tambahkan kata-kata atau kalimat lain.
#     """,
#     description="Meminta pengguna memilih bahasa dan menyimpan nama bahasa tersebut ke state.",
#     generate_content_config=types.GenerateContentConfig(
#         temperature=0.1
#     ),
#     # Menggunakan satu kunci state yang konsisten.
#     output_key="user_language"
# )

# # --- 3. Agen Penjaga (Disederhanakan) ---
# # Memeriksa apakah nama bahasa valid.
# class LanguageGuard(BaseAgent):
#     """
#     Memeriksa apakah state 'user_language' berisi 'Bahasa Indonesia' atau 'English'.
#     Jika tidak, hentikan alur kerja.
#     """
#     async def _run_async_impl(self, ctx: InvocationContext) -> AsyncGenerator[Event, None]:
#         # Membaca dari kunci state yang benar.
#         language = ctx.session.state.get("user_language")

#         # Memeriksa apakah nilainya salah satu dari yang valid.
#         is_valid = language in ["Bahasa Indonesia", "English"]
#         should_stop = not is_valid

#         if should_stop:
#             error_message = "Maaf, terjadi kesalahan dalam pemilihan bahasa. Silakan coba lagi."
#             yield Event(
#                 author=self.name,
#                 content=types.Content(parts=[types.Part(text=error_message)])
#             )

#         # Hentikan alur jika bahasa tidak valid.
#         yield Event(author=self.name, actions=EventActions(escalate=should_stop))


# # --- 4. Agen Status Pasien ---
# # Tidak perlu diubah, karena sudah menggunakan {user_language}.
# patient_status_agent = LlmAgent(
#     name="PatientStatusAgent",
#     model=model_name,
#     instruction="""
#     Anda adalah agen yang bertugas menanyakan status pasien.

#     1.  Gunakan Bahasa yang telah dipilih pengguna: {user_language}.
#     2.  Tanyakan apakah pengguna adalah **Pasien Baru** atau **Pasien Lama**.
#         - Jika {user_language} adalah 'Bahasa Indonesia', tanyakan: "Apakah Anda **Pasien Baru** atau **Pasien Lama**?"
#         - Jika {user_language} adalah 'English', tanyakan: "Are you a **New Patient** or an **Existing Patient**?"
#     3.  Tunggu jawaban pengguna. Respons AKHIR Anda HARUS HANYA status yang mereka pilih (contoh: 'Pasien Baru' atau 'New Patient').
#     """,
#     description="Menanyakan status pasien (baru atau lama) dalam bahasa yang sesuai.",
#     generate_content_config=types.GenerateContentConfig(
#         temperature=0.1
#     ),
#     output_key="patient_status"
# )


# # --- Alur Kerja Sequential ---
# clinical_workflow = SequentialAgent(
#     name="ClinicalAssistantWorkflow",
#     description="Memandu pengguna melalui sapaan, pemilihan bahasa, dan pemeriksaan status pasien dengan alur yang lebih sederhana dan tangguh.",
#     sub_agents=[
#         greeting_agent,
#         language_selection_agent,
#         LanguageGuard(name="LanguageGuard"), # <-- Agen penjaga yang lebih sederhana
#         patient_status_agent
#     ]
# )
# # greeting_agent = LlmAgent(
#     name="GreetingAgent",
#     model= model_name,
#     instruction="""
#     Anda adalah agen penyambut yang ramah. Tugas Anda adalah sebagai berikut:
#     1. Sapa pengguna dalam dua bahasa dengan pesan: "Halo! Selamat datang di Asisten Klinis Virtual. / Hello! Welcome to the Virtual Clinical Assistant."
#     2. Tanyakan preferensi bahasa mereka dalam dua bahasa dengan pertanyaan: "\n Untuk memulai, silakan pilih bahasa yang Anda inginkan: **Bahasa Indonesia** atau **English**? / To get started, please select your preferred language: **Bahasa Indonesia** or **English**?"
#     3. PENTING: Setelah pengguna menjawab, respons AKHIR Anda HARUS HANYA nama bahasa yang mereka pilih (contoh: 'English' atau 'Bahasa Indonesia'). Jangan tambahkan kata-kata lain.
#     """,
#     description="Menyapa pengguna, menanyakan preferensi bahasa, dan menyimpan pilihan bahasa tersebut ke dalam state.",    
#     generate_content_config=types.GenerateContentConfig(
#         temperature=0.1
#     )
# )

# # Agent that calls the Language Selection tool
# language_selection_agent = LlmAgent(
#     name="LanguageSelection",
#     model= model_name,
#     instruction="""
#     Gunakan alat `language_selection_tool` untuk meminta pengguna memilih bahasa yang mereka inginkan.
#     """,
#     description="Menyapa pengguna, menanyakan preferensi bahasa, dan menyimpan pilihan bahasa tersebut ke dalam state.",
#     tools=[language_selection_tool],
#     generate_content_config=types.GenerateContentConfig(
#         temperature=0.1
#     ),
#     output_key="user:language"
# )

# # Agent that proceeds based on human decision
# process_decision = LlmAgent(
#     name="ProcessDecision",
#     instruction="Check {user:language}. If 'approved', proceed. If 'rejected', inform user."
# )

# patient_status_agent = LlmAgent(
#     name="PatientStatus",
#     model= model_name,
#     instruction="""
#     Anda adalah agen yang bertugas sebagai berikut:
#     1. Gunakan Bahasa: {user:language}.
#     2. Tanyakan apakah pengguna merupakan **Pasien Baru** atau **Pasien Lama**.
#         - Tanyakan: "Apakah Anda **Pasien Baru** atau **Pasien Lama**?"
#     3. Jika pengguna memilih **Pasien Baru**:
#         - Tanyakan: "Anda adalah **Pasien Baru**.\n Apakah Anda ingin mendaftar sebagai pasien baru?"
#     4. Jika pengguna memilih **Pasien Lama**:
#         - Tanyakan: "Anda adalah **Pasien Lama**.\n Apakah Anda ingin melanjutkan proses verifikasi identitas?"
#     """,
#     description="Menanyakan status pasien (baru atau lama), lalu menindaklanjuti dengan pertanyaan pendaftaran atau verifikasi sesuai pilihan pengguna, dengan contoh respons untuk konsistensi.",
#     generate_content_config=types.GenerateContentConfig(
#         temperature=0.1
#     ),
#     output_key="patient_status"
# )

# patient_status_agent = LlmAgent(
#     name="PatientStatus",
#     model= model_name,
#     instruction="""
#     Anda adalah agen yang bertugas sebagai berikut:
#     1. Gunakan Bahasa: {user:language}.
#     2. Tanyakan apakah pengguna merupakan **Pasien Baru** atau **Pasien Lama**.
#         - Tanyakan: "Apakah Anda **Pasien Baru** atau **Pasien Lama**?"
#     3. Jika pengguna memilih **Pasien Baru**:
#         - Tanyakan: "Anda adalah **Pasien Baru**.\n Apakah Anda ingin mendaftar sebagai pasien baru?"
#     4. Jika pengguna memilih **Pasien Lama**:
#         - Tanyakan: "Anda adalah **Pasien Lama**.\n Apakah Anda ingin melanjutkan proses verifikasi identitas?"
#     """,
#     description="Menanyakan status pasien (baru atau lama), lalu menindaklanjuti dengan pertanyaan pendaftaran atau verifikasi sesuai pilihan pengguna, dengan contoh respons untuk konsistensi.",
#     generate_content_config=types.GenerateContentConfig(
#         temperature=0.1
#     ),
#     output_key="patient_status"
# )


# greeting_workflow = SequentialAgent(
#     name="GreetingWorkflow",
#     description="Memandu pengguna melalui sapaan, pemilihan bahasa, dan kemudian melanjutkan ke pemeriksaan status pasien.",
#     sub_agents=[
#         greeting_agent,
#         language_selection_agent,
#         patient_status_agent
#     ]
# )

# 3. Setelah pengguna memilih bahasa, lakukan dua langkah respons:
#     a. Konfirmasi pilihan bahasa:
#         - Jika pengguna memilih "Bahasa Indonesia", respons Anda adalah: "Anda memilih **Bahasa Indonesia**. \n"
#         - Jika pengguna memilih "English", respons Anda adalah: "You have chosen **English**. \n"
#     b. Tanyakan apakah ingin melanjutkan ke langkah selanjutnya:
#         - Jika "Bahasa Indonesia": "\n Apakah Anda ingin melanjutkan ke langkah selanjutnya untuk memeriksa status pasien Anda?"
#         - Jika "English": "\n Would you like to continue to the next step to check your patient status?"
# 4. Setelah mendapatkan persetujuan, lanjutkan ke agen `patient_status_agent`.
