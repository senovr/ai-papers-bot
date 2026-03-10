"""Repository pattern for database access."""

from typing import Optional

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from src.database.models import Analysis, Concept, Paper, Topic, User


class BaseRepository:
    """Base repository with common operations."""

    def __init__(self, session: AsyncSession):
        self.session = session


class UserRepository(BaseRepository):
    """Repository for User model."""

    async def get_by_telegram_id(self, telegram_id: int) -> Optional[User]:
        """Get user by Telegram ID."""
        result = await self.session.execute(select(User).where(User.telegram_id == telegram_id))
        return result.scalar_one_or_none()

    async def create(self, telegram_id: int, **kwargs) -> User:
        """Create new user."""
        user = User(telegram_id=telegram_id, **kwargs)
        self.session.add(user)
        await self.session.flush()
        return user

    async def update(self, user: User, **kwargs) -> User:
        """Update user."""
        for key, value in kwargs.items():
            setattr(user, key, value)
        await self.session.flush()
        return user

    async def get_subscribers_for_topic(
        self, topic: Topic, daily_digest: bool = True
    ) -> list[User]:
        """Get all active users subscribed to a topic."""
        result = await self.session.execute(
            select(User).where(
                User.is_active == True,
                User.subscriptions.contains([topic]),
                User.daily_digest_enabled == daily_digest,
            )
        )
        return result.scalars().all()


class PaperRepository(BaseRepository):
    """Repository for Paper model."""

    async def get_by_arxiv_id(self, arxiv_id: str) -> Optional[Paper]:
        """Get paper by arXiv ID."""
        result = await self.session.execute(select(Paper).where(Paper.arxiv_id == arxiv_id))
        return result.scalar_one_or_none()

    async def create(self, **kwargs) -> Paper:
        """Create new paper."""
        paper = Paper(**kwargs)
        self.session.add(paper)
        await self.session.flush()
        return paper

    async def get_recent_papers(self, limit: int = 100, offset: int = 0) -> list[Paper]:
        """Get recent papers."""
        result = await self.session.execute(
            select(Paper).order_by(Paper.published_date.desc()).limit(limit).offset(offset)
        )
        return result.scalars().all()


class AnalysisRepository(BaseRepository):
    """Repository for Analysis model."""

    async def get_by_paper_and_topic(self, paper_id: int, topic: Topic) -> Optional[Analysis]:
        """Get analysis by paper and topic."""
        result = await self.session.execute(
            select(Analysis).where(
                Analysis.paper_id == paper_id,
                Analysis.topic == topic,
            )
        )
        return result.scalar_one_or_none()

    async def create(self, **kwargs) -> Analysis:
        """Create new analysis."""
        analysis = Analysis(**kwargs)
        self.session.add(analysis)
        await self.session.flush()
        return analysis

    async def get_top_papers_by_topic(
        self, topic: Topic, min_rating: int = 80, limit: int = 10
    ) -> list[Analysis]:
        """Get top papers by rating for a topic."""
        result = await self.session.execute(
            select(Analysis)
            .where(
                Analysis.topic == topic,
                Analysis.rating >= min_rating,
            )
            .order_by(Analysis.rating.desc())
            .limit(limit)
        )
        return result.scalars().all()


class ConceptRepository(BaseRepository):
    """Repository for Concept model."""

    async def get_by_analysis(self, analysis_id: int) -> list[Concept]:
        """Get all concepts for an analysis."""
        result = await self.session.execute(
            select(Concept).where(Concept.analysis_id == analysis_id).order_by(Concept.id)
        )
        return result.scalars().all()

    async def create(self, **kwargs) -> Concept:
        """Create new concept."""
        concept = Concept(**kwargs)
        self.session.add(concept)
        await self.session.flush()
        return concept

    async def bulk_create(self, concepts_data: list[dict]) -> list[Concept]:
        """Create multiple concepts."""
        concepts = [Concept(**data) for data in concepts_data]
        self.session.add_all(concepts)
        await self.session.flush()
        return concepts
