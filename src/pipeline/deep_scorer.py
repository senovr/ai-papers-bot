"""Deep scoring for LLM for paper quality."""

from typing import Optional

from src.core.config import settings
from src.core.logger import get_logger
from src.database.models import Topic
from src.database.repositories import AnalysisRepository
from src.database.repositories import PaperRepository
from src.llm.base_client import BaseLLMClient

logger = get_logger(__name__)


class DeepScorer:
    """Deep scoring using LLM for paper quality."""

    def __init__(self, llm_client: BaseLLMClient):
        self.llm_client = llm_client

    async def score(
        self,
        papers: list[dict],
        min_practical: int = 50,
        min_novelty: int = 30,
        min_total: int = 70,
        limit: int = 100,
    ) -> list[dict]:
        """
        Score papers using deep LLM analysis.

        Args:
            papers: List of paper dicts to score
            min_practical: Minimum practical score (1-40)
            min_novelty: Minimum novelty score (1-30)
            min_total: Minimum total score (1-100)

            topic: Optional topic to filter by specific topic

        Returns:
            Scored papers with total_score >= min_total
        """
        if not papers:
            logger.warning("No papers to score")
            return []

        logger.info(f"Scoring {len(papers)} papers")

        scored = []
        for paper in papers:
            try:
                result = await self.llm_client.score_paper(
                    title=paper["title"],
                    abstract=paper["abstract"],
                    full_text=paper.get("full_text"),
                )

                # Validate scores
                total = result.get("rating", 0)
                if total < min_total:
                    logger.debug(f"Filtered out: {paper['arxiv_id']} - score {total}")
                    continue

                # Add to result
                paper["rating"] = total
                paper["practical_score"] = result.get("practical_score", 0)
                paper["novelty_score"] = result.get("novelty_score", 0)
                paper["quality_score"] = result.get("quality_score", 0)
                paper["is_relevant"] = result.get("is_relevant", True)

                scored.append(paper)

                logger.debug(f"Scored: {paper['arxiv_id']} - {total}/100")

            except Exception as e:
                logger.error(f"Error scoring paper {paper.get('arxiv_id')}: {e}")
                paper["rating"] = 0
                paper["is_relevant"] = False

        # Sort by total score
        scored.sort(key=lambda p: p.get("rating", 0), reverse=True)

        # Limit results
        result = scored[:limit]

        logger.info(
            f"Scoring complete: {len(result)} papers above {min_total} score "
            f"(from {len(papers)} total)"
        )

        return result
