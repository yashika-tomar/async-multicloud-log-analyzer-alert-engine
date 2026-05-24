import re
from typing import Optional, Dict, Generator

# 🔍 Pluggable Regular Expressions Blueprints

# 1. NEW: GCP Cloud Build Patterns
GCP_STEP_START = r'INFO\s+Starting build step #(?P<step_num>\d+)\s+-\s+(?P<step_name>.*)'
GCP_GLOBAL_FAIL = r'BUILD FAILURE:\s+(?P<reason>.*)'

# 2. Existing Azure DevOps Patterns
AZURE_ERROR_PATTERN = r'##\[error\](?P<message>.*)'
AZURE_WARN_PATTERN = r'##\[warning\](?P<message>.*)'
AZURE_TASK_START = r'^Starting:\s*(?P<task_name>.*)'
AZURE_TASK_FINISH = r'^Finishing:\s*(?P<task_name>.*)'

# 3. Existing Web Server Log Pattern (Fallback)
WEB_LOG_PATTERN = r'IP=(?P<ip>[^\s]+).*Method=(?P<method>\w+)\s+Path=(?P<path>[^\s]+).*Status=(?P<status>\d{3})'


def stream_log_file(file_path: str) -> Generator[str, None, None]:
    """Streams the pipeline file line-by-line with flat O(1) memory profile."""
    try:
        with open(file_path, "r", encoding="utf-8") as file:
            for line in file:
                yield line
    except FileNotFoundError:
        print(f"❌ Error: The file '{file_path}' was not found.")


def parse_line(line: str) -> Optional[Dict]:
    """
    Scans a log line. Dynamically routes and routes logs depending on whether 
    it detects GCP Cloud Build, Azure DevOps, or standard Web Server formats.
    """
    clean_line = line.strip()
    if not clean_line:
        return None

    # ----------------------------------------------------
    # 🔴 ROUTE 1: GCP CLOUD BUILD PATTERNS
    # ----------------------------------------------------
    # Track the active build step changing
    gcp_start_match = re.search(GCP_STEP_START, clean_line)
    if gcp_start_match:
        return {
            "type": "GCP_STEP_STARTED",
            "task": f"Step #{gcp_start_match.group('step_num')} ({gcp_start_match.group('step_name').strip()})",
            "source": "Google_Cloud_Build"
        }

    # Catch the explicit global build termination string
    gcp_global_match = re.search(GCP_GLOBAL_FAIL, clean_line)
    if gcp_global_match:
        return {
            "type": "GCP_BUILD_ERROR",
            "severity": "CRITICAL",
            "message": gcp_global_match.group("reason").strip(),
            "source": "Google_Cloud_Build"
        }

    # ----------------------------------------------------
    # 🔵 ROUTE 2: AZURE DEVOPS PIPELINE PATTERNS
    # ----------------------------------------------------
    # Catch Critical Azure Build Errors
    azure_error_match = re.search(AZURE_ERROR_PATTERN, clean_line)
    if azure_error_match:
        return {
            "type": "AZURE_PIPELINE_ERROR",
            "severity": "CRITICAL",
            "message": azure_error_match.group("message").strip(),
            "source": "Azure_DevOps",
            "timestamp": "N/A"
        }

    # Catch Azure Warnings
    azure_warn_match = re.search(AZURE_WARN_PATTERN, clean_line)
    if azure_warn_match:
        return {
            "type": "AZURE_PIPELINE_WARNING",
            "severity": "WARNING",
            "message": azure_warn_match.group("message").strip(),
            "source": "Azure_DevOps",
            "timestamp": "N/A"
        }

    # Catch Task Lifecycle Events
    start_match = re.search(AZURE_TASK_START, clean_line)
    if start_match:
        return {
            "type": "AZURE_TASK_STARTED", 
            "task": start_match.group("task_name").strip(),
            "source": "Azure_DevOps"
        }

    finish_match = re.search(AZURE_TASK_FINISH, clean_line)
    if finish_match:
        return {
            "type": "AZURE_TASK_FINISHED", 
            "task": finish_match.group("task_name").strip(),
            "source": "Azure_DevOps"
        }

    # ----------------------------------------------------
    # 🟢 ROUTE 3: WEB SERVER LOG PATTERNS (FALLBACK)
    # ----------------------------------------------------
    web_match = re.search(WEB_LOG_PATTERN, clean_line)
    if web_match:
        data = web_match.groupdict()
        data["type"] = "WEB_SERVER_LOG"
        data["source"] = "Nginx_Gateway"
        try:
            data["timestamp"] = clean_line.split(" ")[0]
        except IndexError:
            data["timestamp"] = "N/A"
        return data

    return None


# 🧪 Local Testing Harness
if __name__ == "__main__":
    print("--- Starting Advanced Multi-Format Log Testing ---")
    
    # Updated testing harness executing both Azure and GCP sample lines
    mock_mixed_logs = [
        "Starting: Install Dependencies",
        "##[warning]Deprecated API usage detected in express@3.x",
        "Finishing: Install Dependencies",
        "2026-05-24T11:42:15.001Z INFO  Starting build step #1 - Install Dependencies",
        "2026-05-24T13:14:55.012Z [PRD-API-GW-01] ERROR c.a.p.a.AutoAPIController - [ReqID: e723a1-029c] IP=172.16.0.44 User=\"yashika@company.com\" Method=PUT Path=/api/v1/settings Protocol=HTTP/1.1 Status=500 Latency=312ms Exception=\"NullPointerException\"",
        "BUILD FAILURE: React build compilation failed"
    ]
    
    for line in mock_mixed_logs:
        result = parse_line(line)
        if result:
            print(f"\nParsed Event: {result}")