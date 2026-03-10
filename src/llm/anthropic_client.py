"""Anthropic Claude client (stub/fallback)."""

from typing import Any, Optional

from src.core.config import settings
from src.llm.base_client import BaseLLMClient


class AnthropicClient(BaseLLMClient):
    """Client for Anthropic Claude API (stub implementation).

    This is a fallback when ZAI provider is preferred.
    Implements the same interface as ZaiClient.
    """

    def __init__(self, api_key: Optional[str] = None, model: str = "claude-sonnet-4-20250514"):
        self.api_key = api_key or settings.anthropic_api_key
        self.model = model
        self._client = None

    async def complete(
        self,
        prompt: str,
        system_prompt: Optional[str] = None,
        max_tokens: int = 4000,
        temperature: float = 1.0,
        **kwargs: Any,
    ) -> str:
        """Stub: Return placeholder response."""
        # TODO: Implement actual Anthropic API call if needed
        return f"[Anthropic Stub] Would analyze: {prompt[:100]}..."

    async def complete_json(
        self,
        prompt: str,
        system_prompt: Optional[str] = None,
        max_tokens: int = 2000,
        **kwargs: Any,
    ) -> dict:
        """Stub: Return placeholder JSON."""
        return {
            "rating": 50,
            "is_relevant": True,
            "note": "Anthropic stub - implement if needed",
        }

    async def is_relevant(self, abstract: str) -> bool:
        """Stub: Always return True."""
        return True

    async def score_paper(
        self,
        title: str,
        abstract: str,
        full_text: Optional[str] = None,
    ) -> dict:
        """Stub: Return default scores."""
        return {
            "rating": 50,
            "practical_score": 20,
            "novelty_score": 15,
            "quality_score": 15,
            "is_relevant": True,
        }

    async def generate_summary(
        self,
        title: str,
        abstract: str,
        full_text: Optional[str] = None,
        style: str = "digest",
    ) -> str:
        """Stub: Return placeholder summary."""
        return f"[Stub Summary for: {title}]"

    async def extract_concepts(
        self,
        title: str,
        abstract: str,
        full_text: Optional[str] = None,
    ) -> list[dict]:
        """Stub: Return empty concepts list."""
        return []
