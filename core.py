"""Сборка бота: создаём Bot и Dispatcher. Используется и локально, и на Vercel."""
from aiogram import Bot, Dispatcher
from aiogram.client.default import DefaultBotProperties
from aiogram.enums import ParseMode
from aiogram.types import BotCommand

import config
import handlers

COMMANDS = [
    BotCommand(command="tasks", description="Список задач"),
    BotCommand(command="check", description="Проверить напоминания"),
    BotCommand(command="help", description="Подсказка"),
]


def make_bot() -> Bot:
    return Bot(token=config.BOT_TOKEN, default=DefaultBotProperties(parse_mode=ParseMode.HTML))


def make_dispatcher() -> Dispatcher:
    dp = Dispatcher()
    dp.include_router(handlers.public)
    dp.include_router(handlers.router)
    return dp
