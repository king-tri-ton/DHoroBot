from config import BOT_LINK
from datetime import datetime, timedelta
import html
import re


MONTHS_RU = {
    1: "январь",
    2: "февраль",
    3: "март",
    4: "апрель",
    5: "май",
    6: "июнь",
    7: "июль",
    8: "август",
    9: "сентябрь",
    10: "октябрь",
    11: "ноябрь",
    12: "декабрь",
}

def is_valid_birthdate(date):
	"""
	Проверяет формат даты рождения:
	ДЕНЬ.МЕСЯЦ.ГОД без ведущих нулей.
	Примеры валидных: 3.5.1999, 5.12.1998
	"""
	pattern = r'^(?:[1-9]|[12][0-9]|3[01])\.(?:[1-9]|1[0-2])\.[0-9]{4}$'
	return bool(re.match(pattern, date.strip()))


def get_bot_username():
    """
    Возвращает username бота из ссылки BOT_LINK.
    Пример: 'https://t.me/DHoroBot' -> 'DHoroBot'
    """
    match = re.search(r't\.me/([A-Za-z0-9_]+)', BOT_LINK)
    if match:
        return match.group(1)
    return None


def md_to_html(md: str) -> str:
    md = html.escape(md)

    # Распознаём код-блоки ```lang ... ```
    def block_code(match):
        code = match.group(2)
        return f"<pre><code>{code}</code></pre>"

    md = re.sub(r"```([a-zA-Z0-9_-]+)?\n([\s\S]*?)```", block_code, md)

    # inline code `...`
    md = re.sub(r"`([^`]+)`", lambda m: f"<code>{m.group(1)}</code>", md)

    # Жирный **...**
    md = re.sub(r"\*\*(.*?)\*\*", lambda m: f"<b>{m.group(1)}</b>", md)

    # Курсив *...*
    md = re.sub(r"\*(.*?)\*", lambda m: f"<i>{m.group(1)}</i>", md)

    # Заголовки # text → просто <b>text</b>
    md = re.sub(r"^#+\s*(.*)$", lambda m: f"<b>{m.group(1)}</b>", md, flags=re.MULTILINE)

    # Цитаты "> ..."
    md = re.sub(r"^&gt;\s?(.*)$", r"<blockquote>\1</blockquote>", md, flags=re.MULTILINE)

    # Переводы строк
    md = md.replace("\n", "\n")

    return md


def get_period_text(period_key: str) -> str:
    now = datetime.now()

    if period_key == "today":
        return f"сегодня {now.day} {MONTHS_RU[now.month]} {now.year} года"

    if period_key == "tomorrow":
        tomorrow = now + timedelta(days=1)
        return f"завтра {tomorrow.day} {MONTHS_RU[tomorrow.month]} {tomorrow.year} года"

    if period_key == "week":
        start_of_week = now - timedelta(days=now.weekday())
        end_of_week = start_of_week + timedelta(days=6)
        return (
            f"неделю с {start_of_week.day} {MONTHS_RU[start_of_week.month]} "
            f"по {end_of_week.day} {MONTHS_RU[end_of_week.month]} {end_of_week.year} года"
        )

    if period_key == "month":
        return f"{MONTHS_RU[now.month]} {now.year} года"

    if period_key == "year":
        return f"{now.year} год"

    return period_key


def personal_horoscope_text(balance: int) -> str:
    balance = abs(balance)

    if balance % 10 == 1 and balance % 100 != 11:
        form = "Персональный гороскоп"
    elif 2 <= balance % 10 <= 4 and not (12 <= balance % 100 <= 14):
        form = "Персональных гороскопа"
    else:
        form = "Персональных гороскопов"

    return f"{balance} {form}"
