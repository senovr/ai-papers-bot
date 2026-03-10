"""Bot handlers package."""

from aiogram import Router

from . import callbacks, commands

__all__ = ["router"]

router = Router()

# Include sub-routers
router.include_router(commands.router)
router.include_router(callbacks.router)
