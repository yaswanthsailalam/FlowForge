from fastapi import APIRouter
from backend.app.api.api_v1.endpoints import auth, workspaces, poc, users

api_router = APIRouter()
api_router.include_router(auth.router, prefix="/auth", tags=["auth"])
api_router.include_router(users.router, prefix="/users", tags=["users"])
api_router.include_router(workspaces.router, prefix="/workspaces", tags=["workspaces"])
api_router.include_router(poc.router, prefix="/poc", tags=["poc"])
