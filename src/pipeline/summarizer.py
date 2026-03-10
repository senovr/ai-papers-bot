"""Paper summarization for different styles."""

from typing import Optional

from src.core.logger import get_logger
from src.database.models import Topic
from src.llm.base_client import BaseLLMClient

logger = get_logger(__name__)


class Summarizer:
    """Generate summaries in different styles."""

    STYLES = ["digest", "simple", "concepts"]

    def __init__(self, llm_client: BaseLLMClient):
        self.llm_client = llm_client

    async def summarize(
        self,
        papers: list[dict],
        style: str = "digest",
        topic: Optional[Topic] = None,
    ) -> list[dict]:
        """
        Generate summaries for papers.

        Args:
            papers: List of paper dicts with 'abstract', 'full_text', 'title'
            style: Summary style ("digest", "simple", "concepts")
            topic: Optional topic for context

        Returns:
            List of papers with 'summary' field added
        """
        if not papers:
            logger.warning("No papers to summarize")
            return []

        if style not in self.STYLES:
            logger.warning(f"Unknown style: {style}, using digest")
            style = "digest"

        logger.info(f"Generating {style} summaries for {len(papers)} papers")

        summarized = []
        for paper in papers:
            try:
                summary = await self.llm_client.generate_summary(
                    title=paper["title"],
                    abstract=paper["abstract"],
                    full_text=paper.get("full_text"),
                    style=style,
                )

                paper["summary"] = summary
                paper["summary_style"] = style
                summarized.append(paper)

                logger.debug(f"Summarized: {paper['arxiv_id']}")

            except Exception as e:
                logger.error(f"Error summarizing paper {paper.get('arxiv_id')}: {e}")
                paper["summary"] = None

        logger.info(f"Summarization complete: {len(summarized)} papers")

        return summarized
