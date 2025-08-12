from google.adk.agents import LlmAgent, SequentialAgent
from google.genai import types
from ...tools import cek_pasien_terdaftar, model_name, model_lite

patient_info_display_agent  = LlmAgent(
    name="PatientInfoDisplayAgent",
    model=model_lite,
    description="Agen yang menampilkan informasi pasien (Nama, Tanggal Lahir).",
    instruction=(
        # "Gunakan bahasa: {user_language} setiap memberikan respon.\n"
        "Anda adalah agen untuk menampilkan informasi nama dan tanggal lahir pasien. "
        "Tugas Anda adalah sebagai berikut:\n"
        "1. Apabila bahasa yang digunakan 'Bahasa Indonesia', berikan respon seperti di bawah ini:\n"
        "       Melakukan pengecekan status pendaftaran. \n\n"
        "       * Nama Depan: \n"
        "       * Nama Belakang:  \n"
        "       * Tanggal Lahir: Hari Bulan Tahun\n"
        "2. If the language used is 'English', provide a response as shown below:\n"
        "       Verifying registration status.\n\n"
        "       * First Name: \n"
        "       * Last Name:  \n"
        "       * Date of Birth: Month Date, Year\n"
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
    description="Agen untuk melakukan pengecekan data pasien baru apakah sudah terdaftar apa belum.",
    instruction=(
    "Tugas Anda adalah memverifkasi data pasien sudah terdaftar apa belum sesuai alur berikut: \n"
    "0. Gunakan bahasa: {user_language} setiap memberikan respon. \n"
    "1. Gunakan informasi dari {patient_name_dob} untuk pengecekan status pendaftaran pasien.\n"
    "   - Jika tidak ada nama belakang, isi nama belakang dan nama tengah dengan null.\n"
    "   - Saat meminta tanggal lahir, tidak perlu format khusus dari pasien.\n"
    "2. Ubah input tanggal lahir dari pasien menjadi format ketat YYYY-MM-DD (contoh: '1985-05-20').\n"
    "3. Panggil alat `cek_pasien_terdaftar` dengan data tersebut.\n"
    "4. Berdasarkan hasil dari `cek_pasien_terdaftar`:\n"
    "   a. Sampaikan respon dibawah ini jika pasien sudah terdaftar: \n"
    "      - Bahasa Indonesia: 'Terima kasih. **Anda sudah terdaftar**. Apakah Anda ingin melanjutkan ke proses verifikasi identitas pasien?' \n"
    "      - English: 'Thank you. **You are already registered**. Would you like to proceed to patient identity verification?' \n"
    "   b. Sampaikan respon dibawah ini jika pasien belum terdaftar: \n"
    "      - Bahasa Indonesia: 'Terima kasih. **Anda belum terdaftar**. Apakah Anda ingin melanjutkan ke proses pendaftaran pasien baru?'\n"
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
    description="Melakukan pengecekan status pendaftaran pasien baru.",
    sub_agents=[
        patient_info_display_agent,
        new_patient_verification_agent
    ]
)
