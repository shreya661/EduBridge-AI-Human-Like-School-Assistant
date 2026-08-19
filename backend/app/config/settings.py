"""Environment-backed application settings."""

import os
from pathlib import Path

from dotenv import load_dotenv
from pydantic import BaseModel, ConfigDict, SecretStr, field_validator


_ENV_FILE = Path(__file__).resolve().parents[2] / ".env"
load_dotenv(_ENV_FILE, override=False)


class Settings(BaseModel):
    """Runtime settings loaded from environment variables."""

    model_config = ConfigDict(frozen=True)

    app_name: str = "XYZ AI"
    environment: str = "development"
    llm_provider: str | None = None
    llm_model: str | None = None
    llm_api_key: SecretStr | None = None
    llm_base_url: str | None = None
    llm_timeout_seconds: float = 20.0

    @field_validator("llm_provider", "llm_model", "llm_base_url", mode="before")
    @classmethod
    def empty_strings_are_unset(cls, value: str | None) -> str | None:
        if isinstance(value, str) and not value.strip():
            return None
        return value

    @field_validator("llm_api_key", mode="before")
    @classmethod
    def empty_api_key_is_unset(cls, value: str | None) -> str | None:
        if isinstance(value, str) and not value.strip():
            return None
        return value

    @classmethod
    def from_environment(cls) -> "Settings":
        """Create settings without exposing secrets in application logs."""
        return cls(
            app_name=os.getenv("APP_NAME", "XYZ AI"),
            environment=os.getenv("ENVIRONMENT", "development"),
            llm_provider=os.getenv("LLM_PROVIDER"),
            llm_model=os.getenv("LLM_MODEL"),
            llm_api_key=os.getenv("LLM_API_KEY"),
            llm_base_url=os.getenv("LLM_BASE_URL"),
            llm_timeout_seconds=os.getenv("LLM_TIMEOUT_SECONDS", "20"),
        )


def get_settings() -> Settings:
    """Return settings for the current process environment."""
    return Settings.from_environment()
