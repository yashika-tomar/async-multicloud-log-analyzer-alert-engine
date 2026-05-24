import httpx
import os
import asyncio  
from datetime import datetime  
from fastapi import FastAPI, UploadFile, File, BackgroundTasks, Query
from parser import parse_line 

app = FastAPI()
DISCORD_WEBHOOK_URL = os.environ.get("DISCORD_WEBHOOK_URL")

async def send_discord_alert(payload: dict):
    """Asynchronously dispatches an incident card to the DevOps/SecOps channel."""
    async with httpx.AsyncClient() as client:
        try:
            response = await client.post(DISCORD_WEBHOOK_URL, json=payload)
            print(f"[Alert Engine] Discord broadcast status: {response.status_code}")
        except Exception as e:
            print(f"❌ Failed to send alert to Discord: {e}")

def process_log_bg(file_contents: str, pipeline: str, environment: str, repository: str):
    """
    Background worker that filters logs. Routes Multi-Cloud CI/CD pipeline errors 
    (Azure, GCP) and critical Web Gateway server errors (403/500) seamlessly to Discord.
    """
    print("--- [Background Task] Starting Unified Log Stream Analysis ---")
    
    current_stage = "Unknown Stage"
    
    for line in file_contents.splitlines():
        parsed_data = parse_line(line)
        
        if parsed_data:
            # 1. Update active pipeline stage context across different cloud providers
            if parsed_data["type"] == "AZURE_TASK_STARTED":
                current_stage = parsed_data.get("task", current_stage)
                continue
            elif parsed_data["type"] == "GCP_STEP_STARTED":
                current_stage = parsed_data.get("task", current_stage)
                continue

            # 🚨 2. Route CI/CD Pipeline Failures (Supports Azure DevOps & Google Cloud Build)
            if parsed_data["type"] in ["AZURE_PIPELINE_ERROR", "GCP_BUILD_ERROR"]:
                timestamp_str = datetime.utcnow().strftime("%Y-%m-%d %H:%M UTC")
                source_agent = parsed_data.get("source", "Pipeline_Scanner")
                
                discord_payload = {
                    "username": "CI/CD Observability Engine",
                    "embeds": [{
                        "title": "❌ CI/CD Pipeline Build Failure",
                        "color": 15158332,
                        "fields": [
                            {"name": "📋 Pipeline", "value": pipeline, "inline": True},
                            {"name": "🌐 Environment", "value": environment, "inline": True},
                            {"name": "⚡ Failed Stage", "value": current_stage, "inline": True},
                            {"name": "📦 Repository", "value": repository, "inline": True},
                            {"name": "🚨 Severity", "value": "CRITICAL", "inline": True},
                            {"name": "⏱️ Timestamp", "value": timestamp_str, "inline": True},
                            {"name": "🔍 Error Message", "value": f"```text\n{parsed_data['message']}\n```", "inline": False}
                        ],
                        "footer": {"text": f"Cloud Agent: {source_agent}"}
                    }]
                }
                asyncio.run(send_discord_alert(discord_payload))
                break 

            # 🌐 3. Route Web Gateway Production Anomalies (403 Forbidden / 500 Server Error)
            elif parsed_data["type"] == "WEB_SERVER_LOG":
                status_code = parsed_data.get("status")
                
                if status_code in ["403", "500"]:
                    timestamp_str = datetime.utcnow().strftime("%Y-%m-%d %H:%M UTC")
                    
                    severity_level = "CRITICAL" if status_code == "500" else "WARNING"
                    card_title = "💥 Production Server Exception (500)" if status_code == "500" else "🛑 Security Incident Flagged (403)"
                    card_color = 15158332 if status_code == "500" else 15105570  
                    
                    discord_payload = {
                        "username": "API Gateway Monitor",
                        "embeds": [{
                            "title": card_title,
                            "color": card_color,
                            "fields": [
                                {"name": "🌐 Source IP", "value": parsed_data.get("ip", "Unknown"), "inline": True},
                                {"name": "🛣️ Request Path", "value": f"`{parsed_data.get('method')} {parsed_data.get('path')}`", "inline": True},
                                {"name": "🔢 Status Code", "value": f"**{status_code}**", "inline": True},
                                {"name": "🚨 Incident Severity", "value": severity_level, "inline": True},
                                {"name": "⏱️ Operational Time", "value": timestamp_str, "inline": True}
                            ],
                            "footer": {"text": f"Gateway Cluster: {parsed_data.get('source', 'Nginx_Gateway')}"}
                        }]
                    }
                    asyncio.run(send_discord_alert(discord_payload))

    print("--- [Background Task] Completed Analysis ---")  

@app.post("/upload-logs/")
async def upload_log_file(
    background_tasks: BackgroundTasks, 
    file: UploadFile = File(...),
    pipeline: str = Query("Frontend-Build-Pipeline", description="Name of the executing pipeline"),
    environment: str = Query("UAT", description="Target environment deployment stage"),
    repository: str = Query("job-portal-frontend", description="Source code repository code link")
):
    """
    Ingests log files and pushes metadata directly to background processing workers.
    """
    contents = await file.read()
    text_content = contents.decode("utf-8")
    
    background_tasks.add_task(process_log_bg, text_content, pipeline, environment, repository)
    
    return {
        "status": "Successfully Queued",
        "filename": file.filename,
        "message": "The pipeline log stream is being analyzed asynchronously. Alerts will dispatch instantly if issues are found."
    }