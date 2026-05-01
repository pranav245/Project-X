from pydantic_settings import BaseSettings
from functools import lru_cache


class Settings(BaseSettings):
    # VAPI
    VAPI_API_KEY: str = ""
    VAPI_WEBHOOK_SECRET: str = ""

    # Sarvam AI
    SARVAM_API_KEY: str = ""
    SARVAM_STT_URL: str = "https://api.sarvam.ai/speech-to-text"
    SARVAM_TTS_URL: str = "https://api.sarvam.ai/text-to-speech"
    SARVAM_LID_URL: str = "https://api.sarvam.ai/text-lid"
    SARVAM_DEFAULT_VOICE: str = "meera"

    # LLM — switch provider + model freely via .env
    # Supported providers: anthropic, openai, groq, together-ai, openrouter
    LLM_PROVIDER: str = "anthropic"
    LLM_MODEL: str = "claude-haiku-4-5"
    LLM_API_KEY: str = ""

    # Telnyx
    TELNYX_API_KEY: str = ""
    TELNYX_CONNECTION_ID: str = ""

    # Database
    DATABASE_URL: str = "postgresql+asyncpg://user:pass@localhost:5432/projectsole"

    # App
    APP_ENV: str = "development"
    SECRET_KEY: str = "change-me-in-production"
    BACKEND_URL: str = "http://localhost:8000"

    # Sentry
    SENTRY_DSN: str = ""

    model_config = {"env_file": ".env", "extra": "ignore"}


@lru_cache
def get_settings() -> Settings:
    return Settings()
