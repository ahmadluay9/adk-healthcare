from google.adk.agents import LlmAgent, SequentialAgent
from google.genai import types
from ...tools import registrasi_pasien_baru, cek_pasien_terdaftar, model_name

patient_info_display_agent  = LlmAgent(
    name="PatientInfoDisplayAgent",
    model=model_name,
    description="Agen yang menampilkan informasi pasien (Nama, Tanggal Lahir, MRN) yang sudah terverifikasi.",
    instruction=(
        # "Gunakan bahasa: {user_language} setiap memberikan respon.\n"
        "Anda adalah agen untuk menampilkan informasi nama dan tanggal lahir pasien. "
        "Tugas Anda adalah sebagai berikut:\n"
        "1. Apabila bahasa yang digunakan 'Bahasa Indonesia', berikan respon seperti di bawah ini:\n"
        "       * Nama Depan: Charles \n"
        "       * Nama Belakang: Watts \n"
        "       * Tanggal Lahir: 9 September 1999\n"
        "2. If the language used is 'English', provide a response as shown below:\n"
        "       * First Name: Charles \n"
        "       * Last Name: Watts \n"
        "       * Date of Birth: September 9, 1999\n"
        "3. Jika nama belakang tidak ada atau kosong, jangan tampilkan baris nama belakang sama sekali."
    ),
    output_key="patient_name_dob",
    generate_content_config=types.GenerateContentConfig(
        temperature=0.2
    )
)

new_patient_verification_agent = LlmAgent(
    name="NewPatientVerificationAgent",
    model=model_name,
    description="Agen untuk memverifikasi data pasien baru sudah terdaftar apa belum.",
    instruction=(
    "Tugas Anda adalah memverifkasi data pasien sudah terdaftar apa belum sesuai alur berikut: \n"
    "0. Gunakan bahasa: {user_language} setiap memberikan respon. \n"
    "1. Gunakan informasi dari {patient_name_dob} untuk memverifikasi identitas pengguna.\n"
    "   - Jika tidak ada nama belakang, isi nama belakang dan nama tengah dengan null.\n"
    "   - Saat meminta tanggal lahir, tidak perlu format khusus dari pasien.\n"
    "2. Ubah input tanggal lahir dari pasien menjadi format ketat YYYY-MM-DD (contoh: '1985-05-20').\n"
    "3. Panggil alat `cek_pasien_terdaftar` dengan data tersebut.\n"
    "4. Berdasarkan hasil dari `cek_pasien_terdaftar`:\n"
    "   a. Sampaikan respon dibawah ini jika pasien sudah terdaftar: \n"
    "      - Bahasa Indonesia: 'Terima kasih. **Anda sudah terdaftar**. Apakah Anda ingin melanjutkan ke proses verifikasi identitas pasien?' \n"
    "      - English: 'Thank you. **You are already registered**. Would you like to proceed to patient identity verification?' \n"
    "   b. Sampaikan respon dibawah ini jika pasien belum terdaftar: \n"
    "      - Bahasa Indonesia: 'Terima kasih. **Anda belum terdaftar**. Apakah Anda ingin melanjutkan ke proses registrasi pasien baru?'\n"
    "      - English: 'Thank you. **You are not yet registered**. Would you like to proceed to new patient registration?'\n"
    "5. Jika pasien setuju, lanjutkan ke agen yang sesuai (`patient_verification_agent` atau `new_patient_registration_agent`)."
),
    tools=[
            cek_pasien_terdaftar
           ],
    generate_content_config=types.GenerateContentConfig(
        temperature=0.1
    )
)

new_patient_verification_workflow = SequentialAgent(
    name="NewPatientVerificationWorkflow",
    description="Memverifikasi data pasien baru.",
    sub_agents=[
        patient_info_display_agent,
        new_patient_verification_agent
    ]
)

# "Gunakan bahasa: {user_language} setiap memberikan respon. \n"
# "Anda adalah agen verifikasi identitas pengguna. Tugas Anda adalah sebagai berikut:\n"
# "1. Gunakan informasi dari {patient_name_dob} untuk memverifikasi identitas pengguna.\n"
# "2. PENTING: Sebelum memanggil alat, Anda WAJIB mengubah input tanggal lahir dari pengguna (misalnya '20 Mei 1985', '20/05/1985', dll.) menjadi format YYYY-MM-DD yang ketat (contoh: '1985-05-20').\n"
# "3. Panggil alat `cek_pasien_terdaftar` dengan data yang telah Anda format ulang.\n"
# "4. Jika {patient_status} adalah 'Pasien Lama dipilih' atau 'Existing Patient selected', dan verifikasi gagal karena data tidak ditemukan atau duplikat, minta Nomor Rekam Medis (MRN) dan Tanggal Lahir sebagai verifikasi cadangan, lalu panggil kembali alat `cek_pasien_terdaftar` (pastikan format tanggal lahir tetap YYYY-MM-DD).\n"
# "5. Setelah verifikasi berhasil, sampaikan pesan konfirmasi keberhasilan seperi contoh dibawah ini: "
# "   a. Berikan respon seperti dibawah ini: \n"
# "   - Bahasa Indonesia: 'Verifikasi berhasil!'"
# "   - English: 'Verification successful!'"
# "   b. Lanjutkan ke agen `existing_patient_service_workflow`. \n"
# "6. Jika {patient_status} adalah 'Pasien Baru dipilih' atau 'New Patient selected' dan verifikasi gagal karena data tidak ditemukan: \n"
# "   a. Berikan respon seperti dibawah ini: \n"
# "   - Bahasa Indonesia: 'Terima kasih. Anda belum terdaftar.'"
# "   - English: 'Thank you. You are not yet registered.'"
# "   b. Lanjutkan ke agen `new_patient_registration_agent`. \n"

# fu_patient_registration_status_agent = LlmAgent(
#     name="PatientRegistrationStatusAgent",
#     model="gemini-2.5-flash-lite",
#     instruction="""  
#     Anda adalah agen yang bertugas untuk:
#     1. Gunakan bahasa: {user_language} setiap memberikan respon.
#     2. Sampaikan respon dibawah ini jika {new_patient_verification_status} adalah 'Terima kasih. **Anda sudah terdaftar**.' atau 'Thank you. **You are already registered**.':
#         - Bahasa Indonesia: "Nomor Rekam Medis (MRN): 00011100."
#         - English: "Medical Record Number (MRN): 00011100."
#     3. Sampaikan respon dibawah ini jika {new_patient_verification_status} adalah ''Terima kasih. **Anda belum terdaftar**.' atau 'Thank you. **You are not yet registered**.':
#         - Bahasa Indonesia: "Saya akan melanjutkan ke proses pendaftaran pasien baru."
#         - English: "I will proceed to the new patient registration process."
#     4. Setelah itu, lanjutkan ke agen `new_patient_registration_agent` untuk proses pendaftaran pasien baru jika belum terdaftar.
#     """,
#     description="Agen untuk Menentukan tindak lanjut setelah verifikasi pasien baru, memberi MRN jika sudah terdaftar atau melanjutkan pendaftaran jika belum.",
#     generate_content_config=types.GenerateContentConfig(
#         temperature=0.1
#     ),
# )

# new_patient_verification_workflow = SequentialAgent(
#     name="NewPatientVerificationWorkflow",
#     description="Mengonfirmasi pemilihan status pasien dan mengarahkan ke langkah selanjutnya.",
#     sub_agents=[
#         new_patient_verification_agent,
#         fu_patient_registration_status_agent
#     ]
# )

# # new_patient_registration_agent = LlmAgent(
# #     name="RegistrationAgent",
# #     model=model_name,
# #     description="Agen untuk memandu pengguna melalui proses pendaftaran pasien baru.",
# # instruction = (
# #     "Tugas Anda adalah mendaftarkan pasien baru sesuai alur berikut:\n"
# #     "0. Gunakan bahasa: {user_language} setiap memberikan respon. \n"
# #     "1. Tanyakan **Nama Depan**, **Nama Belakang** (jika ada), dan **Tanggal Lahir** pasien untuk memeriksa apakah sudah terdaftar.\n"
# #     "   - Jika tidak ada nama belakang, isi nama belakang dan nama tengah dengan null.\n"
# #     "   - Saat meminta tanggal lahir, tidak perlu format khusus dari pasien.\n"
# #     "2. Ubah input tanggal lahir dari pasien menjadi format ketat YYYY-MM-DD (contoh: '1985-05-20').\n"
# #     "3. Panggil alat `cek_pasien_terdaftar` dengan data tersebut.\n"
# #     "4. Berdasarkan hasil dari `cek_pasien_terdaftar`:\n"
# #     "   a. Jika pasien sudah terdaftar: sampaikan informasi tersebut (termasuk MRN jika ada), lalu minta pasien mengetik **VERIFIKASI** dan hentikan proses.\n"
# #     "   b. Jika pasien belum terdaftar: lanjutkan ke langkah pendaftaran.\n"
# #     "5. Minta semua informasi tambahan yang diperlukan:\n"
# #     "   - Jenis Identitas (hanya 'KTP', 'KIA', 'Paspor/Passport')\n"
# #     "   - Nomor Identitas\n"
# #     "   - Agama\n"
# #     "   - Jenis Kelamin (ubah ke format 'male' atau 'female')\n"
# #     "   - Nomor HP (format: 628xxxxxxxxx)\n"
# #     "   - Data tambahan lainnya jika diperlukan.\n"
# #     "6. Setelah semua informasi lengkap, panggil alat `registrasi_pasien_baru`.\n"
# #     "7. Sampaikan hasil pendaftaran (berhasil/gagal) ke pasien.\n"
# #     "   - Jika berhasil: 'Pendaftaran berhasil!' (Bahasa Indonesia) atau 'Registration successful!' (English)\n"
# #     "   - Jika gagal: 'Pendaftaran gagal!' (Bahasa Indonesia) atau 'Registration failed!' (English)\n"
# #     "8. Kemudian lanjutkan ke `registration_confirmation_agent`."
# # ),
# #     tools=[
# #             cek_pasien_terdaftar
# #            ],
# #     output_key="registration_status",
# #     generate_content_config=types.GenerateContentConfig(
# #         temperature=0.1
# #     )
# # )

# # ask_patient_registration_agent = LlmAgent(
# #     name="AskPatientRegistrationAgent",
# #     model="gemini-2.5-flash-lite",
# #     instruction="""  
# #     Anda adalah agen yang bertugas untuk:
# #     1. Gunakan bahasa: {user_language} setiap memberikan respon.
# #     2. Jika {registration_status} adalah **Pendaftaran berhasil!**:
# #          - Respon Anda:: "Apakah Anda ingin mendaftar sebagai pasien baru?"
# #     3. Jika {registration_status} adalah **Pasien Lama**:
# #          - Respon Anda:: "Apakah Anda ingin melanjutkan proses verifikasi identitas?"
# #     """,
# #     description="",
# #     generate_content_config=types.GenerateContentConfig(
# #         temperature=0.1
# #     ),
# #     output_key="ask_patient_registration_response"
# # )

# # new_patient_registration_workflow = SequentialAgent(
# #     name="NewPatientRegistrationWorkflow",
# #     description="Mengonfirmasi pemilihan status pasien dan mengarahkan ke langkah selanjutnya.",
# #     sub_agents=[
# #         new_patient_registration_agent,
# #         ask_patient_registration_agent
# #     ]
# # )

# # ask_patient_confirmation_agent
# # registration_confirmation_agent = LlmAgent(
# #     name="RegistrationConfirmationAgent",
# #     model=model_name,
# #     instruction="""
# #     Anda adalah agen yang bertugas untuk:
# #     1. Gunakan bahasa: {user_language} setiap memberikan respon.
# #     2. Jika {registration_status} adalah **Pendaftaran berhasil!**, sampaikan:
# #        a. Sampaikan konfirmasi data pasien yang berhasil didaftarkan:
# #            - Nama Depan
# #            - Nama Belakang (jika ada, jika tidak jangan ditampilkan)
# #            - Tanggal Lahir
# #            - Nomor Rekam Medis (MRN)
# #            Contoh:
# #            Nama Depan: **Alex**
# #            Tanggal Lahir: **9 Agustus 1995**
# #            Nomor Rekam Medis (MRN): **000001**

# #         b. Setelah itu, tawarkan untuk melanjutkan ke proses verifikasi identitas.
# #            Contoh pertanyaan:
# #            - Bahasa Indonesia: "Apakah Anda ingin melanjutkan ke proses verifikasi identitas?"
# #            - English: "Would you like to proceed to the identity verification process?"

# #     3. Jika {registration_status} adalah **Pendaftaran gagal!**, tanyakan kepada pengguna apakah mereka ingin mengulangi proses pendaftaran.
# #        Contoh pertanyaan:
# #        - Bahasa Indonesia: "Apakah Anda ingin mengulangi proses pendaftaran?"
# #        - English: "Would you like to try the registration process again?"
# #     """,
# #     description="Agen yang bertugas untuk menyampaikan data pasien setelah selesai proses registrasi dan menanyakan kelanjutan jika pendaftaran gagal.",
# #     generate_content_config=types.GenerateContentConfig(
# #         temperature=0.1,
# #     output_key="registration_confirmation"
# #     )
# # )

# # registration_verification_agent = LlmAgent(
# #     name="RegistrationVerificationAgent",
# #     model=model_name,
# #     instruction="""  
# #     Anda adalah agen yang bertugas untuk:
# #     1. Gunakan bahasa: {user_language} setiap memberikan respon.
# #     2. Jika {registration_status} adalah **Pendaftaran berhasil!**, tawarkan kepada pengguna apakah ingin melanjutkan ke proses verifikasi identitas.
# #         Contoh pertanyaan:
# #         - Bahasa Indonesia: "Apakah Anda ingin melanjutkan ke proses verifikasi identitas?"
# #         - English: "Would you like to proceed to the identity verification process?"
# #     3. Jika {registration_status} adalah **Pendaftaran gagal!**, tanyakan kepada pengguna apakah mereka ingin mengulangi proses pendaftaran.
# #         Contoh pertanyaan:
# #         - Bahasa Indonesia: "Apakah Anda ingin mengulangi proses pendaftaran?"
# #         - English: "Would you like to try the registration process again?"
# #     """,
# #     description="Agen yang bertugas untuk menyampaikan data pasien setelah selesai proses registrasi.",
# #     generate_content_config=types.GenerateContentConfig(
# #         temperature=0.1
# #     )
# # )

# # patient_registration_workflow = SequentialAgent(
# #     name="PatientRegistrationWorkflow",
# #     description="Memandu pengguna baru melalui proses pendaftaran.",
# #     sub_agents=[
# #         new_patient_registration_agent,
# #         registration_confirmation_agent,
# #         # registration_verification_agent
# #     ]
# # )

    
# # post_registration_agent = LlmAgent(
# #     name="PostRegistrationAgent",
# #     model= "gemini-2.5-flash-lite",
# #     instruction="""
# #     Anda adalah agen bertugas sebagai berikut:
# #     1. Gunakan selalu Gunakan bahasa: {user_language} setiap memberikan respon. yang dipilih pengguna.
# #     2. Bila Pendaftaran berhasil tanyakan apakah pengguna mau melanjutkan ke proses verifikasi identitas atau tidak.
# #     """,
# #     description="Agen ini menangani komunikasi setelah pendaftaran pasien berhasil, termasuk menyampaikan keberhasilan pendaftaran dan menawarkan proses verifikasi identitas.",
# #     generate_content_config=types.GenerateContentConfig(
# #         temperature=0.1
# #     ),
# # )

# # new_patient_registration_agent = SequentialAgent(
# #     name="NewPatientRegistrationAgent",
# #     sub_agents=[registration_agent, post_registration_agent],
# #     description="Agen yang menangani pendaftaran pasien baru."
# # )