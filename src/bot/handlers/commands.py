"""Command handlers for Telegram bot."""

from aiogram import Router
from aiogram.filters import Command
from aiogram.types import Message

from src.database.repositories import UserRepository
from src.database.session import get_session
from src.database.models import Topic
from src.core.logger import get_logger

logger = get_logger(__name__)

router = Router(name="commands")


@router.message(Command("start"))
async def cmd_start(message: Message) -> None:
    """Handle /start command - show welcome message and subscription options."""
    async with get_session() as session:
        user_repo = UserRepository(session)

        # Check if user exists
        user = await user_repo.get_by_telegram_id(message.from_user.id)

        if not user:
            # Create new user
            user = await user_repo.create(
                telegram_id=message.from_user.id,
                subscriptions=[Topic.LLM_GENERAL],
            )
            await session.commit()

    # Show welcome message with inline keyboard
    from ..keyboards.digest import get_topic_keyboard

    await message.answer(
        f"👋 Добро пожаловать в <b>AI Papers Digest Bot</b>!\n\n"
        f"Я помогаю вам быть в курсе последних научных статей о LLM и AI в нефтегазовой отрасли.\n\n"
        "Выберите темы для подписки:\n\n"
        "• 📊 <b>LLM General</b> - Промпт-инжиниринг, архитектура LLM\n"
        "• 🛢️ <b>LLM в НГ</b> - LLM в геологии, геофизике, бурении\n"
        "• 🤖 <b>ИИ в НГ</b> - Все применения ИИ/ML в нефтегазе\n\n"
        "Используйте команду /digest чтобы получить свежие статьи.",
        reply_markup=get_topic_keyboard(user.subscriptions),
    )


@router.message(Command("help"))
async def cmd_help(message: Message) -> None:
    """Handle /help command."""
    await message.answer(
        "📚 <b>Доступные команды:</b>\n\n"
        "/start - Начать работу с ботом\n"
        "/help - Показать эту справку\n"
        "/digest [topic] - Получить свежие статьи\n"
        "/settings - Настройки уведомлений\n"
        "/weekly - Недельный обзор\n"
        "/monthly - Месячный отчет\n\n"
        "Используйте кнопки под сообщениями для переключения формата."
    )


@router.message(Command("digest"))
async def cmd_digest(message: Message) -> None:
    """Handle /digest command with optional topic argument."""
    # Parse topic from message text
    text = message.text or ""
    parts = text.split(maxsplit=1)

    topic_str = parts[1].strip().lower() if len(parts) > 1 else "llm_general"

    # Map string to Topic enum
    topic_map = {
        "llm_general": Topic.LLM_GENERAL,
        "llm_oil_gas": Topic.LLM_OIL_GAS,
        "ai_oil_gas": Topic.AI_OIL_GAS,
    }

    topic = topic_map.get(topic_str, Topic.LLM_GENERAL)
    await _send_digest(message, topic)


async def _send_digest(message: Message, topic: Topic) -> None:
    """Send digest for specific topic."""
    from ..keyboards.digest import get_digest_keyboard
    from src.database.repositories import AnalysisRepository

    async with get_session() as session:
        analysis_repo = AnalysisRepository(session)

        # Get top 5 papers with rating >= 80
        analyses = await analysis_repo.get_top_papers_by_topic(
            topic=topic,
            min_rating=80,
            limit=5,
        )

        if not analyses:
            await message.answer(
                f"📭 Нет свежих статей по теме <b>{topic.value}</b>.\n\n"
                "Попробуйте позже или выберите другую тему."
            )
            return

        # Send each paper
        for analysis in analyses:
            await _send_paper_digest(message.chat.id, analysis)


async def _send_paper_digest(chat_id: int, analysis) -> None:
    """Send formatted paper digest with inline buttons."""
    from aiogram import Bot
    from src.core.config import settings

    bot = Bot(token=settings.telegram_bot_token)

    text = _format_paper_message(analysis)

    # Send with inline keyboard for different formats
    from ..keyboards.digest import get_format_keyboard

    await bot.send_message(
        chat_id=chat_id,
        text=text,
        parse_mode="HTML",
        reply_markup=get_format_keyboard(analysis.id),
    )


def _format_paper_message(analysis) -> str:
    """Format paper analysis for Telegram message."""
    paper = analysis.paper

    rating_stars = "⭐" * (analysis.rating // 20)

    return (
        f"{rating_stars} <b>{paper.title}</b>\n\n"
        f"📊 <b>Рейтинг:</b> {analysis.rating}/100\n"
        f"📅 <b>Дата:</b> {paper.published_date.strftime('%d.%m.%Y')}\n"
        f"🏷️ <b>Тема:</b> {analysis.topic.value}\n\n"
        f"📝 <b>Суть:</b>\n{analysis.digest_text or 'Анализ в процессе...'}\n\n"
        f"➡️ <a href='{paper.arxiv_url}'>Читать на arXiv</a>"
    )


@router.message(Command("settings"))
async def cmd_settings(message: Message) -> None:
    """Handle /settings command."""
    from ..keyboards.settings import get_settings_keyboard
    from src.database.repositories import UserRepository
    from src.database.session import get_session

    async with get_session() as session:
        user_repo = UserRepository(session)
        user = await user_repo.get_by_telegram_id(message.from_user.id)

        if not user:
            await message.answer("❌ Пользователь не найден. Используйте /start")
            return

        await message.answer(
            "⚙️ <b>Настройки</b>\n\n"
            f"Еажедневный дайджест: {'✅' if user.daily_digest_enabled else '❌'}\n"
            f"Еженедельный обзор: {'✅' if user.weekly_digest_enabled else '❌'}\n"
            f"Месячный отчет: {'✅' if user.monthly_digest_enabled else '❌'}\n\n"
            f"Время уведомлений: {user.daily_digest_time}\n\n"
            "Выберите действие:",
            reply_markup=get_settings_keyboard(user),
        )
