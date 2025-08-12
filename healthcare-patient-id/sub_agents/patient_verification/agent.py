from google.adk.agents import LlmAgent, SequentialAgent
from google.genai import types
from ...tools import cek_pasien_terdaftar, model_name, model_lite

patient_info_agent  = LlmAgent(
    name="PatientInfoAgent",
    model=model_lite,
    description="Agen yang menanyakan dan menampilkan informasi identitas pasien (Nama, Tanggal Lahir).",
    instruction=("""
        Tugas Anda adalah sebagai berikut:\n
        1. Tanyakan nama lengkap pasien dan tanggal lahir.
        2. Saat meminta tanggal lahir, tidak perlu format khusus dari pasien.
        3. Ubah input tanggal lahir dari pasien menjadi format ketat YYYY-MM-DD (contoh: '1985-05-20').
        4. Berikan respon seperti contoh di bawah ini:\n
               Melakukan verifikasi identitas. \n\n
               * Nama Depan:  \n
               * Nama Belakang:  \n
               * Tanggal Lahir: hari bulan tahun\n
        5. Jika nama belakang tidak ada atau kosong, jangan tampilkan baris nama belakang sama sekali.
    """),
    output_key="patient_info",
    generate_content_config=types.GenerateContentConfig(
        temperature=0.2
    ),
)

patient_verification_agent = LlmAgent(
    name="VerificationAgent",
    model=model_name,
    # model="gemini-2.5-pro",
    description="Agen yang bertugas untuk memverifikasi identitas pengguna.",
    instruction=("""
       Tugas Anda adalah memverifikasi data pasien sudah terdaftar apa belum sesuai alur berikut: \n
       1. Verifikasi identitas pengguna menggunakan nama lengkap dan tanggal lahir.\n
          - Jika tidak ada nama belakang, isi nama belakang dan nama tengah dengan null.\n
       2. Ubah input tanggal lahir dari pasien menjadi format ketat YYYY-MM-DD (contoh: '1985-05-20').\n
       3. Gunakan data tersebut untuk pengecekan data pasien menggunakan alat `cek_pasien_terdaftar`.\n
       4. Berdasarkan hasil dari pengecekan tersebut:\n
          a. Sampaikan respon dibawah ini jika pasien sudah terdaftar: \n
              - 'Terima kasih,**nama_lengkap_pasien**. **Anda sudah terverifikasi**.'\n
          b. Sampaikan respon dibawah ini jika pasien belum terdaftar: \n
              - '**Anda belum terdaftar**. Apakah Anda ingin melanjutkan ke proses pendaftaran pasien baru?'\n
    """),
    tools=[cek_pasien_terdaftar],
    generate_content_config=types.GenerateContentConfig(
        temperature=0.1
    ),
    output_key="patient_verification_status",
)

# patient_verification_workflow = SequentialAgent(
#     name="PatientVerificationWorkflow",
#     sub_agents=[patient_info_agent, patient_verification_agent],
#     description="Workflow untuk memverifikasi identitas pasien dan menampilkan informasi mereka.",
# )
