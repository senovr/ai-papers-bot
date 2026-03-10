"""Extract atomic concepts from papers."""

from typing import Union

from src.core.logger import get_logger
from src.llm.base_client import BaseLLMClient

logger = get_logger(__name__)


class ConceptExtractor:
    """Extract atomic concepts from paper content."""

    def __init__(self, llm_client: BaseLLMClient):
        self.llm = llm_client

    async def extract(
        self,
        papers: Union[list[dict], dict],
    ) -> Union[list[dict], dict]:
        """
        Extract concepts from papers.

        Args:
            papers: Single paper dict or list of paper dicts
                    Each paper needs 'abstract', 'title', and optionally 'full_text'

        Returns:
            Single paper or list of papers with 'concepts' field added
        """
        # Handle single paper case
        single_mode = isinstance(papers, dict)
        if single_mode:
            papers = [papers]

        if not papers:
            logger.warning("No papers to extract concepts from")
            return papers[0] if single_mode else papers

        result = []
        for paper in papers:
            try:
                # Extract concepts using LLM
                concepts = await self.llm.extract_concepts(
                    title=paper["title"],
                    abstract=paper["abstract"],
                    full_text=paper.get("full_text"),
                )

                paper["concepts"] = concepts
                result.append(paper)

                logger.debug(
                    f"Extracted {len(concepts)} concepts from {paper.get('arxiv_id', 'unknown')}"
                )

            except Exception as e:
                logger.error(
                    f"Error extracting concepts from {paper.get('arxiv_id', 'unknown')}: {e}"
                )
                paper["concepts"] = []
                result.append(paper)

        logger.info(f"Concept extraction complete: {len(result)} papers processed")

        # Return single paper if input was single
        return result[0] if single_mode else result
