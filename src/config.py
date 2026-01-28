import logging
from functools import lru_cache
from pydantic_settings import BaseSettings, SettingsConfigDict
from pydantic import Field , SecretStr, ValidationError

logger = logging.getLogger(__name__)

class Settings(BaseSettings):
    """
    Configuration management using Pydantic.
    Reads from environment variables (eg., OPS_POENAI_API_KEY) )
    """
    model_config = SettingsConfigDict(
        env_prefix = "OPS_",
        env_file = ".env",
        env_file_encoding = "utf-8",
        extra = "ignore"
    )

    openai_api_key: SecretStr = Field(..., description="API key for OpenAI services")

    model_name: str = Field("gpt-4-turbo", description="Target LLM Model")
    chunk_size: int = Field(1000, description = "Target token size for chunks")

@lru_cache
def load_config() -> Settings:
    """
    Cached loader to prevent reading file I/O on every call.
    """

try:
    return Settings()
except ValidationError as e:
    logger.critical("Failed to load configuration. Check .env file or environment variables.")
    raise SystemExit(1)

settings = load_config()