"""SQLAlchemy database models."""

import enum
from datetime import datetime
from typing import Optional

from sqlalchemy import (
    ARRAY,
    Boolean,
    DateTime,
    Enum,
    ForeignKey,
    Integer,
    String,
    Text,
    func,
)
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column, relationship


class Topic(str, enum.Enum):
    """Topics for paper categorization."""

    LLM_GENERAL = "llm_general"
    LLM_OIL_GAS = "llm_oil_gas"
    AI_OIL_GAS = "ai_oil_gas"


class Base(DeclarativeBase):
    """Base class for all models."""

    pass


class User(Base):
    """User model for Telegram bot users."""

    __tablename__ = "users"

    telegram_id: Mapped[int] = mapped_column(Integer, primary_key=True)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        onupdate=func.now(),
    )
    is_active: Mapped[bool] = mapped_column(Boolean, default=True)
    settings: Mapped[dict] = mapped_column(JSONB, default=dict)
    subscriptions: Mapped[list] = mapped_column(
        ARRAY(Enum(Topic)),
        default=[Topic.LLM_GENERAL],
    )
    daily_digest_enabled: Mapped[bool] = mapped_column(Boolean, default=True)
    weekly_digest_enabled: Mapped[bool] = mapped_column(Boolean, default=True)
    monthly_digest_enabled: Mapped[bool] = mapped_column(Boolean, default=True)
    daily_digest_time: Mapped[str] = mapped_column(String(5), default="09:00")

    # Relationships
    analyses: Mapped[list["Analysis"]] = relationship(
        "Analysis",
        back_populates="user",
        cascade="all, delete-orphan",
    )

    def __repr__(self) -> str:
        return f"<User(telegram_id={self.telegram_id})>"


class Paper(Base):
    """Paper model for arXiv papers."""

    __tablename__ = "papers"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    arxiv_id: Mapped[str] = mapped_column(String(20), unique=True, nullable=False, index=True)
    title: Mapped[str] = mapped_column(Text, nullable=False)
    abstract: Mapped[Optional[str]] = mapped_column(Text)
    authors: Mapped[Optional[list]] = mapped_column(ARRAY(String))
    published_date: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)
    arxiv_url: Mapped[str] = mapped_column(String(255), nullable=False)
    full_text_path: Mapped[Optional[str]] = mapped_column(String(500))
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
    )

    # Relationships
    analyses: Mapped[list["Analysis"]] = relationship(
        "Analysis",
        back_populates="paper",
        cascade="all, delete-orphan",
    )

    def __repr__(self) -> str:
        return f"<Paper(arxiv_id={self.arxiv_id}, title={self.title[:50]}...)"


class Analysis(Base):
    """Analysis model for LLM-processed papers."""

    __tablename__ = "analyses"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    paper_id: Mapped[int] = mapped_column(
        Integer, ForeignKey("papers.id", ondelete="CASCADE"), nullable=False
    )
    user_id: Mapped[Optional[int]] = mapped_column(
        Integer, ForeignKey("users.telegram_id", ondelete="SET NULL")
    )

    topic: Mapped[Topic] = mapped_column(Enum(Topic), nullable=False, index=True)
    rating: Mapped[int] = mapped_column(Integer, nullable=False)  # 0-100
    practical_score: Mapped[int] = mapped_column(Integer, default=0)  # 0-40
    novelty_score: Mapped[int] = mapped_column(Integer, default=0)  # 0-30
    quality_score: Mapped[int] = mapped_column(Integer, default=0)  # 0-30

    digest_text: Mapped[Optional[str]] = mapped_column(Text)
    simple_text: Mapped[Optional[str]] = mapped_column(Text)

    processed_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
    )

    # Relationships
    paper: Mapped["Paper"] = relationship("Paper", back_populates="analyses")
    user: Mapped[Optional["User"]] = relationship("User", back_populates="analyses")
    concepts: Mapped[list["Concept"]] = relationship(
        "Concept",
        back_populates="analysis",
        cascade="all, delete-orphan",
    )

    def __repr__(self) -> str:
        return f"<Analysis(id={self.id}, paper_id={self.paper_id}, rating={self.rating})>"


class Concept(Base):
    """Concept model for atomic knowledge extraction."""

    __tablename__ = "concepts"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    analysis_id: Mapped[int] = mapped_column(
        Integer,
        ForeignKey("analyses.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )

    concept_type: Mapped[str] = mapped_column(String(20), nullable=False)  # problem, thesis, method
    title: Mapped[str] = mapped_column(String(255), nullable=False)
    explanation: Mapped[str] = mapped_column(Text, nullable=False)
    example: Mapped[Optional[str]] = mapped_column(Text)

    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
    )

    # Relationships
    analysis: Mapped["Analysis"] = relationship("Analysis", back_populates="concepts")

    def __repr__(self) -> str:
        return f"<Concept(id={self.id}, type={self.concept_type}, title={self.title[:30]}...)"
