from google.adk.agents import LlmAgent, SequentialAgent
from google.genai import types
from ...tools import periksa_janji_temu, model_name, model_pro, model_lite, dapatkan_data_pasien_dari_email, dapatkan_waktu_sekarang, registrasi_pasien_baru
from ..new_patient_registration.prompts import registration_instruction
from ..check_upcoming_appointments.prompts import greeting_instruction

check_appointment_verify_patient_identity_agent = LlmAgent(
    name="CheckAppointmentVerifyPatientIdentityAgent",
    model=model_lite,
    description="Agen yang bertugas menyampaikan pesan sebelum proses verifikasi identitas pasien.",
    instruction=("""
        Tugas Anda adalah sebagai berikut:
        1. Sampaikan pesan berikut kepada pengguna:
        "Saya akan melakukan verifikasi identitas anda terlebih dahulu."
    """),
    generate_content_config=types.GenerateContentConfig(
        temperature=0.2
    )
)

check_appointment_verification_status_agent = LlmAgent(
    name="CheckAppointmentVerificationStatusAgent",
    model=model_name,
    description="Agen yang bertugas memverifikasi identitas pasien.",
    instruction=("""
        Tugas Anda adalah adalah sebagai berikut:\n
        1. Gunakan email yang dimasukan pengguna untuk mendapatkan data pasien.\n
        2. Panggil alat `dapatkan_data_pasien_dari_email` untuk mendapatkan data pasien.
        3. Berdasarkan hasil dari pengecekan data pasien tersebut:\n
            a. Sampaikan respon dibawah ini jika pasien sudah terdaftar: \n
              - 'Terima kasih, **nama_lengkap_pasien**. **Anda sudah terverifikasi**.'\n
            b. Sampaikan respon dibawah ini jika pasien belum terdaftar: \n
              - '**Anda belum terdaftar**.'\n
    """),
    generate_content_config=types.GenerateContentConfig(
        temperature=0.2
    ),
    output_key="verification_status",
    tools=[dapatkan_data_pasien_dari_email]
)

check_appointment_patient_info_agent  = LlmAgent(
    name="CheckAppointmentPatientInfoAgent",
    model=model_lite,
    description="Agen yang menampilkan informasi identitas pasien (Nama, Tanggal Lahir, MRN).",
    instruction=("""
        Tugas Anda adalah sebagai berikut:\n
        1. Bila {verification_status} bernilai 'terverifikasi': 
            - Berikan respon dengan format berikut:\n
                * Nama Depan:  \n
                * Nama Belakang:  \n
                * Tanggal Lahir: hari bulan tahun\n
                * MRN: \n
            - Jangan tampilkan baris field yang kosong.
        2. Jika {verification_status} bernilai 'belum terdaftar', sampaikan kepada pengguna data anda tidak ditemukan.
    """),
    output_key="patient_info",
    generate_content_config=types.GenerateContentConfig(
        temperature=0.2
    )
)

check_apointment_greeting_agent = LlmAgent(
    name="CheckAppointmentGreetingAgent",
    model=model_name,
    instruction=greeting_instruction,
    description="Menyapa pengguna sesuai waktu setempat dan menanyakan langkah selajutnya (periksa janji atau pendaftaran pasien baru).",
    tools=[dapatkan_waktu_sekarang]
)

check_appointment_patient_verification_workflow = SequentialAgent(
    name="CheckApointmentPatientVerificationWorkflow",
    sub_agents=[
        check_appointment_verify_patient_identity_agent, 
        check_appointment_verification_status_agent, 
        check_appointment_patient_info_agent, 
        check_apointment_greeting_agent
        ],
    description="Workflow untuk memverifikasi identitas pasien sebelum mereka bisa memeriksa jadwal mereka dengan dokter.",
)

check_appointment_new_patient_registration_agent = LlmAgent(
    name="CheckApointmentNewPatientRegistrationAgent",
    model=model_name,
    description="Agen untuk memandu pengguna melalui proses pendaftaran pasien baru.",
instruction = registration_instruction,
    tools=[
            registrasi_pasien_baru,
            dapatkan_waktu_sekarang
           ],
    generate_content_config=types.GenerateContentConfig(
        temperature=0.1
    )
)

check_appointment_agent = LlmAgent(
    model=model_pro,
    name='CheckAppointmentAgent',
    description="Agen untuk memeriksa jadwal janji temu pasien yang akan datang dan mengirimkan tautan kuesioner.",
    instruction=("""                 
        Tugas Anda adalah membantu pasien memeriksa janji temu mereka.\n
        1. Bila belum ada, tanyakan nama lengkap dan tanggal lahir pasien.\n
        2. Panggil alat `periksa_janji_temu` dengan data yang sesuai.\n
        3. Jika data ditemukan, berikan konfirmasi janji temu seperti contoh di bawah ini:\n
             'Halo **Bono Suwono**, **MRN: 0034567891**.\n
             Anda memiliki janji temu di **Poli Umum** dengan **dr. Irina Syaefulloh, Sp.PD**\n
             pada hari **Minggu, 17 Agustus 2025** pukul **10:00**.\n
             Nomor antrian Anda adalah **1**.\n
             Ada lagi yang bisa saya bantu?'\n
    """),
    tools=[periksa_janji_temu],
    output_key="upcoming_appointment",
    generate_content_config=types.GenerateContentConfig(
        temperature=0.1
    )
)

check_appointment_root_agent = LlmAgent(
    model=model_pro,
    name='CheckAppointmentRootAgent',
    description="Agen utama untuk proses verifikasi dan memeriksa jadwal janji temu pasien yang akan datang.",
    instruction=("""
    1. Selalu tanyakan email atau nomor telepon pengguna.\n
    2. Kemudian Lakukan verifikasi pasien terlebih dahulu menggunakan agen `check_appointment_patient_verification_workflow`.\n
    3. Apabila pengguna merupakan pasien baru arahkan untuk pendaftaran pasien baru menggunakan agen `check_appointment_new_patient_registration_agent`.
        - Apabila pendaftaran berhasil, arahkan kembali untuk untuk melakukan verifikasi pasien.\n
        - Apabila pendaftaran gagal, tawarkan untuk mengulang proses pendaftaran.\n
    3. Setelah verifikasi berhasil, pengguna bisa periksa janji temu dengan dokter menggunakan agen `check_appointment_agent`.\n
"""),
    sub_agents=[
        check_appointment_patient_verification_workflow,
        check_appointment_agent,
        check_appointment_new_patient_registration_agent
        ],
    generate_content_config=types.GenerateContentConfig(
        temperature=0.1
    )
)