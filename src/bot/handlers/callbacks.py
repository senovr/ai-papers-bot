"""Callback query handlers for Telegram bot."""

from aiogram import Router
from aiogram.types import CallbackQuery

from src.database.repositories import UserRepository
from src.database.session import get_session
from src.database.models import Topic

router = Router(name="callbacks")


# Topic subscription callbacks
@router.callback_query(lambda c: c.data.startswith("sub_"))
async def cb_subscribe(callback: CallbackQuery) -> None:
    """Handle topic subscription."""
    topic_str = callback.data.split("_")[1]
    topic = Topic(topic_str)

    async with get_session() as session:
        user_repo = UserRepository(session)
        user = await user_repo.get_by_telegram_id(callback.from_user.id)

        if not user:
            user = await user_repo.create(telegram_id=callback.from_user.id)

        # Toggle subscription
        if topic in user.subscriptions:
            user.subscriptions.remove(topic)
            status = "отписаны от"
        else:
            user.subscriptions.append(topic)
            status = "подписаны на"

        await user_repo.update(user, subscriptions=user.subscriptions)
        await session.commit()

        # Update keyboard
        from ..keyboards.digest import get_topic_keyboard

        await callback.message.edit_text(
            f"✅ Вы {status} тему <b>{topic.value}</b>",
            reply_markup=get_topic_keyboard(user.subscriptions),
        )


# Format change callbacks
@router.callback_query(lambda c: c.data == "format_digest")
async def cb_format_digest(callback: CallbackQuery) -> None:
    """Show digest format."""
    _analysis_id = int(callback.data.split("_")[2])

    # TODO: Get analysis from DB and send digest
    await callback.answer("📋 Дайджест загружается...")


@router.callback_query(lambda c: c.data == "format_simple")
async def cb_format_simple(callback: CallbackQuery) -> None:
    """Show simple format."""
    _analysis_id = int(callback.data.split("_")[2])

    # TODO: Get analysis from DB and send simple text
    await callback.answer("📝 Простое объяснение загружается...")


@router.callback_query(lambda c: c.data == "format_concepts")
async def cb_format_concepts(callback: CallbackQuery) -> None:
    """Show concepts format."""
    _analysis_id = int(callback.data.split("_")[2])

    # TODO: Get concepts from DB and send
    await callback.answer("💡 Концепты загружаются...")


# Settings callbacks
@router.callback_query(lambda c: c.data == "settings_daily")
async def cb_settings_daily(callback: CallbackQuery) -> None:
    """Toggle daily digest."""
    async with get_session() as session:
        user_repo = UserRepository(session)
        user = await user_repo.get_by_telegram_id(callback.from_user.id)

        if user:
            user.daily_digest_enabled = not user.daily_digest_enabled
            await user_repo.update(user, daily_digest_enabled=user.daily_digest_enabled)
            await session.commit()

            status = "включен" if user.daily_digest_enabled else "выключен"
            await callback.answer(f"✅ Ежедневный дайджест {status}")


@router.callback_query(lambda c: c.data == "settings_weekly")
async def cb_settings_weekly(callback: CallbackQuery) -> None:
    """Toggle weekly digest."""
    async with get_session() as session:
        user_repo = UserRepository(session)
        user = await user_repo.get_by_telegram_id(callback.from_user.id)

        if user:
            user.weekly_digest_enabled = not user.weekly_digest_enabled
            await user_repo.update(user, weekly_digest_enabled=user.weekly_digest_enabled)
            await session.commit()

            status = "включен" if user.weekly_digest_enabled else "выключен"
            await callback.answer(f"✅ Еженедельный обзор {status}")


@router.callback_query(lambda c: c.data == "settings_monthly")
async def cb_settings_monthly(callback: CallbackQuery) -> None:
    """Toggle monthly digest."""
    async with get_session() as session:
        user_repo = UserRepository(session)
        user = await user_repo.get_by_telegram_id(callback.from_user.id)

        if user:
            user.monthly_digest_enabled = not user.monthly_digest_enabled
            await user_repo.update(user, monthly_digest_enabled=user.monthly_digest_enabled)
            await session.commit()

            status = "включен" if user.monthly_digest_enabled else "выключен"
            await callback.answer(f"✅ Месячный отчет {status}")
