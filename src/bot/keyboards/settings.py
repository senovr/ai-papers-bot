"""Inline keyboards for settings."""

from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from src.database.models import User


def get_settings_keyboard(user: User) -> InlineKeyboardMarkup:
    """Create keyboard for settings."""
    daily_status = "✅" if user.daily_digest_enabled else "❌"
    weekly_status = "✅" if user.weekly_digest_enabled else "❌"
    monthly_status = "✅" if user.monthly_digest_enabled else "❌"

    return InlineKeyboardMarkup(
        inline_keyboard=[
            [
                InlineKeyboardButton(
                    text=f"📅 Ежедневный дайджест {daily_status}",
                    callback_data="settings_daily",
                ),
            ],
            [
                InlineKeyboardButton(
                    text=f"📊 Еженедельный обзор {weekly_status}",
                    callback_data="settings_weekly",
                ),
            ],
            [
                InlineKeyboardButton(
                    text=f"📈 Месячный отчет {monthly_status}",
                    callback_data="settings_monthly",
                ),
            ],
            [
                InlineKeyboardButton(text="🏷️ Управление темами", callback_data="settings_topics"),
            ],
        ]
    )
