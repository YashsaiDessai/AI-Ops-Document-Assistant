from functools import lru_cache
from pydantic_settings import BaseSettings, SettingsConfigDict
from pydantic import Field, SecretStr, ValidationError
from src.core.exceptions import ConfigurationError
from src.core.logging import get_logger

logger = get_logger(__name__)


class Settings(BaseSettings):
    """
    Configuration management using Pydantic.
    Reads from environment variables with the prefix 'OPS_'
    (e.g., OPS_OPENAI_API_KEY).
    """
    model_config = SettingsConfigDict(
        env_prefix="OPS_",
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore"
    )

    openai_api_key: SecretStr = Field(..., description="API key for OpenAI services")
    model_name: str = Field("gpt-4-turbo", description="Target LLM Model")
    chunk_size: int = Field(1000, description="Target character/token size for chunks")


@lru_cache
def load_config() -> Settings:
    """
    Cached config loader.
    """
    try:
        return Settings()
    except ValidationError as e:
        logger.error("Failed to load configuration. Verify that OPS_OPENAI_API_KEY is set in .env or environment variables.")
        raise ConfigurationError(
            "Application configuration validation failed. Check your environment setup."
        ) from e
