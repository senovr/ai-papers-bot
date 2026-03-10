"""Base LLM client with common interface."""

from abc import ABC, abstractmethod
from typing import Any, Optional


class BaseLLMClient(ABC):
    """Abstract base class for LLM clients."""

    @abstractmethod
    async def complete(
        self,
        prompt: str,
        system_prompt: Optional[str] = None,
        max_tokens: int = 4000,
        temperature: float = 0.0,
        **kwargs: Any,
    ) -> str:
        """Generate completion from LLM.

        Args:
            prompt: User prompt
            system_prompt: System instructions
            max_tokens: Maximum tokens to generate
            temperature: Sampling temperature (0.0 = deterministic)
            **kwargs: Provider-specific parameters

        Returns:
            Generated text response
        """
        pass

    @abstractmethod
    async def complete_json(
        self,
        prompt: str,
        system_prompt: Optional[str] = None,
        max_tokens: int = 2000,
        **kwargs: Any,
    ) -> dict:
        """Generate JSON completion from LLM.

        Args:
            prompt: User prompt
            system_prompt: System instructions
            max_tokens: Maximum tokens to generate
            **kwargs: Provider-specific parameters

        Returns:
            Parsed JSON dict
        """
        pass

    @abstractmethod
    async def is_relevant(self, abstract: str) -> bool:
        """Fast relevance check for paper abstract.

        Args:
            abstract: Paper abstract to check

        Returns:
            True if paper is relevant
        """
        pass

    @abstractmethod
    async def score_paper(
        self,
        title: str,
        abstract: str,
        full_text: Optional[str] = None,
    ) -> dict:
        """Deep scoring for paper quality and relevance.

        Args:
            title: Paper title
            abstract: Paper abstract
            full_text: Full paper text (optional)

        Returns:
            {
                "rating": 0-100,
                "practical_score": 0-40,
                "novelty_score": 1-30,
                "quality_score": 1-30,
                "is_relevant": bool,
            }
        """
        pass

    @abstractmethod
    async def generate_summary(
        self,
        title: str,
        abstract: str,
        full_text: Optional[str] = None,
        style: str = "digest",  # "digest", "simple", "concepts"
    ) -> str:
        """Generate summary in specified style.

        Args:
            title: Paper title
            abstract: Paper abstract
            full_text: Full paper text (optional)
            style: Summary style ("digest", "simple", "concepts")

        Returns:
            Generated summary text
        """
        pass

    @abstractmethod
    async def extract_concepts(
        self,
        title: str,
        abstract: str,
        full_text: Optional[str] = None,
    ) -> list[dict]:
        """Extract atomic concepts from paper.

        Args:
            title: Paper title
            abstract: Paper abstract
            full_text: Full paper text (optional)

        Returns:
            [
                {
                    "type": "problem" | "thesis" | "method",
                    "title": str,
                    "explanation": str,
                    "example": str (optional)
                },
                ...
            ]
        """
        pass
