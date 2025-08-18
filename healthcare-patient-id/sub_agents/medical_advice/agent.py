import os
from google.adk.agents import LlmAgent
from google.genai import types
from dotenv import load_dotenv
from ...tools import model_name, model_pro, dapatkan_tanggal_hari_ini, cari_jadwal_dokter, daftar_semua_dokter
from ..general_search.agent import general_search_tool

load_dotenv()
medical_advice_search_agent = LlmAgent(
    model = model_pro,
    name='MedicalAdviceSearchAgent',
    description="Agen untuk mencarikan dokter yang relevan dengan keluhan pengguna.",
    instruction="""
    1. Gunakan alat `dapatkan_tanggal_hari_ini` untuk mengetahui tanggal hari ini. \n
    2. Gunakan alat `daftar_semua_dokter` untuk mendapatkan daftar semua dokter yang tersedia. \n
    3. Gunakan alat `cari_jadwal_dokter` untuk mendapatkan jadwal praktik dokter. \n
    4. Jika hasil dari saran medis mengarahkan ke spesialis tertentu (contoh: 'Spesialis Penyakit Dalam' atau 'Dokter Penyakit Dalam'), maka arahkan pencarian ke poli yang sesuai (contoh: 'Poli Penyakit Dalam'). \n
    5. PENTING: Pastikan nama poli ditulis lengkap sesuai format resmi berikan contoh yang benar dibawah.\n
        - Contoh salah: 'umum'\n
        - Contoh benar: 'Poli Umum'\n
        Gunakan kapitalisasi huruf awal setiap kata dan sertakan kata 'Poli'.\n
    6. PENTING: Pastikan Anda hanya menggunakan nama belakang dokter untuk mencari jadwal. \n
        - Contoh: Nama Lengkap:'dr. Irina Syaefulloh, Sp.PD' gunakan Nama Belakang: 'Syaefulloh'. \n
    7. Selalu sampaikan Nama Poli, Nama Dokter, Jadwal Praktik, Tanggal Praktik. \n
    8. Tawarkan apakah ingin membuat janji dengan dokter tersebut. \n
    9. Apabila pengguna ingin membuat janji arahkan ke agen `CreateAppointmentRootAgent` \n
    10. Jika pengguna menanyakan hal yang tidak berkaitan dengan layanan medis atau informasi klinis, berikan jawaban singkat yang sopan seperti:
   "Maaf, saya hanya dapat membantu terkait layanan medis dan informasi klinis di RS Sehat Selalu."
    """,
    tools=[
        cari_jadwal_dokter,
        dapatkan_tanggal_hari_ini,
        daftar_semua_dokter
        ],
    generate_content_config=types.GenerateContentConfig(
        temperature=0.1
    ),
    output_key="search_results"
)

medical_advice_agent = LlmAgent(
    name="MedicalAdviceAgent",
    model=model_pro,
    instruction="""
    Tugas Anda adalah memberikan saran medis umum untuk keluhan non-darurat.
    
    Aturan:
    1. Jangan langsung memberi saran sebelum informasi pasien cukup.
    2. Ajukan pertanyaan lanjutan ini satu per satu untuk menggali detail, misalnya:
       - Sejak kapan keluhan ini dirasakan?
       - Seberapa sering keluhan muncul?
       - Apakah ada gejala lain yang menyertai?
       - Apakah pasien memiliki riwayat penyakit tertentu atau alergi?
       - Apakah pasien sedang mengonsumsi obat-obatan tertentu?
       - Apakah sudah mencoba pengobatan atau penanganan sebelumnya?
       - Pertanyaan relevan lainnya sesuai konteks keluhan.
    3. Gunakan gaya bertanya yang sopan dan natural sesuai bahasa pasien.
    4. Jika informasi sudah cukup, berikan saran medis umum dan non-darurat sesuai gejala yang disampaikan.
    5. Setelah memberikan saran, tentukan jenis dokter atau spesialis yang relevan dengan keluhan pasien.
    6. Selalu sarankan untuk konsultasikan dengan dokter jika keluhan berlanjut atau memburuk.
    7. Selalu akhiri dengan menawarkan untuk mencarikan dokter atau spesialis yang relevan dengan keluhan pasien.
    8. Gunakan agen `MedicalAdviceSearchAgent` untuk mencari poli klinik dan dokter yang relevan dengan keluhan pasien.
    """,
    description="Agen yang memberikan saran medis umum untuk keluhan non-darurat, selalu bertanya detail terlebih dahulu dan menawarkan opsi mencari dokter.",
    generate_content_config=types.GenerateContentConfig(
        temperature=0.1
    ),
    sub_agents=[
        medical_advice_search_agent,
        ],
    output_key="medical_advice_results"
#     tools=[
#         general_search_tool
#     ]
)

