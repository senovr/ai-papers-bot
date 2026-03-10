"""Inline keyboards for digest messages."""

from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from src.database.models import Topic


def get_topic_keyboard(subscriptions: list[Topic]) -> InlineKeyboardMarkup:
    """Create keyboard for topic selection."""
    buttons = []

    for topic in Topic:
        emoji = {
            Topic.LLM_GENERAL: "📊",
            Topic.LLM_OIL_GAS: "🛢️",
            Topic.AI_OIL_GAS: "🤖",
        }[topic]

        is_subscribed = topic in subscriptions
        status = "✅" if is_subscribed else "❌"

        buttons.append(
            [
                InlineKeyboardButton(
                    text=f"{emoji} {topic.value} {status}",
                    callback_data=f"sub_{topic.value}",
                )
            ]
        )

    buttons.append([InlineKeyboardButton(text="✅ Готово", callback_data="sub_done")])

    return InlineKeyboardMarkup(inline_keyboard=buttons)


def get_format_keyboard(analysis_id: int) -> InlineKeyboardMarkup:
    """Create keyboard for format selection."""
    return InlineKeyboardMarkup(
        inline_keyboard=[
            [
                InlineKeyboardButton(
                    text="📄 Дайджест", callback_data=f"format_digest_{analysis_id}"
                ),
                InlineKeyboardButton(
                    text="💬 Простыми словами", callback_data=f"format_simple_{analysis_id}"
                ),
            ],
            [
                InlineKeyboardButton(
                    text="💡 Концепты", callback_data=f"format_concepts_{analysis_id}"
                ),
            ],
        ]
    )
