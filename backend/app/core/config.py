import os
from typing import List, Union
from pydantic_settings import BaseSettings
from pydantic import AnyHttpUrl, field_validator

class Settings(BaseSettings):
    PROJECT_NAME: str = "FlowForge AI"
    API_V1_STR: str = "/api"

    # Security
    SECRET_KEY: str = os.environ.get("SECRET_KEY", "CHANGEME_SECRET_KEY")
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = int(os.environ.get("ACCESS_TOKEN_EXPIRE_MINUTES", "1440")) # 24 hours

    # MongoDB
    MONGO_URL: str = os.environ.get("MONGO_URL", "mongodb://localhost:27017")
    DB_NAME: str = os.environ.get("DB_NAME", "flowforge_ai")

    # POC Control
    ENABLE_POC_ENDPOINTS: bool = os.environ.get("ENABLE_POC_ENDPOINTS", "false").lower() == "true"

    # AI Integration
    EMERGENT_LLM_KEY: Union[str, None] = os.environ.get("EMERGENT_LLM_KEY", None)

    # CORS
    BACKEND_CORS_ORIGINS: List[AnyHttpUrl] = []

    @field_validator("BACKEND_CORS_ORIGINS", mode="before")
    @classmethod
    def assemble_cors_origins(cls, v: Union[str, List[str]]) -> Union[List[str], str]:
        if isinstance(v, str) and not v.startswith("["):
            return [i.strip() for i in v.split(",")]
        elif isinstance(v, (list, str)):
            return v
        return v

    class Config:
        case_sensitive = True

settings = Settings()
