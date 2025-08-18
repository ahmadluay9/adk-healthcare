from google.adk.agents import LlmAgent, SequentialAgent
from google.genai import types
from ...tools import periksa_janji_temu, model_name, model_pro, model_lite, dapatkan_data_pasien, dapatkan_waktu_sekarang, registrasi_pasien_baru
from ..new_patient_registration.prompts import registration_instruction
from ..check_upcoming_appointments.prompts import greeting_instruction

check_appointment_verify_patient_identity_agent = LlmAgent(
    name="CheckAppointmentVerifyPatientIdentityAgent",
    model=model_lite,
    description="Agen yang bertugas menyampaikan pesan sebelum proses pencarian data pasien.",
    instruction=("""
        Tugas Anda adalah sebagai berikut:
        1. Sampaikan pesan berikut kepada pengguna:
        "Saya akan bantu mencarikan data Anda. Mohon tunggu terlebih dahulu."
    """),
    generate_content_config=types.GenerateContentConfig(
        temperature=0.2
    )
)

check_appointment_verification_status_agent = LlmAgent(
    name="CheckAppointmentVerificationStatusAgent",
    model=model_name,
    description="Agen yang bertugas mencarikan data pasien.",
    instruction=("""
        Tugas Anda adalah adalah sebagai berikut:\n
        1. Gunakan email atau nomor telepon yang dimasukan pengguna untuk mendapatkan data pasien.\n
        2. Jika menggunakan email, pastikan seluruh huruf diubah menjadi huruf kecil (lowercase) sebelum diproses.\n
        3. Jika menggunakan nomor telepon, pastikan format nomor telepon dalam format internasional (contoh: 6281234567890).\n
        4. Panggil alat `dapatkan_data_pasien` untuk mendapatkan data pasien.
        5. Berdasarkan hasil dari pengecekan data pasien tersebut:\n
            a. Sampaikan respon dibawah ini jika pasien sudah terdaftar: \n
              - 'Terima kasih, **nama_lengkap_pasien**. Data Anda berhasil ditemukan.'\n
            b. Sampaikan respon dibawah ini jika pasien belum terdaftar: \n
              - 'Maaf, data Anda belum terdaftar dalam sistem kami.'\n
    """),
    generate_content_config=types.GenerateContentConfig(
        temperature=0.2
    ),
    output_key="verification_status",
    tools=[dapatkan_data_pasien]
)

check_appointment_patient_info_agent  = LlmAgent(
    name="CheckAppointmentPatientInfoAgent",
    model=model_lite,
    description="Agen yang menampilkan informasi identitas pasien (Nama, MRN).",
    instruction=("""
        Tugas Anda adalah sebagai berikut:\n
        1. Bila {verification_status} bernilai 'Data anda ditemukan': 
            - Berikan respon dengan format berikut:\n
                * Nama Depan:  \n
                * Nama Belakang:  \n
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
    description="Workflow untuk mencarikan data pasien sebelum mereka bisa memeriksa jadwal mereka dengan dokter.",
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
        1. Gunakan informasi dari {patient_info} untuk mengisi data pasien (Nama depan, Nama Belakang, Tanggal Lahir, MRN).\n
        2. Selalu ubah input tanggal lahir menjadi format ketat YYYY-MM-DD (contoh: '1985-05-20').\n
        3. Panggil alat `periksa_janji_temu` dengan data yang sesuai.\n
        4. Jika data ditemukan, berikan konfirmasi janji temu seperti contoh di bawah ini:\n
             'Halo **nama_pasien**, **MRN: mrn_pasien**.\n
             Anda memiliki janji temu di **nama_poli** dengan **nama_dokter**\n
             pada hari **tanggal_janji** pukul **jam_janji**.\n
             Nomor antrian Anda adalah **nomor_antrian**.\n
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
    1. Untuk pasien lama, selalu minta email atau nomor telepon (format: 628xxxxxxxxx) agar dapat dicarikan datanya. \n
    2. Pastikan format nomor telepon dalam format internasional (contoh: 6281234567890).\n
    3. Kemudian carikan data pasien terlebih dahulu menggunakan agen `check_appointment_patient_verification_workflow`.\n
    4. Apabila pengguna merupakan pasien baru arahkan untuk pendaftaran pasien baru menggunakan agen `check_appointment_new_patient_registration_agent`.
        - Apabila pendaftaran berhasil, arahkan kembali untuk untuk melakukan verifikasi pasien.\n
        - Apabila pendaftaran gagal, tawarkan untuk mengulang proses pendaftaran.\n
    5. Setelah verifikasi berhasil, pengguna bisa periksa janji temu dengan dokter menggunakan agen `check_appointment_agent`.\n
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