import logging
from typing import List, Dict, Type, TypeVar, Optional
from pydantic import BaseModel
import openai
from openai import OpenAI, AsyncOpenAI
from tenacity import retry, stop_after_attempt, wait_exponential, retry_if_exception_type, before_sleep_log

from src.core.config import load_config, Settings
from src.core.exceptions import LLMError
from src.core.logging import get_logger

logger = get_logger(__name__)

T = TypeVar("T", bound=BaseModel)

# Configured retry decorator for transient API anomalies
openai_retry = retry(
    reraise=True,
    stop=stop_after_attempt(3),
    wait=wait_exponential(multiplier=1.5, min=2, max=10),
    retry=(
        retry_if_exception_type(openai.RateLimitError)
        | retry_if_exception_type(openai.APIConnectionError)
        | retry_if_exception_type(openai.InternalServerError)
    ),
    before_sleep=before_sleep_log(logger.logger, logging.WARNING)
)


class LLMClientManager:
    """
    Wraps the OpenAI clients, providing robust sync and async interfaces 
    with automatic Pydantic parsing and API retry handling.
    """
    def __init__(self, settings: Optional[Settings] = None):
        self._settings = settings
        self._sync_client: Optional[OpenAI] = None
        self._async_client: Optional[AsyncOpenAI] = None

    @property
    def settings(self) -> Settings:
        """Lazily retrieves configurations when needed."""
        if self._settings is None:
            self._settings = load_config()
        return self._settings

    @property
    def sync_client(self) -> OpenAI:
        """Lazily instantiates the synchronous OpenAI client."""
        if self._sync_client is None:
            api_key = self.settings.openai_api_key.get_secret_value()
            self._sync_client = OpenAI(api_key=api_key)
        return self._sync_client

    @property
    def async_client(self) -> AsyncOpenAI:
        """Lazily instantiates the asynchronous OpenAI client."""
        if self._async_client is None:
            api_key = self.settings.openai_api_key.get_secret_value()
            self._async_client = AsyncOpenAI(api_key=api_key)
        return self._async_client

    @openai_retry
    def parse_completion(self, messages: List[Dict[str, str]], response_format: Type[T]) -> T:
        """
        Submits a synchronous chat completion request with structured Pydantic format.
        """
        try:
            completion = self.sync_client.beta.chat.completions.parse(
                model=self.settings.model_name,
                messages=messages,
                response_format=response_format,
            )
            result = completion.choices[0].message.parsed
            if result is None:
                raise LLMError("OpenAI API response returned empty structured contents.")
            return result
        except openai.OpenAIError as e:
            logger.error("OpenAI API call encountered error during synchronous request", error=str(e))
            raise LLMError(f"LLM API failure: {e}") from e
        except Exception as e:
            logger.error("Unexpected failure processing synchronous completion", error=str(e))
            raise LLMError(f"Unexpected completion issue: {e}") from e

    @openai_retry
    async def aparse_completion(self, messages: List[Dict[str, str]], response_format: Type[T]) -> T:
        """
        Submits an asynchronous chat completion request with structured Pydantic format.
        """
        try:
            completion = await self.async_client.beta.chat.completions.parse(
                model=self.settings.model_name,
                messages=messages,
                response_format=response_format,
            )
            result = completion.choices[0].message.parsed
            if result is None:
                raise LLMError("OpenAI API response returned empty structured contents in async mode.")
            return result
        except openai.OpenAIError as e:
            logger.error("OpenAI API call encountered error during asynchronous request", error=str(e))
            raise LLMError(f"Async LLM API failure: {e}") from e
        except Exception as e:
            logger.error("Unexpected failure processing asynchronous completion", error=str(e))
            raise LLMError(f"Unexpected async completion issue: {e}") from e
