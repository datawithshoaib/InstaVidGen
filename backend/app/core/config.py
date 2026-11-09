"""Application settings, loaded from environment variables and `.env` files."""

from functools import lru_cache
from pathlib import Path

from pydantic import Field, SecretStr
from pydantic_settings import BaseSettings, SettingsConfigDict

BACKEND_DIR = Path(__file__).resolve().parents[2]
PROJECT_DIR = BACKEND_DIR.parent

DEFAULT_MODEL = "openai/gpt-oss-120b"


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        # Later files win: backend/.env overrides the project-root .env.
        env_file=(PROJECT_DIR / ".env", BACKEND_DIR / ".env"),
        env_file_encoding="utf-8",
        extra="ignore",
    )

    app_name: str = "InstaVidGen API"
    version: str = "3.0.0"

    # --- AI (Groq via LangChain) ---
    groq_api_key: SecretStr | None = None
    groq_model: str = DEFAULT_MODEL
    groq_models: list[str] = Field(
        default=[
            "openai/gpt-oss-120b",
            "openai/gpt-oss-20b",
            "llama-3.3-70b-versatile",
            "llama-3.1-8b-instant",
            "qwen/qwen3.8-27b",
        ],
        description="Models offered in the UI model picker.",
    )
    groq_temperature: float = Field(default=0.9, ge=0.0, le=2.0)
    groq_timeout_seconds: float = 60.0

    # --- HTTP ---
    port: int = 8002
    cors_origins: list[str] = ["http://localhost:3000", "http://127.0.0.1:3000"]

    # --- Filesystem ---
    assets_dir: Path = BACKEND_DIR / "assets"
    storage_dir: Path = BACKEND_DIR / "storage"

    # --- Rendering ---
    video_fps: int = 30
    batch_workers: int = Field(default=2, ge=1, le=8)

    @property
    def backgrounds_dir(self) -> Path:
        return self.assets_dir / "backgrounds"

    @property
    def fonts_dir(self) -> Path:
        return self.assets_dir / "fonts"

    @property
    def videos_dir(self) -> Path:
        return self.storage_dir / "videos"

    @property
    def posts_dir(self) -> Path:
        return self.storage_dir / "posts"

    @property
    def thumbnails_dir(self) -> Path:
        return self.storage_dir / "thumbnails"

    @property
    def groq_configured(self) -> bool:
        return bool(self.groq_api_key and self.groq_api_key.get_secret_value().strip())

    def ensure_directories(self) -> None:
        for directory in (self.videos_dir, self.posts_dir, self.thumbnails_dir):
            directory.mkdir(parents=True, exist_ok=True)


@lru_cache
def get_settings() -> Settings:
    return Settings()
