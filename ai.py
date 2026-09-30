"""ИИ (Groq) превращает обычный текст в задание + дедлайн + заметку."""
import json
from datetime import date

import aiohttp

import config
from view import WEEKDAYS_FULL

GROQ_URL = "https://api.groq.com/openai/v1/chat/completions"

# Инструкция для ИИ. Хочешь изменить, как он понимает текст — правь здесь.
PROMPT = """Ты разбираешь сообщения студента про учебные задания.
Верни ТОЛЬКО JSON такого вида:
{"title": "...", "deadline": "YYYY-MM-DD" или null, "note": "..." или null}

Правила:
- Сегодня {today} ({weekday}).
- title: короткое название задания с заглавной буквы, без даты и без слов про заметку.
- deadline: дата дедлайна. «до конца октября» = последний день октября. «в пятницу» = ближайшая будущая пятница.
  «через неделю» = сегодня + 7 дней. Если года нет — берём ближайшую будущую дату. Если срока нет — null.
- note: всё, что похоже на пояснение или заметку («заметка: ...», «не забыть ...»). Если нет — null.
- Ничего не выдумывай."""


class AIError(Exception):
    pass


async def parse_task(text: str) -> dict:
    today = config.today()
    system = PROMPT.replace("{today}", today.isoformat()).replace("{weekday}", WEEKDAYS_FULL[today.weekday()])
    payload = {
        "model": config.GROQ_MODEL,
        "temperature": 0,
        "response_format": {"type": "json_object"},
        "messages": [
            {"role": "system", "content": system},
            {"role": "user", "content": text},
        ],
    }
    headers = {"Authorization": f"Bearer {config.GROQ_API_KEY}"}
    try:
        timeout = aiohttp.ClientTimeout(total=25)
        async with aiohttp.ClientSession(timeout=timeout) as session:
            async with session.post(GROQ_URL, json=payload, headers=headers) as r:
                body = await r.text()
                if r.status != 200:
                    raise AIError(f"Groq ответил {r.status}: {body[:150]}")
        data = json.loads(json.loads(body)["choices"][0]["message"]["content"])
    except AIError:
        raise
    except Exception as e:
        raise AIError(f"не удалось получить ответ от ИИ ({e})")

    title = (data.get("title") or "").strip()
    if not title:
        raise AIError("ИИ не нашёл название задания")

    deadline = None
    if data.get("deadline"):
        try:
            deadline = date.fromisoformat(str(data["deadline"])[:10])
        except ValueError:
            deadline = None

    note = (data.get("note") or "").strip() or None
    return {"title": title[:200], "deadline": deadline, "note": note[:500] if note else None}
