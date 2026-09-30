"""Работа с базой Supabase (таблица study_tasks). Только тут ходим в базу."""
import json as jsonlib
from datetime import date

import aiohttp

import config


def _headers(extra: dict | None = None) -> dict:
    h = {"apikey": config.SUPABASE_KEY, "Content-Type": "application/json"}
    # Старые ключи — это JWT (начинаются с eyJ), им нужен ещё и Authorization.
    if config.SUPABASE_KEY.startswith("eyJ"):
        h["Authorization"] = f"Bearer {config.SUPABASE_KEY}"
    if extra:
        h.update(extra)
    return h


async def _request(method: str, params: dict | None = None, body=None, prefer: str | None = None):
    url = f"{config.SUPABASE_URL}/rest/v1/{config.TABLE}"
    headers = _headers({"Prefer": prefer} if prefer else None)
    timeout = aiohttp.ClientTimeout(total=20)
    async with aiohttp.ClientSession(timeout=timeout) as session:
        async with session.request(method, url, params=params, json=body, headers=headers) as r:
            text = await r.text()
            if r.status >= 300:
                raise RuntimeError(f"Supabase {r.status}: {text[:200]}")
            return jsonlib.loads(text) if text else None


async def add_task(title: str, deadline: date | None, note: str | None) -> dict:
    rows = await _request(
        "POST",
        body={"title": title, "deadline": deadline.isoformat() if deadline else None, "note": note},
        prefer="return=representation",
    )
    return rows[0]


async def list_open_tasks() -> list[dict]:
    """Невыполненные задачи: сначала ближайшие дедлайны, без срока — в конце."""
    return await _request(
        "GET",
        params={"done": "eq.false", "order": "deadline.asc.nullslast,id.asc"},
    )


async def set_done(task_id: int) -> None:
    await _request("PATCH", params={"id": f"eq.{task_id}"}, body={"done": True})


async def delete_task(task_id: int) -> None:
    await _request("DELETE", params={"id": f"eq.{task_id}"})


async def mark_reminded(task_ids: list[int], day: date) -> None:
    """Запоминаем, что сегодня уже напоминали (защита от дублей)."""
    ids = ",".join(str(i) for i in task_ids)
    await _request("PATCH", params={"id": f"in.({ids})"}, body={"last_reminded_on": day.isoformat()})
