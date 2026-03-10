"""Telegram bot main module."""

import logging
from typing import AsyncIterator

from aiogram import Bot, Dispatcher
from aiogram.enums import ParseMode
from aiogram.webhook.aiohttp_server import SimpleRequestHandler, WebRequestHandler
from aiohttp import web

from src.core.config import settings

logger = logging.getLogger(__name__)


async def create_bot() -> AsyncIterator[Bot]:
    """Create and configure bot instance."""
    bot = Bot(
        token=settings.telegram_bot_token,
        parse_mode=ParseMode.HTML,
    )

    # Test connection
    try:
        me = await bot.get_me()
        logger.info(f"Bot started: @{me.username} (ID: {me.id})")
    except Exception as e:
        logger.error(f"Failed to connect to Telegram: {e}")
        raise

    yield bot

    # Cleanup
    await bot.session.close()


def create_dispatcher() -> Dispatcher:
    """Create dispatcher with all handlers."""
    dp = Dispatcher()

    # Register handlers
    from src.bot.handlers import commands, callbacks

    dp.include_router(commands.router)
    dp.include_router(callbacks.router)

    logger.info("Dispatcher configured with all handlers")
    return dp


async def start_polling(bot: Bot, dp: Dispatcher) -> None:
    """Start bot in polling mode (development)."""
    logger.info("Starting bot in polling mode...")
    await dp.start_polling(bot, allowed_updates=dp.resolve_used_update_types())


async def start_webhook(
    bot: Bot,
    dp: Dispatcher,
    webhook_path: str = "/webhook",
    webhook_url: str | None = None,
) -> None:
    """Start bot in webhook mode (production)."""
    from aiohttp import web

    if webhook_url is None:
        webhook_url = f"{settings.webhook_url}{webhook_path}"

    logger.info(f"Starting bot in webhook mode at {webhook_url}")

    # Set webhook
    await bot.set_webhook(webhook_url)

    # Create aiohttp app
    app = web.Application()
    webhook_handler = SimpleRequestHandler(dispatcher=dp, bot=bot)
    webhook_handler.register(app, path=webhook_path)

    # Start server
    runner = web.AppRunner(app)
    await runner.setup()
    site = web.TCPSite(runner, host="0.0.0.0", port=settings.webhook_port)
    await site.start()

    logger.info(f"Webhook server started on port {settings.webhook_port}")
