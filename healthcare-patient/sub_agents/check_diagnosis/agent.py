from google.adk.agents import LlmAgent, SequentialAgent
from google.genai import types
from ...tools import cek_diagnosis_terakhir, cek_program_asuransi, model_name

# --- Definisi Sub-Agen Cek Diagnosis ---
check_diagnosis_agent = LlmAgent(
    name="CheckDiagnosisAgent",
    model=model_name,
    description="Agen untuk memeriksa diagnosis terakhir pasien dari riwayat kunjungan mereka.",
    instruction=(
        "Gunakan bahasa: {user_language} setiap memberikan respon.\n"
        "Tugas Anda adalah membantu pasien memeriksa diagnosis terakhir mereka.\n"
        "1. Verifikasi identitas pasien.\n"
        "2. Panggil alat `cek_diagnosis_terakhir` dengan data yang sesuai."
        "Contoh Jawaban: 'Berdasarkan kunjungan terakhir Anda, diagnosis yang tercatat adalah: **Infeksi Saluran Pernapasan Akut (ISPA)**.'"
    ),
    tools=[cek_diagnosis_terakhir],
    output_key="patient_diagnosis",
    generate_content_config=types.GenerateContentConfig(
        temperature=0.1
    )
)

# Definisi Sub-Agen Cek Program Asuransi
check_insurance_program_agent = LlmAgent(
    name="CheckInsuranceProgramAgent",
    model=model_name,
    description="Agen untuk memeriksa manfaat asuransi pasien dan, jika relevan, menawarkan untuk memeriksa cakupan diagnosis.",
    instruction=(
        "Gunakan bahasa: {user_language} setiap memberikan respon.\n"
        "Tugas Anda adalah membantu pasien memeriksa program asuransi mereka.\n"
        "1. Verifikasi identitas pasien.\n"
        "2. Panggil alat `cek_program_asuransi` dengan data yang sesuai."
        "Contoh Jawaban: 'Berdasarkan data yang kami miliki, Anda terdaftar dalam program : **Asuransi A**.'"
        "3. Apabila pasien termasuk dalam program 'BPJS Kesehatan', tawarkan ke pasien untuk mengecek apakah penyakit mereka tercakup dalam program."
    ),
    tools=[cek_program_asuransi],
    output_key="insurance_program",
    generate_content_config=types.GenerateContentConfig(
        temperature=0.1
    )
)

# Definisi Agen Diagnosis
diagnosis_agent = SequentialAgent(
    name="DiagnosisAgent",
    sub_agents=[check_diagnosis_agent, check_insurance_program_agent],
    description="Agen yang bertanggung jawab untuk memeriksa diagnosis pasien dan program asuransi yang relevan."
)




