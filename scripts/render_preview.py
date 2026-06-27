import os
import sys
import requests
import time
import json

RENDER_API_URL = "https://api.render.com/v1"
API_KEY = os.environ.get("RENDER_API_KEY")
OWNER_ID = os.environ.get("RENDER_OWNER_ID")
BRANCH = "feature/product-redesign-foundation-617554644579192282"
PREVIEW_DB = "flowforge_ai_preview"

def get_headers():
    if not API_KEY:
        return {}
    return {
        "Authorization": f"Bearer {API_KEY}",
        "Accept": "application/json",
        "Content-Type": "application/json"
    }

def get_services():
    url = f"{RENDER_API_URL}/services"
    params = {"limit": 100}
    if OWNER_ID:
        params["ownerId"] = OWNER_ID

    response = requests.get(url, headers=get_headers(), params=params)
    if response.status_code != 200:
        print(f"Error fetching services: {response.status_code} - {response.text}")
        return []
    return response.json()

def trigger_deploy(service_id):
    url = f"{RENDER_API_URL}/services/{service_id}/deploys"
    response = requests.post(url, headers=get_headers())
    if response.status_code == 201:
        print(f"Deployment triggered for service {service_id}")
    else:
        print(f"Error triggering deploy: {response.status_code} - {response.text}")

def deploy_preview():
    if not API_KEY:
        print("ERROR: RENDER_API_KEY not found in environment.")
        print("Status: BLOCKED_BY_RENDER_AUTHENTICATION")
        sys.exit(1)

    print(f"--- FlowForge Render Preview Deployment (Branch: {BRANCH}) ---")

    services = get_services()
    preview_services = [s for s in services if s.get('repo') and s.get('branch') == BRANCH]

    if not preview_services:
        print(f"No active services found for branch {BRANCH}.")
        print("Check if the Render Blueprint has been applied.")
        return

    for svc in preview_services:
        svc_name = svc.get('name')
        svc_id = svc.get('id')
        print(f"Syncing service: {svc_name} ({svc_id})")
        trigger_deploy(svc_id)

    print("Deployment synchronization complete.")

if __name__ == "__main__":
    deploy_preview()
