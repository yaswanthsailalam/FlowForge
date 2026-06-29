import sys
import os
import logging
from pymongo import MongoClient
from pymongo.errors import ConnectionFailure, OperationFailure, ServerSelectionTimeoutError

# Add parent directory to sys.path to import settings
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from backend.app.core.config import settings

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("verify_mongodb")

def verify_mongodb():
    mongo_url = settings.MONGO_URL
    db_name = settings.DB_NAME

    # Safe masking
    masked_url = mongo_url.split("@")[-1] if "@" in mongo_url else "localhost"
    logger.info(f"Targeting Host: {masked_url}")
    logger.info(f"Targeting Database: {db_name}")

    if db_name == "flowforge_ai" and os.environ.get("FORCE_PROD") != "true":
        logger.warning("Refusing to run against production database 'flowforge_ai' without FORCE_PROD=true")
        # For this script, we default to flowforge_ai_preview if not set,
        # but settings might have flowforge_ai as default.
        if db_name == "flowforge_ai":
             logger.info("Defaulting to flowforge_ai_preview for safety.")
             db_name = "flowforge_ai_preview"

    client = MongoClient(mongo_url, serverSelectionTimeoutMS=5000)

    try:
        # 1. Connection Ping
        client.admin.command('ping')
        logger.info("✅ DNS and Network: Connected")

        # 2. Authentication Check
        db = client[db_name]
        # Attempt to list collections as a proxy for auth/permission check
        db.list_collection_names()
        logger.info(f"✅ Authentication: Success for database '{db_name}'")

        # 3. Write Access Check
        test_col = db["_verification_test"]
        test_doc = {"test": "data", "timestamp": "now"}
        test_col.insert_one(test_doc)
        logger.info("✅ Write Access: Success")

        # Cleanup
        test_col.delete_one({"test": "data"})
        logger.info("✅ Cleanup: Success")

        print("\nSUMMARY: MongoDB is READY")
        return 0

    except ServerSelectionTimeoutError:
        logger.error("❌ ERROR: Connection timed out. Check DNS or network/firewall.")
        return 1
    except OperationFailure as e:
        if e.code == 18 or "auth failed" in str(e).lower():
            logger.error("❌ ERROR: Authentication failed. Check username and password.")
        else:
            logger.error(f"❌ ERROR: Operation failed: {e.details.get('errmsg', str(e))}")
        return 1
    except ConnectionFailure:
        logger.error("❌ ERROR: Connection failure.")
        return 1
    except Exception as e:
        logger.error(f"❌ ERROR: Unexpected error: {str(e)}")
        return 1
    finally:
        client.close()

if __name__ == "__main__":
    sys.exit(verify_mongodb())
