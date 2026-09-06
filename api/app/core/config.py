import os
from typing import List
from pydantic import BaseModel, Field

try:
    from dotenv import load_dotenv
    _e = os.path.join(os.path.dirname(__file__), "..", "..", ".env")
    load_dotenv(dotenv_path=_e)
except ImportError:
    pass


class Settings(BaseModel):
    PROJECT_NAME: str = "SETU - Smart Government Procurement Portal"
    API_V1_STR: str = "/api/v1"
    DB_URL: str = Field(default_factory=lambda: os.getenv("DB_URL", "sqlite:///./setu.db"))
    JWT_SECRET: str = Field(default_factory=lambda: os.getenv("JWT_SECRET", "setu-secret"))
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 60 * 24
    APIFY_TOKEN: str = Field(default_factory=lambda: os.getenv("APIFY_TOKEN", ""))
    CORS_ORIGINS: List[str] = Field(
        default_factory=lambda: [
            o.strip() for o in os.getenv(
                "CORS_ORIGINS", "http://localhost:8000,http://127.0.0.1:8000"
            ).split(",") if o.strip()
        ]
    )


settings = Settings()
