import pytest
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.testclient import TestClient
from backend.app.core.config import Settings
import os

def test_cors_parsing():
    # 1. Test JSON list string
    os.environ["BACKEND_CORS_ORIGINS"] = '["https://preview.onrender.com", "http://localhost:3000/"]'
    s = Settings()
    # Pydantic Settings might cache or reload from env
    # Our validator strips and rstrips "/"
    assert "https://preview.onrender.com" in s.BACKEND_CORS_ORIGINS
    assert "http://localhost:3000" in s.BACKEND_CORS_ORIGINS
    assert "http://localhost:3000/" not in s.BACKEND_CORS_ORIGINS

    # 2. Test comma separated string
    os.environ["BACKEND_CORS_ORIGINS"] = "https://a.com, https://b.com"
    s2 = Settings()
    assert s2.BACKEND_CORS_ORIGINS == ["https://a.com", "https://b.com"]

    # 3. Test single origin string
    os.environ["BACKEND_CORS_ORIGINS"] = "https://c.com"
    s3 = Settings()
    assert s3.BACKEND_CORS_ORIGINS == ["https://c.com"]

def test_cors_middleware_configuration():
    # Verify the exact logic used in main.py for middleware configuration
    test_origin = "https://flowforge-frontend-preview.onrender.com"
    allowed_origins = [test_origin]

    demo_app = FastAPI()
    demo_app.add_middleware(
        CORSMiddleware,
        allow_origins=allowed_origins,
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    @demo_app.get("/api/test")
    def test_route():
        return {"status": "ok"}

    client = TestClient(demo_app)

    # 1. Valid Preflight
    headers = {
        "Origin": test_origin,
        "Access-Control-Request-Method": "POST",
        "Access-Control-Request-Headers": "content-type",
    }
    response = client.options("/api/test", headers=headers)
    assert response.status_code == 200
    assert response.headers.get("access-control-allow-origin") == test_origin
    assert "POST" in response.headers.get("access-control-allow-methods", "")
    assert response.headers.get("access-control-allow-credentials") == "true"

    # 2. Invalid Origin
    malicious_headers = {
        "Origin": "https://malicious.com",
        "Access-Control-Request-Method": "POST",
    }
    malicious_res = client.options("/api/test", headers=malicious_headers)
    # CORSMiddleware returns 200 but without Access-Control-Allow-Origin
    assert malicious_res.headers.get("access-control-allow-origin") is None

    # 3. Headers on error response
    @demo_app.get("/api/error")
    def error_route():
        from fastapi import HTTPException
        raise HTTPException(status_code=503, detail="DATABASE_UNAVAILABLE")

    error_res = client.get("/api/error", headers={"Origin": test_origin})
    assert error_res.status_code == 503
    assert error_res.headers.get("access-control-allow-origin") == test_origin
