from fastapi import APIRouter
from backend.app.api.api_v1.endpoints import (
    auth, users, workspaces, catalogue, workflows, poc, products, services, applications, organisations, support
)

api_router = APIRouter()
api_router.include_router(auth.router, prefix="/auth", tags=["auth"])
api_router.include_router(users.router, prefix="/users", tags=["users"])
api_router.include_router(workspaces.router, prefix="/workspaces", tags=["workspaces"])
api_router.include_router(catalogue.router, prefix="/catalogue", tags=["catalogue"])
api_router.include_router(workflows.router, prefix="/workflows", tags=["workflows"])
api_router.include_router(products.router, prefix="/platform", tags=["platform"])
api_router.include_router(services.router, prefix="/services", tags=["services"])
api_router.include_router(applications.router, prefix="/applications", tags=["applications"])
api_router.include_router(organisations.router, prefix="/organisations", tags=["organisations"])
api_router.include_router(support.router, prefix="/support", tags=["support"])
api_router.include_router(poc.router, prefix="/poc", tags=["poc"])
