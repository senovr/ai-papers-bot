"""Command handlers for Telegram bot."""

from aiogram import Router
from aiogram.filters import Command
from aiogram.types import Message

from src.database.repositories import UserRepository
from src.database.session import get_db_session
from src.database.models import Topic
from src.core.logger import get_logger

from ..keyboards.digest import get_topic_keyboard

from ..keyboards.settings import get_settings_keyboard

logger = get_logger(__name__)

router = Router(name="commands")


@router.message(Command("start"))
async def cmd_start(message: Message) -> None:
    """Handle /start command - show welcome message and subscription options."""
    if message.from_user is None:
        await message.answer("❌ Cannot identify user")
        return

    async with get_db_session() as session:
        user_repo = UserRepository(session)

        user = await user_repo.get_by_telegram_id(message.from_user.id)

        if not user:
            user = await user_repo.create(
                telegram_id=message.from_user.id,
                subscriptions=[Topic.LLM_GENERAL],
            )
            await session.commit()

    await message.answer(
        "👋 Добро пожаловать в <b>AI Papers Digest Bot</b>!\n\n"
        "Я помогаю вам быть в курсе последних научных статей о LLM и AI в нефтегазовой отрасли.\n\n"
        "Выберите темы для подписки:\n\n"
        "• 📊 <b>LLM General</b> - Промпт-инжиниринг, архитектура LLM\n"
        "• 🛢️ <b>LLM в НГ</b> - LLM в геологии, геофизике, бурении\n"
        "• 🤖 <b>ИИ в НГ</b> - Все применения ИИ/ML в нефтегазе отрасли\n\n"
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
    text = message.text or ""
    parts = text.split(maxsplit=1)

    if len(parts) > 1:
        topic_str = parts[1].strip().lower()
    else:
        topic_str = "llm_general"

    topic_map = {
        "llm_general": Topic.LLM_GENERAL,
        "llm_oil_gas": Topic.LLM_OIL_GAS,
        "ai_oil_gas": Topic.AI_OIL_GAS,
    }

    topic = topic_map.get(topic_str, Topic.LLM_GENERAL)
    await _send_digest(message, topic)


async def _send_digest(message: Message, topic: Topic) -> None:
    """Send digest for specific topic."""
    from src.database.repositories import AnalysisRepository

    from ..keyboards.digest import get_format_keyboard
    from aiogram import Bot
    from src.core.config import settings

    async with get_db_session() as session:
        analysis_repo = AnalysisRepository(session)

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

        bot = Bot(token=settings.telegram_bot_token)
        for analysis in analyses:
            paper = analysis.paper
            rating_stars = "⭐" * (analysis.rating // 20)
            text = (
                f"{rating_stars} <b>{paper.title}</b>\n\n"
                f"📊 <b>Рейтинг:</b> {analysis.rating}/100\n"
                f"📅 <b>Дата:</b> {paper.published_date.strftime('%d.%m.%Y')}\n"
                f"🏷️ <b>Тема:</b> {analysis.topic.value}\n\n"
                f"📝 <b>Суть:</b>\n{analysis.digest_text or 'Анализ в процессе...'}\n\n"
                f"➡️ <a href='{paper.arxiv_url}'>Читать на arXiv</a>"
            )
            await bot.send_message(
                chat_id=message.chat.id,
                text=text,
                parse_mode="HTML",
                reply_markup=get_format_keyboard(analysis.id),
            )


@router.message(Command("settings"))
async def cmd_settings(message: Message) -> None:
    """Handle /settings command."""
    if message.from_user is None:
        await message.answer("❌ Cannot identify user")
        return

    async with get_db_session() as session:
        user_repo = UserRepository(session)
        user = await user_repo.get_by_telegram_id(message.from_user.id)

        if not user:
            await message.answer("❌ Пользователь не найден. Используйте /start")
            return

        await message.answer(
            "⚙️ <b>Настройки</b>\n\n"
            f"Ежедневный дайджест: {'✅' if user.daily_digest_enabled else '❌'}\n"
            f"Еженедельный обзор: {'✅' if user.weekly_digest_enabled else '❌'}\n"
            f"Месячный отчет: {'✅' if user.monthly_digest_enabled else '❌'}\n\n"
            f"Время уведомлений: {user.daily_digest_time}\n\n"
            "Выберите действие:",
            reply_markup=get_settings_keyboard(user),
        )
