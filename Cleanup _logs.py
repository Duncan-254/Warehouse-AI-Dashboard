import os
import requests
from dotenv import load_dotenv

load_dotenv()

BASE_URL = f"http://{os.getenv('FRA_IP')}:8000"
API_KEY = os.getenv('FRA_API_KEY')
API_SECRET = os.getenv('FRA_API_SECRET')
DOCTYPE = "Warehouse Attendance"

headers = {
    "Authorization": f"token {API_KEY}:{API_SECRET}",
    "Content-Type": "application/json"
}

def wipe_ugly_logs():
    print(f"🔄 Connecting to {BASE_URL} to clean up dashboard...")

    # 1. Fetch the names of all existing logs
    get_url = f"{BASE_URL}/api/resource/{DOCTYPE}?limit_page_length=1000"
    response = requests.get(get_url, headers=headers)

    if response.status_code != 200:
        print(f" Failed to fetch. Check if {DOCTYPE} is correct.")
        return

    logs = response.json().get("data", [])
    print(f"Found {len(logs)} messy logs. Starting deletion...")

    # 2. Delete the logs
    for log in logs:
        name = log['name']
        # If the name is already clean (optional check), skip it
        if name.startswith("AI-LOG-"):
            continue

        delete_url = f"{BASE_URL}/api/resource/{DOCTYPE}/{name}"
        res = requests.delete(delete_url, headers=headers)

        if res.status_code == 202 or res.status_code == 200:
            print(f" Deleted: {name}")
        else:
            print(f" Could not delete {name}. Status: {res.status_code}")

    print("\n Cleanup Complete! Your dashboard is now a blank canvas.")

if __name__ == "__main__":
    wipe_ugly_logs()