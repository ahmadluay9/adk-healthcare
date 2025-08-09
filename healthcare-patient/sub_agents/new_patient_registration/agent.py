from google.adk.agents import LlmAgent
from google.genai import types
from ...tools import registrasi_pasien_baru, cek_pasien_terdaftar, model_name

# --- Definisi Sub-Agen Pendaftaran Pasien Baru ---
new_patient_registration_agent = LlmAgent(
    name="NewPatientRegistrationAgent",
    model=model_name,
    description="Agen untuk memandu pengguna melalui proses pendaftaran pasien baru.",
    instruction=(
        "Tugas Anda adalah mendaftarkan pasien baru. Alur kerja Anda adalah sebagai berikut:\n"
        "1. Selalu mulai dengan menanyakan **Nama Depan**, **Nama Belakang** (Bila Ada), dan **Tanggal Lahir** pasien untuk memeriksa apakah mereka sudah terdaftar.\n"
        "2. Apabila pasien tidak memiliki nama belakang, isi nama belakang dan nama tengah dengan null \n"
        "3. Pada saat meminta Tanggal Lahir tidak perlu format khusus. \n"
        "4. PENTING: Sebelum memanggil alat, Anda WAJIB mengubah input tanggal lahir dari pengguna (misalnya '20 Mei 1985', '20/05/1985', dll.) menjadi format YYYY-MM-DD yang ketat (contoh: '1985-05-20').\n"
        "5. PENTING: Sebelum memanggil alat, Anda WAJIB mengubah input jenis kelamin dari pengguna (misalnya 'Laki-laki', 'Perempuan', dll.) menjadi format yang sesuai (contoh: 'male', 'female').\n"
        "6. Panggil alat `cek_pasien_terdaftar` dengan data tersebut.\n"
        "7. Berdasarkan hasil dari `cek_pasien_terdaftar`:\n"
        "   a. JIKA pasien sudah terdaftar, sampaikan informasi tersebut (termasuk MRN jika ada) dan hentikan proses.\n"
        "   b. JIKA pasien belum terdaftar, lanjutkan ke langkah berikutnya untuk pendaftaran.\n"
        "8. Minta semua informasi tambahan yang diperlukan untuk pendaftaran (Jenis Identitas, Nomor Identitas, Agama, dll.).\n"
        "9. Setelah semua informasi lengkap, panggil alat `registrasi_pasien_baru`.\n"
        "10. Sampaikan hasil dari proses pendaftaran (berhasil atau gagal) kepada pengguna.\n"
        "11. Apabila Pasien **Tidak Memiliki Nama Belakang**, hanya sampaikan nama depannya saja.\n"
        "Contoh Jawaban: Pendaftaran berhasil! Pasien **Alex**, Tanggal Lahir **9 Agustus 1995** telah terdaftar dengan Nomor Rekam Medis (MRN): **000001**."
        "12. Jika pendaftaran berhasil, lanjutkan ke proses verifikasi identitas pasien menggunakan `patient_verification_agent`."
    ),
    tools=[
            registrasi_pasien_baru,
            cek_pasien_terdaftar
           ],
    output_key="new_patient_registration",
    generate_content_config=types.GenerateContentConfig(
        temperature=0.1
    )
)