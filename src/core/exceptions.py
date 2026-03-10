"""Custom exceptions for the application."""


class AIPapersBotError(Exception):
    """Base exception for all custom errors."""

    pass


class ArXivFetchError(AIPapersBotError):
    """Error during arXiv fetching."""

    pass


class LLMProcessingError(AIPapersBotError):
    """Error during LLM processing."""

    pass


class DatabaseError(AIPapersBotError):
    """Database-related error."""

    pass


class ConfigurationError(AIPapersBotError):
    """Configuration error."""

    pass


class RateLimitError(AIPapersBotError):
    """Rate limit exceeded error."""

    pass
