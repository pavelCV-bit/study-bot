"""Что бот делает в ответ на команды, текст и нажатия кнопок."""
import html
import logging

from aiogram import F, Router
from aiogram.filters import Command
from aiogram.types import CallbackQuery, Message

import ai
import config
import db
import reminders
import view

log = logging.getLogger(__name__)

# Команда /id доступна всем — чтобы узнать свой Telegram ID при настройке.
public = Router()

# Всё остальное — только тебе (OWNER_ID). Чужим бот не отвечает.
router = Router()
router.message.filter(F.from_user.id == config.OWNER_ID)
router.callback_query.filter(F.from_user.id == config.OWNER_ID)


@public.message(Command("id"))
async def cmd_id(message: Message):
    await message.answer(f"Твой Telegram ID: <code>{message.from_user.id}</code>")


@router.message(Command("start", "help"))
async def cmd_help(message: Message):
    await message.answer(view.help_text())


@router.message(Command("tasks", "list"))
async def cmd_tasks(message: Message):
    text, kb = view.render_list(await db.list_open_tasks())
    await message.answer(text, reply_markup=kb)


@router.message(Command("check"))
async def cmd_check(message: Message):
    sent = await reminders.send_due_reminders(message.bot)
    if sent == 0:
        await message.answer("Проверил: сегодня напоминать не о чем 👌")


# Любой обычный текст (не команда) = новая задача
@router.message(F.text, ~F.text.startswith("/"))
async def on_text(message: Message):
    wait = await message.answer("⏳ Разбираю…")
    try:
        parsed = await ai.parse_task(message.text)
        task = await db.add_task(parsed["title"], parsed["deadline"], parsed["note"])
    except Exception as e:
        log.exception("add task failed")
        await wait.edit_text(f"❌ Не получилось: {html.escape(str(e))}")
        return
    text, kb = view.render_saved(task)
    await wait.edit_text(text, reply_markup=kb)


async def _show_list(message: Message):
    text, kb = view.render_list(await db.list_open_tasks())
    await message.edit_text(text, reply_markup=kb)


@router.callback_query(F.data == "list")
async def cb_list(cb: CallbackQuery):
    await cb.answer()
    await _show_list(cb.message)


@router.callback_query(F.data.startswith("done:"))
async def cb_done(cb: CallbackQuery):
    await db.set_done(int(cb.data.split(":")[1]))
    await cb.answer("Готово ✅")
    await _show_list(cb.message)


@router.callback_query(F.data.startswith("del:"))
async def cb_delete(cb: CallbackQuery):
    await db.delete_task(int(cb.data.split(":")[1]))
    await cb.answer("Удалено 🗑")
    await _show_list(cb.message)


@router.callback_query(F.data.startswith("undo:"))
async def cb_undo(cb: CallbackQuery):
    await db.delete_task(int(cb.data.split(":")[1]))
    await cb.answer("Отменено")
    await cb.message.edit_text("↩️ Отменил. Напиши задачу ещё раз, можно точнее.")
