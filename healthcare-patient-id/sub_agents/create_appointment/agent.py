from google.adk.agents import LlmAgent, SequentialAgent
from google.genai import types
from ..general_search.agent import general_search_tool
from ...tools import buat_janji_temu, \
                    dapatkan_tanggal_hari_ini, \
                    registrasi_pasien_baru, \
                    dapatkan_waktu_sekarang, \
                    model_name, \
                    model_lite, \
                    model_pro, \
                    dapatkan_data_pasien, \
                    registrasi_pasien_baru, \
                    cari_jadwal_dokter, \
                    daftar_semua_dokter
from ..create_appointment.prompts import appointment_instruction, greeting_instruction, registration_instruction

create_appointment_verify_patient_identity_agent = LlmAgent(
    name="CreateAppointmentVerifyPatientIdentityAgent",
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

create_appointment_verification_status_agent = LlmAgent(
    name="CreatePatientVerificationStatusAgent",
    model=model_name,
    description="Agen yang bertugas mencarikan data pasien.",
    instruction=("""
        Tugas Anda adalah adalah sebagai berikut:\n
        1. Gunakan email atau nomor telepon yang dimasukan pengguna untuk mendapatkan data pasien.\n
        2. Jika menggunakan email, pastikan seluruh huruf diubah menjadi huruf kecil (lowercase) sebelum diproses.\n
        3. Pastikan format nomor telepon di ubah dalam format internasional (contoh: 6281234567890).\n
        4. Panggil alat `dapatkan_data_pasien` untuk mendapatkan data pasien.
        5. Berdasarkan hasil dari pengecekan data pasien tersebut:\n
            a. Sampaikan respon dibawah ini jika data pasien ditemukan: \n
              - 'Terima kasih, **nama_lengkap_pasien**. Data Anda berhasil ditemukan.'\n
            b. Sampaikan respon dibawah ini jika data pasien tidak ditemukan: \n
              - 'Maaf, data dengan **{email/nomor_telepon}** tidak terdaftar dalam sistem kami.'\n
    """),
    generate_content_config=types.GenerateContentConfig(
        temperature=0.2
    ),
    output_key="verification_status",
    tools=[dapatkan_data_pasien]
)

create_appointment_patient_info_agent  = LlmAgent(
    name="CreateAppointmentPatientInfoAgent",
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
        2. Jika {verification_status} bernilai 'tidak terdaftar', minta pengguna untuk periksa kembali email/nomor telepon yang dimasukan.
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
    description="Workflow untuk mencarikan data pasien sebelum mereka bisa membuat janji temu mereka dengan dokter.",
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
        cari_jadwal_dokter,
        daftar_semua_dokter
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
    1. Untuk pasien lama, selalu minta email atau nomor telepon (format: 628xxxxxxxxx) agar dapat dicarikan datanya. \n
    2. Kemudian carikan data pasien terlebih dahulu menggunakan agen `create_apointment_patient_verification_workflow`.\n
    3. Apabila pengguna merupakan pasien baru arahkan untuk pendaftaran pasien baru menggunakan agen `create_apointment_new_patient_registration_agent`.
        - Apabila pendaftaran berhasil, arahkan kembali untuk untuk melakukan verifikasi pasien.\n
        - Apabila pendaftaran gagal, tawarkan untuk mengulang proses pendaftaran.\n
    4. Setelah verifikasi berhasil, pengguna bisa membuat janji temu dengan dokter menggunakan agen `create_appointment_agent`.\n
    5. Gunakan alat `daftar_semua_dokter` untuk mendapatkan daftar semua dokter yang tersedia.
    6. Ikuti aturan berikut sebelum mencari jadwal dokter:
        a.PENTING: Pastikan anda mengubah nama poli yang ditulis sesuai format resmi berikan, contoh yang benar dibawah.\n
        - Contoh salah: 'umum'\n
        - Contoh benar: 'Poli Umum'\n
        Gunakan kapitalisasi huruf awal setiap kata dan sertakan kata 'Poli'.\n
      b. PENTING: Pastikan anda hanya menggunakan nama belakang dokter. \n
        - Contoh: Nama Lengkap:'dr. Irina Syaefulloh, Sp.PD' menjadi Nama Belakang: 'Syaefulloh'.
""",
    sub_agents=[
        create_apointment_patient_verification_workflow,
        create_apointment_new_patient_registration_agent,
        create_appointment_agent
        ],
    tools=[
        cari_jadwal_dokter,
        daftar_semua_dokter
    ],
    generate_content_config=types.GenerateContentConfig(
        temperature=0.1
    )
)

