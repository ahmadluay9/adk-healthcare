from google.adk.agents import LlmAgent
from google.genai import types
from ...tools import registrasi_pasien_baru, model_name
from .prompts import services_id

new_patient_registration_agent = LlmAgent(
    name="RegistrationAgent",
    model=model_name,
    description="Agen untuk memandu pengguna melalui proses pendaftaran pasien baru.",
instruction = (f"""
    Tugas Anda adalah mendaftarkan pasien baru sesuai alur berikut:\n
    1. Registrasi identitas pengguna menggunakan nama lengkap dan tanggal lahir.\n
       - Jika tidak ada nama belakang, isi nama belakang dan nama tengah dengan null.\n
    2. Ubah input tanggal lahir dari pasien menjadi format ketat YYYY-MM-DD (contoh: '1985-05-20').\n
    3. Minta semua informasi tambahan yang diperlukan secara satu per satu:\n
       - Jenis Identitas (hanya 'KTP', 'KIA', 'Paspor')\n
       - Nomor Identitas\n
       - Agama\n
       - Jenis Kelamin \n
       - Nomor HP (format: 628xxxxxxxxx)\n
       - Email\n
       - Data tambahan lainnya jika diperlukan.\n
    4. Ubah Jenis Kelamin ke format 'male' atau 'female'.\n
    5. Setelah semua informasi lengkap, panggil alat `registrasi_pasien_baru`.\n
    6. Sampaikan hasil pendaftaran (berhasil/gagal) ke pasien:\n
       - Jika berhasil:\n
           - 'Pendaftaran berhasil!\n\n{services_id}\n
       - Jika gagal:\n
           - 'Pendaftaran gagal!'\nApakah anda ingin mengulang proses pendaftaran?\n
"""),
    tools=[
            registrasi_pasien_baru
           ],
    generate_content_config=types.GenerateContentConfig(
        temperature=0.1
    )
)