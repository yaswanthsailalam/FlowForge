from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from backend.app.api.api_v1.api import api_router
from backend.app.core.config import settings
from backend.app.db.mongodb import init_db

app = FastAPI(
    title=settings.PROJECT_NAME,
    openapi_url=f"{settings.API_V1_STR}/openapi.json"
)

# Set all CORS enabled origins
if settings.BACKEND_CORS_ORIGINS:
    app.add_middleware(
        CORSMiddleware,
        allow_origins=[str(origin) for origin in settings.BACKEND_CORS_ORIGINS],
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )
else:
    # Fallback for dev if not configured
    app.add_middleware(
        CORSMiddleware,
        allow_origins=["*"],
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

@app.on_event("startup")
def startup_db_client():
    init_db()

@app.get("/api/health")
def health_check():
    return {"status": "healthy", "service": settings.PROJECT_NAME}

app.include_router(api_router, prefix=settings.API_V1_STR)
