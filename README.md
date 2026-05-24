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

🚀 Getting Started
1. Clone the Repository
git clone [https://github.com/YOUR_USERNAME/async-multicloud-log-analyzer-alert-engine.git](https://github.com/YOUR_USERNAME/async-multicloud-log-analyzer-alert-engine.git)
cd async-multicloud-log-analyzer-alert-engine

2. Install Dependencies
Bash
pip install fastapi uvicorn httpx pydantic
3. Set Your Environment Secrets
To keep your webhooks hidden from public source directories, set the runtime token parameter locally before booting up the microservice application server:

PowerShell
# PowerShell / Windows Environment Configuration Setup
$env:DISCORD_WEBHOOK_URL="[https://discordapp.com/api/webhooks/your-actual-secure-token-here](https://discordapp.com/api/webhooks/your-actual-secure-token-here)"
4. Run the Server
Bash
uvicorn main:app --reload
Once started, navigate to http://127.0.0.1:8000/docs to access the interactive Swagger UI Documentation dashboard to upload files and execute live stream parsing.

📋 Extensible Parsing Signatures
The decoupled design separates routing blueprints from core ingestion logic, making it fully extensible to support any system signature. Current production profiles include:

Google Cloud Build: Tracks lifecycle boundaries (Starting build step #) and intercepts compilation termination structures.

Azure DevOps Pipelines: Matches standard ##[error] and ##[warning] tokens alongside contextual runtime pipelines tracking.

Web Gateways / Nginx: Monitors live HTTP request methods, tracking access attempts, and filtering critical anomalies like 403 Forbidden security risks or 500 Internal Server Errors.

---

### How to apply this updated markdown right now:

1. Open your local `README.md` file on your desktop and replace its contents entirely with this text.
2. Open your PowerShell terminal and push the updated documentation block to your remote repo branch:

```powershell
git add README.md
git commit -m "docs: upgrade readme documentation with secure env instructions and gcp specs"
git push origin main
