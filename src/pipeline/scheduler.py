"""Schedule daily/weekly/monthly digest generation."""

from datetime import datetime, timedelta
from typing import Optional

from src.core.logger import get_logger
from src.database.models import Topic
from src.database.repositories import AnalysisRepository
from src.database.repositories import UserRepository

from src.database.session import get_db_session

logger = get_logger(__name__)


class DigestScheduler:
    """Schedule digest generation and distribution."""

    def __init__(self):
        self._jobs = {}

    async def run_daily_digest(
        self,
        topic: Topic,
        min_rating: int = 80,
        limit: int = 10,
    ) -> list[int]:
        """
        Generate and send daily digest.

        Args:
            topic: Topic to generate digest for
            min_rating: Minimum paper rating
            limit: Maximum papers to include

        Returns:
            List of user IDs who received the digest
        """
        logger.info(f"Running daily digest for topic: {topic.value}")

        async with get_db_session() as session:
            # Get top papers
            analysis_repo = AnalysisRepository(session)
            user_repo = UserRepository(session)

            analyses = await analysis_repo.get_top_papers_by_topic(
                topic=topic,
                min_rating=min_rating,
                limit=limit,
            )

            if not analyses:
                logger.info(f"No papers found for daily digest")
                return []

            # Get subscribers
            subscribers = await user_repo.get_subscribers_for_topic(
                topic=topic,
                daily_digest=True,
            )

            if not subscribers:
                logger.info(f"No subscribers for topic: {topic.value}")
                return []

            # TODO: Send digest to each subscriber
            # This will be implemented in TelegramNotifier

            user_ids = [u.telegram_id for u in subscribers]
            logger.info(f"Daily digest ready for {len(user_ids)} users")

            return user_ids

    async def run_weekly_summary(
        self,
        topic: Topic,
        days: int = 7,
    ) -> str:
        """
        Generate weekly narrative summary.

        Args:
            topic: Topic to generate summary for
            days: Number of days to include

        Returns:
            Weekly summary text
        """
        logger.info(f"Running weekly summary for topic: {topic.value}")

        async with get_db_session() as session:
            analysis_repo = AnalysisRepository(session)

            # Get papers from last N days
            # TODO: Implement date filtering
            analyses = await analysis_repo.get_top_papers_by_topic(
                topic=topic,
                min_rating=70,
                limit=50,
            )

            if not analyses:
                logger.info(f"No papers for weekly summary")
                return ""

            # TODO: Generate narrative summary using LLM
            # This would use the LLM client to create a narrative

            summary = f"# Еженедельный дайджест: {topic.value}\n\n"
            summary += f"Топ-{len(analyses)} статей за неделю.\n\n"

            for analysis in analyses[:10]:
                paper = analysis.paper
                summary += f"- **{paper.title}** (Рейтинг: {analysis.rating})\n"

            logger.info(f"Weekly summary generated: {len(summary)} chars")

            return summary

    async def run_monthly_essay(
        self,
        topic: Topic,
    ) -> str:
        """
        Generate monthly narrative essay.

        Args:
            topic: Topic to generate essay for

        Returns:
            Monthly essay text
        """
        logger.info(f"Running monthly essay for topic: {topic.value}")

        # TODO: Implement monthly essay generation
        # This would use LLM client to create a long-form narrative

        essay = f"# Ежемесячный обзор: {topic.value}\n\n"
        essay += "Обзор ключевых трендов и инсайтов за месяц.\n\n"

        logger.info(f"Monthly essay generated: {len(essay)} chars")

        return essay
