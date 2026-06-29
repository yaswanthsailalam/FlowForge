import logging
from fastapi import FastAPI, HTTPException, status
from fastapi.middleware.cors import CORSMiddleware
from backend.app.api.api_v1.api import api_router
from backend.app.core.config import settings
from backend.app.db.mongodb import init_db, is_db_connected

logger = logging.getLogger(__name__)

app = FastAPI(
    title=settings.PROJECT_NAME,
    openapi_url=f"{settings.API_V1_STR}/openapi.json"
)

# CORS Configuration
allowed_origins = [str(origin) for origin in settings.BACKEND_CORS_ORIGINS]
logger.info(f"Configuring CORS with {len(allowed_origins)} origins: {allowed_origins}")

app.add_middleware(
    CORSMiddleware,
    allow_origins=allowed_origins if allowed_origins else ["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.on_event("startup")
def startup_db_client():
    # Attempt to initialize DB, but we allow startup to continue
    # so we can report unhealthiness via /api/health
    try:
        init_db()
    except Exception:
        # logging is already handled in init_db
        pass

@app.get("/api/health")
def health_check():
    db_status = "connected" if is_db_connected() else "disconnected"
    status_code = status.HTTP_200_OK

    if db_status == "disconnected":
        # We return a 503 so Render/Load Balancers know we are not ready
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail={"status": "unhealthy", "db": db_status}
        )

    return {
        "status": "healthy",
        "service": settings.PROJECT_NAME,
        "db": db_status
    }

# Readiness endpoint specifically for Render
@app.get("/api/ready")
def ready_check():
    if not is_db_connected():
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="Database not connected"
        )
    return {"status": "ready"}

app.include_router(api_router, prefix=settings.API_V1_STR)
