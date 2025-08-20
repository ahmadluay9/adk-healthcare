# Virtual Clinical Assistant Project (Healthcare Agent)
Welcome to the Virtual Clinical Assistant project! This is a sophisticated chatbot application designed to streamline interactions between patients and healthcare providers. Built with Google's **Agent Development Kit (ADK)**, this project leverages a multi-agent architecture to handle a wide range of tasks, from new patient registration to providing general medical advice.

✨ Key Features
- **Multi-Agent Architecture**: Utilizes a primary "router" agent to delegate tasks to specialized sub-agents, creating a modular and organized workflow.

- **New Patient Registration**: Guides users through a complete registration process, with validation to prevent duplicate data entries.

- **Appointment Management**: Allows patients to book new appointments, check upcoming schedules, and receive queue numbers.

- **Insurance Services**: Enables patients to check their insurance benefits and the status of their claims.

- **Medical Records**: Patients can retrieve their latest diagnosis from their visit history.

- **Medical Advice & Doctor Search**: Provides general medical advice for non-emergency symptoms and recommends relevant specialists within the hospital.

- **FHIR Integration**: Connects directly to the **Google Cloud Healthcare API** for secure and standardized patient data management.

- **Interactive Frontend**: A clean, modern chatbot interface served directly by the FastAPI backend.

📂 Project Structure
```
adk-healthcare/
├── README.md
├── .gitignore
├── cloudbuild.yaml
├── Dockerfile
├── main.py
├── healthcare-patient-id/
│   ├── sub_agents/
│   │   ├── general_search/
│   │   │   ├── __init.py__
│   │   │   └── agent.py 
│   │   ├── medical_advice/
│   │   │   ├── __init.py__
│   │   │   └── agent.py 
│   │   ├── check_upcoming_appointments/
│   │   │   ├── __init.py__
│   │   │   ├── agent.py
│   │   │   └── prompts.py 
│   │   ├── create_appointment/
│   │   │   ├── __init.py__
│   │   │   ├── agent.py
│   │   │   └── prompts.py 
│   │   ├── new_patient_registration/
│   │   │   ├── __init.py__
│   │   │   └── agent.py 
│   │   │   └── prompts.py 
│   ├── .env
│   ├── agent.py
│   ├── prompts.py
│   └── tools.py 
├── requirements.txt
├── templates/
│   ├── chatbot.html
│   ├── chatbot-raw.html
└── └── index.html 
```

- `healthcare-patient-id/`: The core directory containing all agent logic.

    - `sub_agents/`: Each subdirectory here contains a single sub-agent with a specific task (e.g., create_appointment).

    - `agent.py`: Defines the root_agent which acts as the central orchestrator or router.

    - `tools.py`: Contains all Python functions that interact with external services, like the FHIR API.

- `main.py`: The entry point for the FastAPI application. It loads the ADK agent and serves the HTML files from templates/.

- `cloudbuild.yaml`: Configuration file for automating deployments with Google Cloud Build.

- `Dockerfile`: Instructions for building the application's container image.

- `requirements.txt`: A list of all necessary Python dependencies.

- `templates/`: Contains all frontend files (HTML, CSS, JS).


# 🚀 Running the Application Locally
This application runs as a single, unified service using FastAPI.

1. **Navigate to the project's root directory:**
```
cd adk-healthcare
```

2. **Create and activate a virtual environment:**

```
python3 -m venv .venv
source .venv/bin/activate
```

3. **Install the required dependencies:**

```
pip install -r requirements.txt
```

4. **Configure your .env file:**
Copy the .env.example file (if one exists) to a new file named .env inside the healthcare-patient-id/ directory. Fill in all the required variables (GCP Project ID, FHIR credentials, etc.).

5. **Run the FastAPI server:**

```
uvicorn main:app --reload
```

The server will start, typically on http://localhost:8000.

**Accessing the Application**
- Open your browser and navigate to http://localhost:8000/. You will see the chatbot interface immediately.

# ☁️ Automated Deployment to Google Cloud Run
This project uses a `cloudbuild.yaml` file to automate deployment to Cloud Run. The pipeline is triggered on every `git push` to your main branch.

**Prerequisites (One-Time Setup)**
> 1. **Store Environment Variables in Secret Manager**

For security, your `.env` variables must be stored in Google Secret Manager.

1. Navigate to Secret Manager in the Google Cloud Console.

2. Create a new secret:

    - Name it `healthcare-patient-env` (or a name of your choice).

    - In the **Secret value**, paste the entire content of your local `.env` file.

    - Click **"Create secret"**.

>2. **Grant Permissions to Cloud Build**

The Cloud Build service account needs permission to access secrets and deploy to Cloud Run.

1. Navigate to IAM & Admin.

2. Find the service account ending in `@cloudbuild.gserviceaccount.com`.

3. Click the pencil icon to edit its roles.

4. **Add** the following two roles:

- `Secret Manager Secret Accessor`

- `Cloud Run Admin`

5. Click **"Save"**.

> 3. Create a Cloud Build Trigger

This connects your GitHub repository to Cloud Build.

1. Navigate to **Cloud Build Triggers**.

2. Connect your GitHub repository if you haven't already.

3. Create a new trigger:

- **Name**: **deploy-on-push-main**

- **Event**: Push to a branch

- **Repository**: Select your project repository.

- **Branch**: `^main$` (or your primary branch name).

- **Configuration**: Cloud Build configuration file (yaml or json)

- **Location**: Repository, with the path set to `cloudbuild.yaml`.

- **Substitution Variables (IMPORTANT)**:

    - Click **"Add variable"**.

    - Variable: `_SECRET_ID`

    - Value: Enter the name of the secret you created in Step 1 (e.g., `healthcare-patient-env`).

- Click **"Create"**.

**How It Works**

With this setup, every time you execute a `git push` to your main branch, Cloud Build will automatically:

1. Fetch your secrets from Secret Manager.

2. Build your Docker container image.

3. Push the image to Google Artifact Registry.

4. Deploy the new version to your Cloud Run service.