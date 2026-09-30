"""Запуск бота на своём ПК для теста (без Vercel): python run_local.py"""
import asyncio
import logging

from core import COMMANDS, make_bot, make_dispatcher


async def main():
    logging.basicConfig(level=logging.INFO)
    bot = make_bot()
    await bot.delete_webhook()          # на время локального запуска отключаем вебхук
    await bot.set_my_commands(COMMANDS)
    print("Бот запущен. Напиши ему в Telegram. Остановить: Ctrl+C")
    await make_dispatcher().start_polling(bot)


if __name__ == "__main__":
    asyncio.run(main())
