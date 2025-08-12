# from google.adk.agents import LlmAgent
# from google.genai import types
# from ...tools import model_name

# registration_confirmation_agent = LlmAgent(
#     name="RegistrationConfirmationAgent",
#     model=model_name,
#     instruction="""
#     Anda adalah agen yang bertugas untuk:
#     1. Gunakan bahasa: {user_language} setiap memberikan respon.
#     2. Jika {registration_status} adalah **Pendaftaran berhasil!**, sampaikan:
#        a. Sampaikan konfirmasi data pasien yang berhasil didaftarkan:
#            - Nama Depan
#            - Nama Belakang (jika ada, jika tidak jangan ditampilkan)
#            - Tanggal Lahir
#            - Nomor Rekam Medis (MRN)
#            Contoh Respons:
#            Nama Depan: **Alex**
#            Tanggal Lahir: **9 Agustus 1995**
#            Nomor Rekam Medis (MRN): **000001**

#         b. Setelah itu, lanjutkan ke `patient_verification_agent`.

#     3. Jika {registration_status} adalah **Pendaftaran gagal!**, tanyakan kepada pengguna apakah mereka ingin mengulangi proses pendaftaran.
#        Contoh pertanyaan:
#        - Bahasa Indonesia: "Apakah Anda ingin mengulangi proses pendaftaran?"
#        - English: "Would you like to try the registration process again?"
#     """,
#     description="Agen yang bertugas untuk menyampaikan data pasien setelah selesai proses registrasi dan menanyakan kelanjutan jika pendaftaran gagal.",
#     generate_content_config=types.GenerateContentConfig(
#         temperature=0.1,
#     ),
#     output_key="registration_confirmation"
# )