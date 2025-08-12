from google.adk.agents import LlmAgent, SequentialAgent
from google.genai import types
from ...tools import dapatkan_mrn_pasien, cek_pasien_terdaftar, model_name
from .prompts import services_id, services_en

patient_info_display_agent  = LlmAgent(
    name="PatientInfoDisplayAgent",
    model=model_name,
    description="Agen yang menampilkan informasi pasien (Nama, Tanggal Lahir, MRN) yang sudah terverifikasi.",
    instruction=(
        "Gunakan bahasa: {user_language} setiap memberikan respon.\n"
        # "Anda adalah agen untuk menampilkan informasi nama , tanggal lahir dan MRN pasien. "
        "Tugas Anda adalah sebagai berikut:\n"
        "Ubah input tanggal lahir dari pasien menjadi format ketat YYYY-MM-DD (contoh: '1985-05-20')."
        "Gunakan alat `dapatkan_mrn_pasien` untuk mendapatkan MRN pasien.\n"
        "1. Apabila bahasa yang digunakan 'Bahasa Indonesia', berikan respon seperti contoh di bawah ini:\n"
        "       Melakukan verifikasi identitas. \n\n"
        "       * Nama Depan:  \n"
        "       * Nama Belakang:  \n"
        "       * Tanggal Lahir: hari bulan tahun\n"
        "       * MRN: "
        "2. If the language used is 'English', provide a response like the example below:\n"
        "       Verifying identity. \n\n"
        "       * First Name: \n"
        "       * Last Name: \n"
        "       * Date of Birth: month date, year\n"
        "       * MRN: "
        "3. Jika nama belakang tidak ada atau kosong, jangan tampilkan baris nama belakang sama sekali."
    ),
    output_key="patient_name_dob",
    generate_content_config=types.GenerateContentConfig(
        temperature=0.2
    ),
    tools=[dapatkan_mrn_pasien]
)

patient_verification_agent = LlmAgent(
    name="VerificationAgent",
    model="gemini-2.5-pro",
    description="Agen yang bertugas untuk memverifikasi identitas pengguna.",
    instruction=(
        "Tugas Anda adalah memverifkasi data pasien sudah terdaftar apa belum sesuai alur berikut: \n"
        "0. Gunakan bahasa: {user_language} setiap memberikan respon. \n"
        "1. Gunakan informasi dari {patient_name_dob} untuk memverifikasi identitas pengguna.\n"
        "   - Jika tidak ada nama belakang, isi nama belakang dan nama tengah dengan null.\n"
        "   - Saat meminta tanggal lahir, tidak perlu format khusus dari pasien.\n"
        "2. Ubah input tanggal lahir dari pasien menjadi format ketat YYYY-MM-DD (contoh: '1985-05-20').\n"
        "3. Gunakan data tersebut untuk pengecekan data pasien menggunakan alat `cek_pasien_terdaftar`.\n"
        "4. Berdasarkan hasil dari pengecekan tersebut:\n"
        "   a. Sampaikan respon dibawah ini jika pasien sudah terdaftar: \n"
        f"      - Bahasa Indonesia: 'Terima kasih. **Anda sudah terverifikasi**.\n\n{services_id}'\n"
        f"      - English: 'Thank you. **You are already verified**.\n\n{services_en}'\n"
        "   b. Sampaikan respon dibawah ini jika pasien belum terdaftar: \n"
        "      - Bahasa Indonesia: 'Terima kasih. **Anda belum terdaftar**. Apakah Anda ingin melanjutkan ke proses pendaftaran pasien baru?'\n"
        "      - English: 'Thank you. **You are not yet registered**. Would you like to proceed to new patient registration?'\n"
        "5. Jika pasien setuju, lanjutkan ke agen yang sesuai `new_patient_registration_agent`."
    ),
    tools=[cek_pasien_terdaftar],
    generate_content_config=types.GenerateContentConfig(
        temperature=0.1
    )
)

patient_verification_workflow = SequentialAgent(
    name="PatientVerificationWorkflow",
    sub_agents=[patient_info_display_agent, patient_verification_agent],
    description="Workflow untuk memverifikasi identitas pasien dan menampilkan informasi mereka.",
)
