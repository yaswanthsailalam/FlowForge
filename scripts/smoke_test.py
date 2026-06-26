import os
import sys
import requests
import uuid
import time

FRONTEND_URL = os.environ.get("FLOWFORGE_FRONTEND_URL")
BACKEND_URL = os.environ.get("FLOWFORGE_BACKEND_URL")
EMAIL_PREFIX = os.environ.get("FLOWFORGE_TEST_EMAIL_PREFIX", "smoke")

def test_flow():
    if not BACKEND_URL:
        print("ERROR: FLOWFORGE_BACKEND_URL required.")
        sys.exit(1)

    print(f"--- FlowForge Smoke Test ---")
    print(f"Target Backend: {BACKEND_URL}")

    # 1. Health Check
    try:
        res = requests.get(f"{BACKEND_URL}/api/health")
        res.raise_for_status()
        print("PASS: Health Check")
    except Exception as e:
        print(f"FAIL: Health Check - {e}")
        sys.exit(1)

    # 2. Registration
    user_email = f"{EMAIL_PREFIX}-{uuid.uuid4().hex[:8]}@test.com"
    password = "SecurePassword123!"
    try:
        res = requests.post(f"{BACKEND_URL}/api/auth/register", json={
            "email": user_email,
            "password": password,
            "full_name": "Smoke Test User"
        })
        res.raise_for_status()
        print(f"PASS: Registration ({user_email})")
    except Exception as e:
        print(f"FAIL: Registration - {e}")
        sys.exit(1)

    # 3. Login
    try:
        res = requests.post(f"{BACKEND_URL}/api/auth/login", data={
            "username": user_email,
            "password": password
        })
        res.raise_for_status()
        token = res.json()["access_token"]
        print("PASS: Login")
    except Exception as e:
        print(f"FAIL: Login - {e}")
        sys.exit(1)

    # 4. Create Process Model
    headers = {"Authorization": f"Bearer {token}", "X-Workspace-Id": "placeholder"}
    # Note: In a real test, we would first create a workspace

    print("Smoke test reached end of implemented automated steps.")
    print("SUCCESS: Core authentication and health verified.")

if __name__ == "__main__":
    test_flow()
