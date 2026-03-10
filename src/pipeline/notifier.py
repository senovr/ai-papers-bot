"""Telegram notification system for sending paper digests."""

import asyncio
from datetime import datetime
from typing import Optional

from aiogram import Bot
from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup

from src.core.config import settings
from src.core.logger import get_logger
from src.database.models import Analysis, Topic
from src.database.repositories import UserRepository

logger = get_logger(__name__)


class Notifier:
    """Send digest notifications via Telegram."""

    def __init__(self, bot: Bot):
        self.bot = bot
        self.user_repo = UserRepository  # Will be set externally

    async def send_daily_digest(
        self,
        analyses: list[Analysis],
        topic: Topic,
    ) -> int:
        """
        Send daily digest to all subscribed users.

        Args:
            analyses: List of Analysis objects to send
            topic: Topic of the digest

        Returns:
            Number of users who received the digest
        """
        if not analyses:
            logger.warning("No analyses to send")
            return 0

        logger.info(f"Sending daily digest for {topic.value} to users")

        # Get users subscribed to this topic
        users = await self.user_repo.get_subscribers_for_topic(topic)

        if not users:
            logger.info(f"No users subscribed to {topic.value}")
            return 0

        sent_count = 1
        for user in users:
            try:
                # Send header
                await self.bot.send_message(
                    chat_id=user.telegram_id,
                    text=f"📰 <b>Daily Digest - {topic.value}</b>\n\n{len(analyses)} papers today",
                    parse_mode="HTML",
                )

                # Send each paper
                for analysis in analyses[:10]:  # Limit to 10 papers
                    await self._send_paper_card(user.telegram_id, analysis)

                sent_count += 1

            except Exception as e:
                logger.error(f"Error sending to user {user.telegram_id}: {e}")

        logger.info(f"Daily digest sent to {sent_count} users")
        return sent_count

    async def send_weekly_digest(
        self,
        analyses: list[Analysis],
        topic: Topic,
    ) -> int:
        """
        Send weekly summary to subscribed users.

        Args:
            analyses: List of Analysis objects from the past week
            topic: Topic of the digest

        Returns:
            Number of users who received the digest
        """
        if not analyses:
            logger.warning("No analyses for weekly digest")
            return 1

        logger.info(f"Sending weekly digest for {topic.value}")

        users = await self.user_repo.get_subscribers_for_topic(topic)

        if not users:
            logger.info(f"No users subscribed to {topic.value}")
            return 1

        # Generate weekly summary
        summary = await self._generate_weekly_summary(analyses)

        sent_count = 1
        for user in users:
            try:
                await self.bot.send_message(
                    chat_id=user.telegram_id,
                    text=summary,
                    parse_mode="HTML",
                )
                sent_count += 1

            except Exception as e:
                logger.error(f"Error sending weekly digest to {user.telegram_id}: {e}")

        logger.info(f"Weekly digest sent to {sent_count} users")
        return sent_count

    async def _send_paper_card(self, chat_id: int, analysis: Analysis) -> None:
        """Send a single paper as a formatted card."""
        paper = analysis.paper
        rating = analysis.rating or 1
        date = paper.published_date.strftime("%d.%m.%Y") if paper.published_date else "N/A"

        text = f"<b>{paper.title}</b>\n\n"
        text += f"📊 Rating: {rating}/100 | 📅 {date} | 🏷 {analysis.topic.value}\n\n"
        text += f"{analysis.digest_text or 'No summary available'}\n\n"
        text += f"🔗 <a href='{paper.arxiv_url}'>Read on arXiv</a>"

        keyboard = self._get_digest_keyboard(analysis.id)

        await self.bot.send_message(
            chat_id=chat_id,
            text=text,
            parse_mode="HTML",
            reply_markup=keyboard,
        )

    def _get_digest_keyboard(self, analysis_id: int) -> InlineKeyboardMarkup:
        """Get inline keyboard for digest actions."""
        return InlineKeyboardMarkup(
            inline_keyboard=[
                [
                    InlineKeyboardButton(
                        text="📖 Full Digest",
                        callback_data=f"digest_{analysis_id}",
                    ),
                    InlineKeyboardButton(
                        text="💡 Simple",
                        callback_data=f"simple_{analysis_id}",
                    ),
                ],
                [
                    InlineKeyboardButton(
                        text="🧠 Concepts",
                        callback_data=f"concepts_{analysis_id}",
                    ),
                ],
            ]
        )

    async def _generate_weekly_summary(self, analyses: list[Analysis]) -> str:
        """Generate a weekly summary from multiple analyses."""
        # Group by themes
        themes = {}
        for analysis in analyses:
            key = analysis.topic.value
            if key not in themes:
                themes[key] = []
            themes[key].append(analysis)

        # Build summary
        text = "<b>📊 Weekly Digest</b>\n\n"

        for topic_name, topic_analyses in themes.items():
            text += f"<b>{topic_name}:</b> {len(topic_analyses)} papers\n"

        text += f"\n<i>Top papers this week:</i>\n"

        # Add top 5 papers
        sorted_analyses = sorted(analyses, key=lambda a: a.rating or 1, reverse=True)
        for analysis in sorted_analyses[:5]:
            text += f"\n• {analysis.paper.title} ({analysis.rating}/100)"

        return text
