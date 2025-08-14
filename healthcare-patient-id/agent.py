import os
from google.adk.agents import Agent
from dotenv import load_dotenv

# Sub-Agen yang diimpor
# from .sub_agents.greeting.agent import greeting_workflow
# from .sub_agents.language_selection.agent import language_selection_workflow
# from .sub_agents.patient_status.agent import patient_status_agent
# from .sub_agents.patient_status_confirmation.agent import patient_status_workflow
# from .sub_agents.ask_patient_status.agent import ask_patient_status_agent
# from .sub_agents.patient_status_confirmation.agent import patient_status_confirmation_agent
# from .sub_agents.new_patient_verification.agent import new_patient_verification_workflow
from .sub_agents.new_patient_registration.agent import new_patient_registration_agent
from .sub_agents.patient_verification.agent import verification_agent
# from .sub_agents.existing_patient_service.agent import existing_patient_service_workflow
# from .sub_agents.ask_fullname_dob.agent import ask_fullname_dob_agent
# from .sub_agents.new_patient_verification.agent import new_patient_verification_workflow
# from .sub_agents.registration_confirmation.agent import registration_confirmation_agent
# from .sub_agents.general_search.agent import search_agent
# from .sub_agents.create_appointment.agent import doctor_search_tool
from .sub_agents.general_search.agent import general_search_tool
from .sub_agents.medical_advice.agent import medical_advice_agent
from .sub_agents.check_upcoming_appointments.agent import check_appointment_agent
from .sub_agents.create_appointment.agent import create_appointment_agent
# from .sub_agents.check_insurance_benefits.agent import check_benefits_agent
# from .sub_agents.check_claim_status.agent import check_claim_agent
# from .sub_agents.check_diagnosis.agent import check_diagnosis_agent
# from .sub_agents.bpjs_check.agent import bpjs_check_agent

from .tools import model_name, model_pro, model_lite, dapatkan_waktu_sekarang, dapatkan_tanggal_hari_ini
from .prompts import promp_instruction, promp_instruction_v1, promp_instruction_v2, promp_instruction_v4, promp_instruction_v4

# --- Konfigurasi Lingkungan ---
load_dotenv()
os.environ['GOOGLE_CLOUD_PROJECT'] = os.getenv('GOOGLE_CLOUD_PROJECT')
os.environ['GOOGLE_CLOUD_LOCATION'] = os.getenv('GOOGLE_CLOUD_LOCATION')
os.environ["GOOGLE_GENAI_USE_VERTEXAI"] = os.getenv('GOOGLE_GENAI_USE_VERTEXAI')

# --- Definisi Agen Utama (Router Agent) ---
root_agent = Agent(
    name="root_agent",
    model= model_pro,
    description="Agen utama yang berfungsi sebagai router untuk mendelegasikan tugas ke sub-agen yang sesuai.",
    instruction = promp_instruction_v4,
    sub_agents=[
        # greeting_workflow,
        # language_selection_workflow,
        # patient_status_agent,
        # ask_patient_status_agent,
        # patient_status_confirmation_agent,
        # patient_status_workflow,
        # ask_fullname_dob_agent,
        verification_agent,
        # existing_patient_service_workflow,
        # new_patient_verification_workflow,
        # new_patient_verification_workflow,
        new_patient_registration_agent,
        # registration_confirmation_agent,
        # search_agent,
        # hospital_doctor_search_agent,
        # medical_advice_agent,
        # check_appointment_agent,
        # create_appointment_agent,
        # check_benefits_agent,
        # check_claim_agent,
        # check_diagnosis_agent,
        # bpjs_check_agent
    ],
    tools=[
        general_search_tool,
        dapatkan_waktu_sekarang,
        dapatkan_tanggal_hari_ini
        ]
)