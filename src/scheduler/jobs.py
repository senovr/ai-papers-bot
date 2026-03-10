"""APScheduler integration for automated digest generation."""

import asyncio
from datetime import datetime, timedelta
from typing import Optional

from apscheduler.schedulers.asyncio import AsyncIOScheduler
from apscheduler.triggers.cron import CronTrigger
from apscheduler.triggers.interval import IntervalTrigger
from aiogram import Bot

from src.core.config import settings
from src.core.logger import get_logger
from src.database.models import Topic
from src.database.session import get_db_session
from src.pipeline.arxiv_fetcher import ArxivFetcher
from src.pipeline.pre_filter import PreFilter
from src.pipeline.deep_scorer import DeepScorer
from src.pipeline.summarizer import Summarizer
from src.pipeline.concept_extractor import ConceptExtractor
from src.pipeline.storage import PaperStorage
from src.pipeline.notifier import Notifier
from src.llm.zai_client import ZaiClient

logger = get_logger(__name__)


class JobScheduler:
    """Manage scheduled jobs for paper processing."""

    def __init__(self, bot: Optional[Bot] = None):
        self.scheduler = AsyncIOScheduler()
        self.llm_client = ZaiClient()
        self.bot = bot

        # Initialize pipeline components
        self.fetcher = ArxivFetcher()
        self.pre_filter = PreFilter(self.llm_client)
        self.deep_scorer = DeepScorer(self.llm_client)
        self.summarizer = Summarizer(self.llm_client)
        self.concept_extractor = ConceptExtractor(self.llm_client)
        self.notifier = Notifier(bot) if bot else None

        logger.info("JobScheduler initialized")

    async def run_pipeline(
        self,
        topic: Topic,
        days_back: int = 1,
        limit: int = 500,
    ) -> tuple[list[int], list[int]]:
        """Run the complete processing pipeline for a topic.

        Args:
            topic: Topic to process
            days_back: How many days back to fetch
            limit: Maximum papers to fetch

        Returns:
            Tuple of (paper_ids, analysis_ids)
        """
        logger.info(f"Starting pipeline for {topic.value}")

        try:
            # Stage 1: Fetch papers from arXiv
            papers = await self.fetcher.fetch_papers(topic=topic.value, days_back=days_back)
            logger.info(f"Fetched {len(papers)} papers for {topic.value}")

            # Limit papers
            papers = papers[:limit]

            # Stage 2: Pre-filter
            filtered = await self.pre_filter.filter(
                papers=papers,
                min_score=50,
                topic=topic,
            )
            logger.info(f"Pre-filtered: {len(filtered)}/{len(papers)} papers")

            # Stage 3: Deep scoring
            scored = await self.deep_scorer.score(
                papers=filtered,
                min_practical=50,
                min_novelty=30,
                min_total=70,
            )
            logger.info(f"Scored: {len(scored)}/{len(filtered)} papers")

            # Stage 4: Summarize
            summarized = await self.summarizer.summarize(
                papers=scored,
                style="digest",
                topic=topic,
            )
            logger.info(f"Summarized: {len(summarized)}/{len(scored)} papers")

            # Stage 5: Extract concepts
            processed_count = 0
            for paper in summarized:
                try:
                    # extract() accepts single paper dict, returns paper with 'concepts' added
                    result = await self.concept_extractor.extract(papers=paper)
                    # result is a dict when input is a single paper
                    if isinstance(result, dict):
                        paper["concepts"] = result.get("concepts", [])
                    processed_count += 1
                except Exception as e:
                    logger.error(f"Error extracting concepts: {e}")
                    paper["concepts"] = []

            logger.info(f"Concept extraction complete: {processed_count} papers processed")

            # Stage 6: Store to database
            async with get_db_session() as session:
                storage = PaperStorage(session)
                paper_ids, analysis_ids = await storage.store(
                    papers=summarized,
                    topic=topic,
                )
            logger.info(f"Stored {len(paper_ids)} papers, {len(analysis_ids)} analyses")

            # Stage 7: Notify users
            if self.bot and self.notifier:
                # Get analyses for notification
                async with get_db_session() as session:
                    storage = PaperStorage(session)
                    analyses = await storage.get_analyses_by_ids(analysis_ids)
                    await self.notifier.send_daily_digest(
                        analyses=analyses,
                        topic=topic,
                    )
                    logger.info("Sent digest to users")
            else:
                logger.warning("Bot or notifier not initialized, skipping notifications")

            # Stage 8: Cleanup
            await self.fetcher.close()

            return paper_ids, analysis_ids

        except Exception as e:
            logger.error(f"Pipeline error for {topic.value}: {e}")
            return [], []

    def start(self):
        """Start all scheduled jobs."""
        # Every 6 hours: fetch papers for each topic
        for topic in Topic:
            self.scheduler.add_job(
                self.run_pipeline,
                "interval",
                hours=6,
                id=f"fetch_papers_{topic.value}",
                args=[topic],
            )
            logger.info(f"Scheduled fetch job for {topic.value}")

        # Daily at 9:00: daily digest
        self.scheduler.add_job(
            self._send_daily_digests,
            "cron",
            hour=9,
            id="daily_digest",
        )
        logger.info("Scheduled daily digest job")

        # Weekly on Sunday 10:00
        self.scheduler.add_job(
            self._send_weekly_digests,
            "cron",
            day_of_week="sun",
            hour=10,
            id="weekly_digest",
        )
        logger.info("Scheduled weekly digest job")

        # Monthly on 1st at 10:00
        self.scheduler.add_job(
            self._send_monthly_digests,
            "cron",
            day=1,
            hour=10,
            id="monthly_digest",
        )
        logger.info("Scheduled monthly digest job")

        self.scheduler.start()
        logger.info("Job scheduler started")

    async def stop(self):
        """Stop all scheduled jobs."""
        self.scheduler.shutdown()
        logger.info("Job scheduler stopped")

    async def _send_daily_digests(self):
        """Send daily digests for all topics."""
        for topic in Topic:
            try:
                async with get_db_session() as session:
                    storage = PaperStorage(session)
                    # Get today's analyses
                    now = datetime.now()
                    today_start = now.replace(hour=0, minute=0, second=0, microsecond=0)
                    analyses = await storage.get_analyses_by_topic(
                        topic=topic,
                        since=today_start,
                        limit=50,
                    )

                    if analyses and self.notifier:
                        await self.notifier.send_daily_digest(
                            analyses=analyses,
                            topic=topic,
                        )
            except Exception as e:
                logger.error(f"Error in daily digest for {topic.value}: {e}")

    async def _send_weekly_digests(self):
        """Send weekly summaries for all topics."""
        for topic in Topic:
            try:
                async with get_db_session() as session:
                    storage = PaperStorage(session)
                    # Get week's papers
                    now = datetime.now()
                    week_ago = now - timedelta(days=7)
                    analyses = await storage.get_analyses_by_topic(
                        topic=topic,
                        since=week_ago,
                        limit=20,
                    )
                    if analyses and self.notifier:
                        await self.notifier.send_weekly_digest(
                            analyses=analyses,
                            topic=topic,
                        )
            except Exception as e:
                logger.error(f"Error in weekly digest for {topic.value}: {e}")

    async def _send_monthly_digests(self):
        """Send monthly essays for all topics."""
        for topic in Topic:
            try:
                async with get_db_session() as session:
                    storage = PaperStorage(session)
                    # Get month's papers
                    now = datetime.now()
                    month_ago = now - timedelta(days=30)
                    analyses = await storage.get_analyses_by_topic(
                        topic=topic,
                        since=month_ago,
                        limit=30,
                    )
                    if analyses and self.notifier:
                        # TODO: Generate comprehensive monthly essay
                        await self.notifier.send_weekly_digest(
                            analyses=analyses,
                            topic=topic,
                        )
            except Exception as e:
                logger.error(f"Error in monthly digest for {topic.value}: {e}")
