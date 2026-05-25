class AppError(Exception):
    """Base exception for all AI Ops Document Assistant errors."""
    pass


class ConfigurationError(AppError):
    """Raised when there is an issue with the application configuration."""
    pass


class IngestionError(AppError):
    """Raised when document ingestion or parsing fails."""
    pass


class ChunkingError(AppError):
    """Raised when splitting document text into chunks fails."""
    pass


class LLMError(AppError):
    """Raised when an API call or parsing of LLM response fails."""
    pass


class ExtractionError(AppError):
    """Raised when the orchestrator fails to run the extraction pipeline."""
    pass
