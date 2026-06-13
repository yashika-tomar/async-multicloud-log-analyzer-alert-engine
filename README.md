# Asynchronous Multi-Cloud CI/CD Log Analyzer & Alerting Engine

A high-performance, asynchronous microservice built with **FastAPI** designed to ingest, process, and analyze massive infrastructure streams and multi-cloud CI/CD logs memory-efficiently. The system automatically detects pipeline build failures and server anomalies on the fly, routing real-time contextual alerts to communications channels securely via environment-driven webhooks.

🚀 Core Features
Memory-Efficient Streaming Pipeline: Uses Python line-generators (yield) to read files line-by-line. This keeps memory usage flat and constant, allowing the app to parse gigabyte-scale log files easily without running out of RAM.

Multi-Cloud Log Router: A pattern-matching engine using regular expressions (RegEx) that automatically identifies logs from Azure DevOps, Google Cloud Build, and Nginx API Gateways.

Non-Blocking Asynchronous I/O: Built on FastAPI using BackgroundTasks. The app accepts log files, instantly tells the user "Successfully Queued" (200 OK), and processes the heavy file scanning out-of-band so the user doesn't have to wait.

Instant Incident Alerting: Uses HTTPX to push beautifully structured notification cards directly to a Discord channel webhook the exact millisecond an error is found.

Containerized Architecture: Fully packaged using Docker to ensure the application runs identically on any machine, eliminating environment configuration bugs.

Self-Healing Orchestration: Configured for Kubernetes with multiple replicas for high availability and automated liveness health checks to prevent downtime.

Enterprise-Grade Security: Sensitive keys (like the Discord Webhook URL) are completely removed from the source code. They are stored securely in a Kubernetes Secret vault and injected into the app's memory at runtime.

🏗️ Architecture Data Flow
```text
[ Raw Log File Uploaded ] 
          │
          ▼
   ┌─────────────┐
   │ FastAPI API │ ──► Returns immediate 200 OK to user / upstream agent
   └─────────────┘
          │
          ▼ (Offloaded out-of-band via BackgroundTasks)
   ┌───────────────────┐
   │ Line Generator    │ ──► Streams file line-by-line to protect RAM
   └───────────────────┘
          │
          ▼
   ┌───────────────────┐
   │ Multi-Cloud RegEx │ ──► Matches patterns (Nginx / Azure / GCP)
   └───────────────────┘
          │
          ▼ (If a critical error or failure is matched)
   ┌───────────────────┐
   │ Kubernetes Secret │ ──► Safely injects Discord Webhook URL into app memory
   └───────────────────┘
          │
          ▼ 
   ┌───────────────────┐
   │ Async HTTP Client │ ──► Dispatches instant notification card to Discord
   └───────────────────┘
   
🛠️ Tech Stack
Core Engine: Python 3 (Generators, re Pattern Matcher)

Web Framework: FastAPI (Uvicorn ASGI Server)

Async Network Client: HTTPX

Containerization: Docker

Orchestration: Kubernetes (Local testing via Docker Desktop / Production via AWS EKS)

Target Integration: Discord Developer Webhooks

📂 Project Structure
For this app to run, ensure your project directory looks exactly like this:

Plaintext
async-multicloud-log-analyzer-alert-engine/
async-multicloud-log-analyzer-alert-engine/
├── main.py                 # The FastAPI web server and background worker
├── parser.py               # The regex pattern matcher engine
├── requirements.txt        # Python external library dependencies
├── Dockerfile              # Recipe to build the Docker container image
├── k8s-deployment.yaml     # Kubernetes deployment configuration (2 replicas)
├── k8s-service.yaml        # Kubernetes network routing (NodePort configuration)
├── k8s-secret-sample.yaml  # Safe template showing how to set up secrets
├── .gitignore              # Tells Git to hide venv/ and real secret files
└── README.md               # This documentation file

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

 🐳 How to Run via Docker
If you want to package the app into a container instead of running it raw on your laptop, use these commands:

1. Build the Docker Image
Bash
docker build -t log-analyzer:latest .
2. Run the Container locally
Bash
docker run -d -p 8000:8000 --env DISCORD_WEBHOOK_URL="your_actual_webhook_url" log-analyzer:latest
☸️ How to Run via Kubernetes
To deploy the application as a self-healing, load-balanced system using the provided configuration files, make sure Docker Desktop has Kubernetes enabled, then run:

1. Configure Your Safe Kubernetes Secret Template
Look at k8s-secret-sample.yaml.

Create your own local file named k8s-secret.yaml (this file is hidden from Git automatically via .gitignore).

Convert your real Discord webhook URL to a Base64 string and paste it into the data field.

2. Apply the Deployments and Network Services
PowerShell
kubectl apply -f k8s-secret.yaml
kubectl apply -f k8s-deployment.yaml
kubectl apply -f k8s-service.yaml
3. Verify Cluster Status
PowerShell
kubectl get pods
kubectl get service log-analyzer-service
Once running, the Kubernetes service will open port 32145(sample value) on your computer. Open your web browser and navigate to: http://localhost:32145/docs to view the app!

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
