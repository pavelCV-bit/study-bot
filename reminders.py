"""Ежедневные напоминания. Вызывается по расписанию (cron) или командой /check."""

import config
import db
import view


async def send_due_reminders(bot) -> int:
    """Отправляет одно сообщение со всеми задачами, у которых пора напомнить. Возвращает их число."""
    today = config.today()
    due = []
    for task in await db.list_open_tasks():
        d = view.deadline_of(task)
        if d is None:
            continue
        left = (d - today).days
        already = task.get("last_reminded_on") == today.isoformat()
        if left in config.REMIND_DAYS_BEFORE and not already:
            due.append((left, task))

    if not due:
        return 0

    await bot.send_message(config.OWNER_ID, view.render_reminder(due))
    await db.mark_reminded([t["id"] for _, t in due], today)
    return len(due)
