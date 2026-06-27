import sys
import os
from pymongo import MongoClient

# Add parent directory to sys.path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from backend.app.core.config import settings
from backend.app.core.utils import utcnow, new_id
from backend.app.schemas import PlatformRole

def bootstrap_owner(email: str):
    print(f"--- FlowForge Platform Owner Bootstrap ---")

    # Securely mask the URL in prints
    masked_url = settings.MONGO_URL.split("@")[-1] if "@" in settings.MONGO_URL else "localhost"
    print(f"Connecting to MongoDB at {masked_url}...")

    client = MongoClient(settings.MONGO_URL)
    db = client[settings.DB_NAME]
    users_col = db["users"]
    audit_col = db["audit_events"]

    email = email.lower().strip()
    user = users_col.find_one({"email": email})

    if not user:
        print(f"ERROR: User with email '{email}' not found.")
        print("ACTION REQUIRED: Register the user first via the UI or API.")
        sys.exit(1)

    print(f"Target User: {user['full_name']} ({user['user_id']})")

    if user.get("is_platform_admin") and user.get("platform_role") == PlatformRole.PLATFORM_OWNER:
        print(f"INFO: User already has PLATFORM_OWNER role. No changes made.")
        return

    update_data = {
        "is_platform_admin": True,
        "platform_role": PlatformRole.PLATFORM_OWNER,
        "updated_at": utcnow()
    }

    result = users_col.update_one(
        {"user_id": user["user_id"]},
        {"$set": update_data}
    )

    if result.modified_count > 0:
        print(f"SUCCESS: User '{email}' promoted to PLATFORM_OWNER.")

        # Record Audit Event
        audit_col.insert_one({
            "event_id": new_id(),
            "event_type": "platform_role_assigned",
            "actor_id": "system_bootstrap",
            "subject_id": user["user_id"],
            "metadata": {"role": PlatformRole.PLATFORM_OWNER},
            "timestamp": utcnow()
        })
        print("Audit event recorded.")
    else:
        print(f"ERROR: Failed to update user record.")
        sys.exit(1)

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python scripts/bootstrap_owner.py <email>")
        sys.exit(1)

    target_email = sys.argv[1]
    bootstrap_owner(target_email)
