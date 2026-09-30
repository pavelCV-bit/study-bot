"""Точка входа для Vercel: принимает сообщения от Telegram (/api/webhook)
и запускается по расписанию для напоминаний (/api/cron)."""
import logging

from aiogram.types import Update
from fastapi import FastAPI, Header, HTTPException, Request

import config
import reminders
from core import make_bot, make_dispatcher

logging.basicConfig(level=logging.INFO)
log = logging.getLogger(__name__)

app = FastAPI()
dp = make_dispatcher()


@app.get("/")
async def health():
    return {"ok": True}


@app.post("/api/webhook")
async def webhook(request: Request, x_telegram_bot_api_secret_token: str | None = Header(default=None)):
    if not config.WEBHOOK_SECRET or x_telegram_bot_api_secret_token != config.WEBHOOK_SECRET:
        raise HTTPException(status_code=403)

    bot = make_bot()
    try:
        update = Update.model_validate(await request.json(), context={"bot": bot})
        await dp.feed_update(bot, update)
    except Exception:
        # Всегда отвечаем 200, иначе Telegram будет бесконечно повторять запрос
        log.exception("update failed")
    finally:
        await bot.session.close()
    return {"ok": True}


@app.get("/api/cron")
async def cron(authorization: str | None = Header(default=None)):
    if not config.CRON_SECRET or authorization != f"Bearer {config.CRON_SECRET}":
        raise HTTPException(status_code=401)

    bot = make_bot()
    try:
        sent = await reminders.send_due_reminders(bot)
    finally:
        await bot.session.close()
    return {"ok": True, "reminded": sent}
