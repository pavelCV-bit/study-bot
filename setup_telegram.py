"""Один раз после деплоя: python setup_telegram.py https://твой-проект.vercel.app
Подключает бота к Vercel и включает меню команд."""
import asyncio
import sys

import config
from core import COMMANDS, make_bot


async def main():
    if len(sys.argv) < 2:
        print("Использование: python setup_telegram.py https://твой-проект.vercel.app")
        return
    if not config.WEBHOOK_SECRET:
        print("В .env не задан WEBHOOK_SECRET")
        return
    url = sys.argv[1].rstrip("/") + "/api/webhook"
    bot = make_bot()
    try:
        await bot.set_webhook(url=url, secret_token=config.WEBHOOK_SECRET, drop_pending_updates=True)
        await bot.set_my_commands(COMMANDS)
        info = await bot.get_webhook_info()
        print("Готово. Вебхук:", info.url)
    finally:
        await bot.session.close()


if __name__ == "__main__":
    asyncio.run(main())
