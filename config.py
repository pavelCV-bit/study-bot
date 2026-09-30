"""Все настройки бота в одном месте.

Секреты (токены, ключи) сюда НЕ пишем — они берутся из файла .env (на ПК)
или из Environment Variables (на Vercel).
Настройки ниже (раздел «МОЖНО МЕНЯТЬ») правь прямо здесь.
"""
import os
from datetime import date, datetime
from zoneinfo import ZoneInfo

from dotenv import load_dotenv

load_dotenv()

# ================= СЕКРЕТЫ (из .env / Vercel) =================
BOT_TOKEN = os.getenv("BOT_TOKEN", "")             # токен от @BotFather
OWNER_ID = int(os.getenv("OWNER_ID") or 0)         # твой Telegram ID (бот отвечает только тебе)
GROQ_API_KEY = os.getenv("GROQ_API_KEY", "")       # ключ Groq (ИИ разбирает твой текст)
SUPABASE_URL = os.getenv("SUPABASE_URL", "").rstrip("/")
SUPABASE_KEY = os.getenv("SUPABASE_KEY", "")       # secret / service_role ключ Supabase
WEBHOOK_SECRET = os.getenv("WEBHOOK_SECRET", "")   # любая длинная случайная строка
CRON_SECRET = os.getenv("CRON_SECRET", "")         # ещё одна случайная строка

# ================= МОЖНО МЕНЯТЬ =================
TIMEZONE = "Asia/Almaty"          # твой часовой пояс

# За сколько дней до дедлайна напоминать.
# [3, 1] = за 3 дня и за 1 день. Хочешь ещё и в день дедлайна — добавь 0: [3, 1, 0]
REMIND_DAYS_BEFORE = [3, 1]

# Цвета срочности в списке /tasks:
URGENT_DAYS = 2   # 🔴 если осталось столько дней или меньше (и просрочено)
SOON_DAYS = 7     # 🟡 если осталось столько дней или меньше, дальше 🟢

# Какая ИИ-модель разбирает текст (Groq). Если вдруг перестала работать —
# впиши другую из списка моделей на console.groq.com
GROQ_MODEL = os.getenv("GROQ_MODEL", "openai/gpt-oss-120b")

# Название таблицы в Supabase (должно совпадать с schema.sql)
TABLE = "study_tasks"

# ВРЕМЯ напоминаний (9:00) задаётся не здесь, а в файле vercel.json (там время в UTC).


def today() -> date:
    """Сегодняшняя дата в твоём часовом поясе."""
    return datetime.now(ZoneInfo(TIMEZONE)).date()
