import requests
import time
import os
from crewai_tools import tool

BROWSER_USE_API_KEY = os.getenv("BROWSER_USE_API_KEY")
MCP_URL = "https://api.browser-use.com/mcp"

@tool("browser_use_extract_listing")
def browser_use_extract_listing(url: str) -> str:
    """
    Uses Browser Use Cloud MCP to open a listing page in a real browser
    and extract structured rental listing data.
    """
    headers = {
        "X-Browser-Use-API-Key": BROWSER_USE_API_KEY,
        "Content-Type": "application/json",
    }

    # 1. Start browser task
    task_payload = {
        "tool": "browser_task",
        "arguments": {
            "task": f"""
            Go to {url}.
            Wait for page to fully load.
            Extract rental listing data:
            address, price, bedrooms, bathrooms, images, description,
            facts/features, and contact info.
            Return JSON only.
            """,
            "max_steps": 10
        }
    }

    res = requests.post(MCP_URL, json=task_payload, headers=headers)
    task_id = res.json()["task_id"]

    # 2. Poll until done
    while True:
        status = requests.post(
            MCP_URL,
            json={
                "tool": "monitor_task",
                "arguments": {"task_id": task_id}
            },
            headers=headers
        ).json()

        if status["status"] in ["completed", "failed"]:
            return status.get("result", "{}")

        time.sleep(2)

