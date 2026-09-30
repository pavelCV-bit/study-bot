"""Как бот выглядит: тексты сообщений, эмодзи, кнопки. Меняешь внешний вид — правь этот файл."""
import html
from datetime import date

from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup

import config

WEEKDAYS = ["пн", "вт", "ср", "чт", "пт", "сб", "вс"]
WEEKDAYS_FULL = ["понедельник", "вторник", "среда", "четверг", "пятница", "суббота", "воскресенье"]


def deadline_of(task: dict) -> date | None:
    return date.fromisoformat(task["deadline"]) if task.get("deadline") else None


def days_left(deadline: date) -> int:
    return (deadline - config.today()).days


def marker(days: int) -> str:
    if days <= config.URGENT_DAYS:
        return "🔴"
    if days <= config.SOON_DAYS:
        return "🟡"
    return "🟢"


def left_text(days: int) -> str:
    if days < 0:
        return f"просрочено на {-days} дн."
    if days == 0:
        return "сегодня"
    if days == 1:
        return "завтра"
    return f"через {days} дн."


def date_text(d: date) -> str:
    return f"{d:%d.%m} ({WEEKDAYS[d.weekday()]})"


def help_text() -> str:
    days = ", ".join(str(d) for d in config.REMIND_DAYS_BEFORE)
    return (
        "👋 <b>Бот для учёбы</b>\n\n"
        "Просто напиши задачу обычным текстом, например:\n"
        "<i>сделать код в коллабе до конца октября, заметка: там ещё графики</i>\n\n"
        "/tasks — список задач (🔴 срочно, 🟡 скоро, 🟢 не горит)\n"
        "/check — проверить напоминания прямо сейчас\n"
        "/help — эта подсказка\n\n"
        f"Каждое утро напоминаю за столько дней до дедлайна: {days}."
    )


def render_list(tasks: list[dict]) -> tuple[str, InlineKeyboardMarkup | None]:
    if not tasks:
        return "🎉 Открытых задач нет.\nНапиши новую — например: «лаба по физике до пятницы»", None

    lines = [f"📚 <b>Задачи ({len(tasks)})</b>", ""]
    rows = []
    for i, t in enumerate(tasks, 1):
        d = deadline_of(t)
        title = html.escape(t["title"])
        if d:
            n = days_left(d)
            lines.append(f"{i}. {marker(n)} <b>{title}</b>")
            lines.append(f"└ до {date_text(d)} — {left_text(n)}")
        else:
            lines.append(f"{i}. ⚪ <b>{title}</b>")
            lines.append("└ без срока")
        if t.get("note"):
            lines.append(f"📝 <i>{html.escape(t['note'])}</i>")
        lines.append("")

        short = t["title"][:14] + ("…" if len(t["title"]) > 14 else "")
        rows.append([
            InlineKeyboardButton(text=f"✅ {i}. {short}", callback_data=f"done:{t['id']}"),
            InlineKeyboardButton(text="🗑", callback_data=f"del:{t['id']}"),
        ])
    return "\n".join(lines).rstrip(), InlineKeyboardMarkup(inline_keyboard=rows)


def render_saved(task: dict) -> tuple[str, InlineKeyboardMarkup]:
    d = deadline_of(task)
    lines = [f"✅ Сохранил: <b>{html.escape(task['title'])}</b>"]
    if d:
        lines.append(f"📅 До {date_text(d)} — {left_text(days_left(d))}")
    else:
        lines.append("📅 Без срока")
    if task.get("note"):
        lines.append(f"📝 <i>{html.escape(task['note'])}</i>")
    lines.append("\nПонял не так? Нажми «Отменить» и напиши иначе.")
    kb = InlineKeyboardMarkup(inline_keyboard=[[
        InlineKeyboardButton(text="↩️ Отменить", callback_data=f"undo:{task['id']}"),
        InlineKeyboardButton(text="📋 Все задачи", callback_data="list"),
    ]])
    return "\n".join(lines), kb


def render_reminder(items: list[tuple[int, dict]]) -> str:
    """items — список (сколько дней осталось, задача)."""
    lines = ["⏰ <b>Напоминание о дедлайнах</b>", ""]
    for n, t in sorted(items, key=lambda x: x[0]):
        d = deadline_of(t)
        lines.append(f"{marker(n)} <b>{html.escape(t['title'])}</b> — {left_text(n)}, {date_text(d)}")
        if t.get("note"):
            lines.append(f"📝 <i>{html.escape(t['note'])}</i>")
    lines.append("\nВсе задачи: /tasks")
    return "\n".join(lines)
