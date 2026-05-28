"""PatchPilot configuration — loads settings from environment variables."""

from pathlib import Path
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """Application settings loaded from .env file and environment variables."""

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
        extra="ignore",
    )

    # ── GitHub ────────────────────────────────────────────────────────────────
    github_token: str = ""

    # ── AI Provider ───────────────────────────────────────────────────────────
    gemini_api_key: str = ""
    ai_model: str = "gemini-2.5-pro"

    # ── PatchPilot ────────────────────────────────────────────────────────────
    repos_dir: str = "./repos"

    # ── Server ────────────────────────────────────────────────────────────────
    host: str = "0.0.0.0"
    port: int = 8000
    debug: bool = False

    @property
    def repos_path(self) -> Path:
        """Return repos directory as a resolved Path."""
        path = Path(self.repos_dir)
        path.mkdir(parents=True, exist_ok=True)
        return path.resolve()


settings = Settings()
