"""Google Gemini client (stub/fallback)."""

from typing import Any, Optional

from src.core.config import settings
from src.llm.base_client import BaseLLMClient


class GeminiClient(BaseLLMClient):
    """Client for Google Gemini API (stub implementation).

    This is a fallback when ZAI provider is preferred.
    Used primarily for fast pre-filtering of papers.
    """

    def __init__(self, api_key: Optional[str] = None, model: str = "gemini-2.0-flash"):
        self.api_key = api_key or settings.google_api_key
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
        # TODO: Implement actual Gemini API call if needed
        return f"[Gemini Stub] Would analyze: {prompt[:100]}..."

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
            "note": "Gemini stub - implement if needed",
        }

    async def is_relevant(self, abstract: str) -> bool:
        """Fast relevance check (stub)."""
        # TODO: Implement actual fast relevance check
        # For now, use heuristics
        keywords = [
            "prompt",
            "LLM",
            "GPT",
            "language model",
            "reasoning",
            "RAG",
            "retrieval",
            "chain-of-thought",
            "geology",
            "geophysics",
            "drilling",
            "seismic",
            "oil",
            "gas",
            "petroleum",
            "reservoir",
        ]
        abstract_lower = abstract.lower()
        return any(kw in abstract_lower for kw in keywords)

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
