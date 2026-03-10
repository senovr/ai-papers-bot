"""Pre-filter papers using LLM for fast relevance check."""

import json
import re
from typing import Optional

from src.core.config import settings
from src.core.logger import get_logger
from src.database.models import Topic
from src.llm.base_client import BaseLLMClient

logger = get_logger(__name__)


class PreFilter:
    """Fast pre-filter using LLM to reduce papers from ~5000 to ~600 daily."""

    def __init__(self, llm_client: BaseLLMClient):
        self.llm_client = llm_client

    async def filter(
        self,
        papers: list[dict],
        min_score: int = 50,
        topic: Optional[Topic] = None,
    ) -> list[dict]:
        """
        Filter papers using fast LLM check.

        Args:
            papers: List of paper dicts to filter
            min_score: Minimum relevance score (0-100)
            topic: Optional topic to filter by specific topic

        Returns:
            Filtered papers with score >= min_score
        """
        if not papers:
            logger.warning("No papers to filter")
            return []

        logger.info(
            f"Pre-filtering {len(papers)} papers | Topic: {topic.value if topic else 'all topics'}"
        )

        filtered = []
        for paper in papers:
            try:
                # Quick relevance check
                result = await self._quick_score(paper)
                score = result.get("score", 0)
                keep = result.get("keep", False)

                paper["relevance_score"] = score

                if keep and score >= min_score:
                    filtered.append(paper)
                    logger.debug(f"Kept: {paper.get('arxiv_id')} - score {score}")
                else:
                    logger.debug(f"Filtered out: {paper.get('arxiv_id')} - score {score}")

            except Exception as e:
                logger.error(f"Error filtering paper {paper.get('arxiv_id')}: {e}")
                paper["relevance_score"] = 0

        logger.info(
            f"Pre-filter complete: {len(filtered)}/{len(papers)} papers | "
            f"Topic: {topic.value if topic else 'all topics'}"
        )

        return filtered

    async def _quick_score(self, paper: dict) -> dict:
        """Quick score a paper using LLM."""
        # Use title and abstract for quick scoring
        prompt = f"""Rate this paper's relevance for practical LLM usage (not research/development):

Title: {paper.get("title", "")}
Abstract: {paper.get("abstract", "")[:500]}

Score 0-100 where:
- 80-100: Practical techniques, methods, benchmarks
- 50-79: Interesting but not immediately applicable
- 0-49: Theoretical, model training, infrastructure, CV-focused

Return ONLY: {{"score": <int>, "keep": <bool>}}"""

        try:
            response = await self.llm_client.complete(
                prompt=prompt,
                max_tokens=100,
                temperature=0.0,
            )

            # Parse JSON response
            if "{" in response:
                # Extract JSON from response
                match = re.search(r'\{"score":\s*(\d+),\s*"keep":\s*(true|false)\}', response)
                if match:
                    return json.loads(match.group(0))

            logger.warning(f"Failed to parse LLM response: {response[:100]}")
            return {"score": 0, "keep": False}

        except Exception as e:
            logger.error(f"Error in quick score: {e}")
            return {"score": 0, "keep": False}
