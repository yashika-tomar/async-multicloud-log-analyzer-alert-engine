# Asynchronous Multi-Cloud CI/CD Log Analyzer & Alerting Engine

A high-performance, asynchronous microservice built with **FastAPI** designed to ingest, process, and analyze massive infrastructure streams and multi-cloud CI/CD logs memory-efficiently. The system automatically detects pipeline build failures and server anomalies on the fly, routing real-time contextual alerts to communications channels securely via environment-driven webhooks.

## 🚀 Core Features

*   **Memory-Insulated Streaming Pipeline:** Utilizes Python line-generators (`yield`) to maintain a flat $O(1)$ constant space complexity, seamlessly parsing gigabyte-scale logs without memory exhaustion.
*   **Decoupled Multi-Cloud Router:** A pluggable regular expression engine that automatically identifies log footprints and isolates errors across **Azure DevOps**, **Google Cloud Build**, and **Enterprise API Gateways**.
*   **Enterprise-Grade Security:** Fully decoupled application secrets from source code. Adheres to Twelve-Factor App methodologies by utilizing environment configurations via Python's `os.environ` to completely prevent credential leaking.
*   **Non-Blocking Asynchronous I/O:** Built on **FastAPI** using `BackgroundTasks` to offload deep file scanning out-of-band, allowing the API ingestion tier to return instantaneous responses to upstream agents.
*   **Rich Incident Push Alerting:** Integrated with **HTTPX** to push highly-detailed, beautifully structured JSON Markdown Embed cards to target webhooks the split-second a failure state transitions.

## 🏗️ Architecture Data Flow

```text
[ Raw Log File Uploaded ] 
          │
          ▼
   ┌─────────────┐
   │ FastAPI API │ ──► Returns immediate 200 OK to upstream agent
   └─────────────┘
          │
          ▼ (Offloaded out-of-band via BackgroundTasks)
   ┌───────────────────┐
   │ Line Generator    │ ──► Streams file memory-efficiently line-by-line
   └───────────────────┘
          │
          ▼
   ┌───────────────────┐
   │ Multi-Cloud RegEx │ ──► Slices patterns (Web / Azure / GCP)
   └───────────────────┘
          │
          ▼ (If a critical anomaly or failure state is matched)
   ┌───────────────────┐
   │ Environment Envs  │ ──► Inject target Webhook URL securely via runtime variables
   └───────────────────┘
          │
          ▼ 
   ┌───────────────────┐
   │ Async HTTP Client │ ──► Dispatches instant notification cards to Discord
   └───────────────────┘
🛠️ Tech Stack
Core Engine: Python 3 (Generators, re Pattern Matcher)

Web Framework: FastAPI (Uvicorn ASGI Server)

Async Network Client: HTTPX

Target Integration: Discord Developer Webhooks

📂 Project Structure
For this app to run, ensure your project directory looks exactly like this:

Plaintext
async-multicloud-log-analyzer-alert-engine/
├── main.py          # The FastAPI web server and background worker
├── parser.py        # The regex pattern matcher engine
├── .env             # (Optional) Local environment configuration secret file
└── README.md        # This documentation block
📦 Project Code Blueprints
1. Create parser.py
Create a file named parser.py and paste this regex parsing logic:

Python
import re

def parse_line(line: str) -> dict or None:
    # 1. Match Azure Lifecycle and Errors
    if "AZURE_TASK_STARTED" in line:
        match = re.search(r"AZURE_TASK_STARTED:\s*(.*)", line)
        return {"type": "AZURE_TASK_STARTED", "task": match.group(1)} if match else None
    if "##[error]" in line:
        return {"type": "AZURE_PIPELINE_ERROR", "message": line, "source": "Azure_DevOps_Agent"}

    # 2. Match GCP Cloud Build Lifecycle and Errors
    if "Starting build step" in line:
        match = re.search(r"Starting build step #\d+:\s*(.*)", line)
        return {"type": "GCP_STEP_STARTED", "task": match.group(1)} if match else None
    if "ERROR: (gcloud.builds)" in line or "Build failed" in line:
        return {"type": "GCP_BUILD_ERROR", "message": line, "source": "Google_Cloud_Build_Worker"}

    # 3. Match API Gateway Web Logs (Nginx style)
    web_match = re.search(r'(?P<ip>\d+\.\d+\.\d+\.\d+).*"(?P<method>\w+) (?P<path>[^\s]+).*"\s(?P<status>\d{3})', line)
    if web_match:
        data = web_match.groupdict()
        data["type"] = "WEB_SERVER_LOG"
        data["source"] = "Nginx_Production_Gateway"
        return data

    return None
🚀 Getting Started (Step-by-Step)
1. Clone the Repository
Bash
git clone [https://github.com/YOUR_USERNAME/async-multicloud-log-analyzer-alert-engine.git](https://github.com/YOUR_USERNAME/async-multicloud-log-analyzer-alert-engine.git)
cd async-multicloud-log-analyzer-alert-engine
2. Set Up a Virtual Environment & Install Dependencies
Bash
# Create the environment
python -m venv venv

# Activate it (Windows)
.\venv\Scripts\activate

# Install required external modules
pip install fastapi uvicorn httpx pydantic python-dotenv
3. Configure Your Discord Webhook Secret
To push automated error alerts straight to your server, you need to set up your environment variable using one of the two options below:

Option A: Create a .env file (easiest & recommended)
Create a text file named .env in the root directory and paste your link:

Plaintext
DISCORD_WEBHOOK_URL=[https://discordapp.com/api/webhooks/your-actual-discord-token-here](https://discordapp.com/api/webhooks/your-actual-discord-token-here)
Option B: Set via Windows PowerShell
If you don't want to use a file, run this directly inside your open terminal:

PowerShell
$env:DISCORD_WEBHOOK_URL="[https://discordapp.com/api/webhooks/your-actual-discord-token-here](https://discordapp.com/api/webhooks/your-actual-discord-token-here)"
4. Run the Application
Bash
uvicorn main:app --reload
Once the log prints Uvicorn running on http://127.0.0.1:8000, open your web browser and navigate to: http://127.0.0.1:8000/docs. This launches an interactive Swagger UI control dashboard.

🔬 How to Test (Sample Data)
To test the alert workflows instantly, save this sample log text block into a dummy file named test_logs.txt:

Plaintext
192.168.1.50 - - [24/May/2026:16:00:00] "GET /api/v1/health HTTP/1.1" 200
AZURE_TASK_STARTED: Production Frontend Assets Build
192.168.1.89 - - [24/May/2026:16:01:12] "POST /api/v1/admin/settings HTTP/1.1" 403
##[error] Webpack Compilation failed: Module not found 'src/components/Navbar'
Execution Steps via Swagger:
Expand the POST /upload-logs/ endpoint accordion inside the Swagger web view.

Click Try it out.

Upload your test_logs.txt file into the file picker input field.

Click the blue Execute button.

Expected Result: The webpage will instantly return a Successfully Queued status code response, and a structured, formatted alert block card will push directly into your integrated Discord server backend via the background runner loop!


---

### 🏁 Update Your Repository One Last Time

Save your local `README.md` file with this text, open your terminal, and run:

```powershell
git add README.md parser.py
git commit -m "docs: finalize bulletproof, copy-paste runnable instructions for the readme"
git push origin main
