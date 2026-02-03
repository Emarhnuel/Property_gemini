import requests
import time
import os

BROWSER_USE_API_KEY = os.getenv("BROWSER_USE_API_KEY")
MCP_URL = "https://api.browser-use.com/mcp"

HEADERS = {
    "X-Browser-Use-API-Key": BROWSER_USE_API_KEY,
    "Content-Type": "application/json",
}

# 1️⃣ Start browser task
start_payload = {
    "tool": "browser_task",
    "arguments": {
        "task": """
        Go to https://www.zillow.com.
        In the search box, search for "2 bedroom apartments for rent in New York".
        Wait for results to load.
        Scroll the page to load listings.
        Click the first rental listing.
        Wait for the listing page to fully load.

        Extract the following from the listing page:
        - Address
        - Rent price
        - Bedrooms and bathrooms
        - First 5 image URLs
        - Listing description

        Return the result as JSON.
        """,
        "max_steps": 10
    }
}

response = requests.post(MCP_URL, headers=HEADERS, json=start_payload)
response.raise_for_status()
task_id = response.json()["task_id"]

print("✅ Started browser task:", task_id)

# 2️⃣ Monitor task
while True:
    poll_payload = {
        "tool": "monitor_task",
        "arguments": {
            "task_id": task_id
        }
    }

    poll_resp = requests.post(MCP_URL, headers=HEADERS, json=poll_payload)
    poll_resp.raise_for_status()
    status = poll_resp.json()

    print("⏳ Status:", status["status"])

    if status["status"] in ("completed", "failed"):
        print("\n===== FINAL RESULT =====")
        print(status.get("result"))
        break

    time.sleep(2)
