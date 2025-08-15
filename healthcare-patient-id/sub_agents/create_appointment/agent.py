from google.adk.agents import LlmAgent, SequentialAgent
from google.genai import types
from ..general_search.agent import general_search_tool
from ...tools import buat_janji_temu, dapatkan_tanggal_hari_ini, dapatkan_waktu_sekarang, model_name, model_lite, model_pro, dapatkan_data_pasien_dari_email, registrasi_pasien_baru
from ..create_appointment.prompts import appointment_instruction, greeting_instruction, registration_instruction

create_appointment_verify_patient_identity_agent = LlmAgent(
    name="CreateAppointmentVerifyPatientIdentityAgent",
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

create_appointment_verification_status_agent = LlmAgent(
    name="CreatePatientVerificationStatusAgent",
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

create_appointment_patient_info_agent  = LlmAgent(
    name="CreateAppointmentPatientInfoAgent",
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

create_appointment_greeting_agent = LlmAgent(
    name="CreateAppointmentGreetingAgent",
    model=model_name,
    instruction=greeting_instruction,
    description="Menyapa pengguna sesuai waktu setempat dan menanyakan langkah selajutnya (buat janji temu atau pendaftaran pasien baru).",
    tools=[dapatkan_waktu_sekarang]
)

create_apointment_patient_verification_workflow = SequentialAgent(
    name="CreateApointmentPatientVerificationWorkflow",
    sub_agents=[
        create_appointment_verify_patient_identity_agent, 
        create_appointment_verification_status_agent, 
        create_appointment_patient_info_agent, 
        create_appointment_greeting_agent
        ],
    description="Workflow untuk memverifikasi identitas pasien sebelum mereka bisa membuat janji temu mereka dengan dokter.",
)

create_apointment_new_patient_registration_agent = LlmAgent(
    name="CreateApointmentNewPatientRegistrationAgent",
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


create_appointment_agent = LlmAgent(
    model = model_pro,
    name='CreateAppointmentAgent',
    description="Agen untuk membuat janji temu baru untuk pasien dengan dokter tertentu.",
    instruction=appointment_instruction,
    tools=[
        buat_janji_temu, 
        dapatkan_tanggal_hari_ini,
        general_search_tool
        ],
    output_key="appointment_confirmation",
    generate_content_config=types.GenerateContentConfig(
        temperature=0.1
    )
)


create_appointment_root_agent = LlmAgent(
    model = model_pro,
    name='CreateAppointmentRootAgent',
    description="Agen utama untuk proses verifikasi dan membuat janji temu baru untuk pasien dengan dokter tertentu.",
    instruction="""
    1. Selalu tanyakan email atau nomor telepon pengguna.\n
    2. Kemudian Lakukan verifikasi pasien terlebih dahulu menggunakan agen `create_apointment_patient_verification_workflow`.\n
    3. Apabila pengguna merupakan pasien baru arahkan untuk pendaftaran pasien baru menggunakan agen `create_apointment_new_patient_registration_agent`.
        - Apabila pendaftaran berhasil, arahkan kembali untuk untuk melakukan verifikasi pasien.\n
        - Apabila pendaftaran gagal, tawarkan untuk mengulang proses pendaftaran.\n
    4. Setelah verifikasi berhasil, pengguna bisa membuat janji temu dengan dokter menggunakan agen `create_appointment_agent`.\n
""",
    sub_agents=[
        create_apointment_patient_verification_workflow,
        create_apointment_new_patient_registration_agent,
        create_appointment_agent
        ],
    generate_content_config=types.GenerateContentConfig(
        temperature=0.1
    )
)

