"""Configuración local del backend; las claves nunca salen de este proceso."""
from __future__ import annotations
from functools import lru_cache
from pathlib import Path
from pydantic_settings import BaseSettings, SettingsConfigDict

ROOT = Path(__file__).resolve().parents[2]

class Settings(BaseSettings):
    app_name: str = "Asistente Académico UNIANDES"
    app_env: str = "development"
    cors_origins: str = "http://localhost:5173"
    ai_provider: str = "gemini"
    ai_model: str = "gemini-3.5-flash-lite"
    fallback_provider: str = "openai"
    fallback_model: str = "gpt-4.1-mini"
    gemini_api_key: str | None = None
    openai_api_key: str | None = None
    llm_timeout_seconds: float = 15
    llm_retries: int = 0
    llm_max_input_chars: int = 2000
    admin_username: str = 'admin'
    admin_password: str = ''
    admin_cookie_secure: bool = False
    admin_session_minutes: int = 60
    model_config = SettingsConfigDict(env_file=ROOT / ".env", extra="ignore")

    @property
    def origins(self) -> list[str]:
        return [origin.strip() for origin in self.cors_origins.split(",") if origin.strip()]

@lru_cache
def get_settings() -> Settings:
    return Settings()
