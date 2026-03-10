"""Store papers and analyses in database."""

from datetime import datetime
from typing import Optional

from sqlalchemy.ext.asyncio import AsyncSession

from src.core.logger import get_logger
from src.database.models import Analysis, Concept, Paper, Topic
from src.database.repositories import (
    AnalysisRepository,
    ConceptRepository,
    PaperRepository,
)

logger = get_logger(__name__)


class PaperStorage:
    """Store papers and analyses in PostgreSQL."""

    def __init__(self, session: AsyncSession):
        self.session = session
        self.paper_repo = PaperRepository(session)
        self.analysis_repo = AnalysisRepository(session)
        self.concept_repo = ConceptRepository(session)

    async def store(
        self,
        papers: list[dict],
        topic: Topic,
    ) -> tuple[list[int], list[int]]:
        """
        Store papers and their analyses in database.

        Args:
            papers: List of paper dicts with all fields
            topic: Topic for analysis

        Returns:
            Tuple of (stored_paper_ids, stored_analysis_ids)
        """
        if not papers:
            logger.warning("No papers to store")
            return [], []

        logger.info(f"Storing {len(papers)} papers for topic {topic.value}")

        paper_ids: list[int] = []
        analysis_ids: list[int] = []

        for paper_data in papers:
            try:
                # Check if paper already exists
                existing_paper = await self.paper_repo.get_by_arxiv_id(paper_data["arxiv_id"])

                if existing_paper:
                    paper = existing_paper
                    logger.debug(f"Paper already exists: {paper_data['arxiv_id']}")
                else:
                    # Create new paper
                    paper = await self.paper_repo.create(
                        arxiv_id=paper_data["arxiv_id"],
                        title=paper_data["title"],
                        abstract=paper_data["abstract"],
                        url=paper_data["url"],
                        published_date=paper_data["published_date"],
                        full_text=paper_data.get("full_text"),
                    )

                paper_ids.append(paper.id)

                # Create analysis if we have scoring data
                if "rating" in paper_data or "summary" in paper_data:
                    analysis = await self.analysis_repo.create(
                        paper_id=paper.id,
                        topic=topic,
                        rating=paper_data.get("rating", 0),
                        practical_score=paper_data.get("practical_score", 0),
                        novelty_score=paper_data.get("novelty_score", 0),
                        quality_score=paper_data.get("quality_score", 0),
                        digest_text=paper_data.get("summary"),
                        simple_text=paper_data.get("simple_text"),
                    )
                    analysis_ids.append(analysis.id)

                    # Store concepts if we have them
                    if "concepts" in paper_data:
                        for concept_data in paper_data["concepts"]:
                            concept = await self.concept_repo.create(
                                analysis_id=analysis.id,
                                concept_type=concept_data.get("type", "insight"),
                                content=concept_data.get("content", ""),
                            )
                            logger.debug(f"Stored concept: {concept_data.get('type')}")

            except Exception as e:
                logger.error(f"Error storing paper {paper_data.get('arxiv_id')}: {e}")
                continue

        logger.info(f"Storage complete: {len(paper_ids)} papers, {len(analysis_ids)} analyses")

        return paper_ids, analysis_ids

    async def get_analyses_by_ids(self, analysis_ids: list[int]) -> list[Analysis]:
        """
        Get analyses by list of IDs.

        Args:
            analysis_ids: List of analysis IDs to fetch

        Returns:
            List of Analysis objects
        """
        if not analysis_ids:
            return []
        return await self.analysis_repo.get_by_ids(analysis_ids)

    async def get_analyses_by_topic(
        self,
        topic: Topic,
        since: datetime,
        limit: int = 50,
    ) -> list[Analysis]:
        """
        Get analyses for a topic created since a given datetime.

        Args:
            topic: Topic to filter by
            since: Datetime to filter from
            limit: Maximum number of analyses to return

        Returns:
            List of Analysis objects ordered by rating
        """
        return await self.analysis_repo.get_by_topic_since(
            topic=topic,
            since=since,
            limit=limit,
        )

    async def get_top_analyses(
        self,
        topic: Topic,
        min_rating: int = 80,
        limit: int = 10,
    ) -> list[Analysis]:
        """
        Get top-rated analyses for a topic.

        Args:
            topic: Topic to filter by
            min_rating: Minimum rating threshold
            limit: Maximum number of analyses to return

        Returns:
            List of top Analysis objects
        """
        return await self.analysis_repo.get_top_papers_by_topic(
            topic=topic,
            min_rating=min_rating,
            limit=limit,
        )
