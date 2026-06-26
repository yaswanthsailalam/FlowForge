from fastapi import APIRouter
from backend.app.api.api_v1.endpoints import auth, workspaces, poc, users, catalogue, workflows

api_router = APIRouter()
api_router.include_router(auth.router, prefix="/auth", tags=["auth"])
api_router.include_router(users.router, prefix="/users", tags=["users"])
api_router.include_router(workspaces.router, prefix="/workspaces", tags=["workspaces"])
api_router.include_router(catalogue.router, prefix="/catalogue", tags=["catalogue"])
api_router.include_router(workflows.router, prefix="/workflows", tags=["workflows"])
api_router.include_router(poc.router, prefix="/poc", tags=["poc"])
