# coding: utf8
from telebot import types
from newsletter import (
    STATE_CREATING,
    STATE_READY,
    STATE_SENDING,
    STATE_COMPLETED
)

# Знаки зодиака - главный словарь
zodiac_signs = {
    '♈️ Овен': 'aries',
    '♉ Телец': 'taurus',
    '♊ Близнецы': 'gemini',
    '♋️ Рак': 'cancer',
    '♌ Лев': 'leo',
    '♍ Дева': 'virgo',
    '♎ Весы': 'libra',
    '♏ Скорпион': 'scorpio',
    '♐ Стрелец': 'sagittarius',
    '♑ Козерог': 'capricorn',
    '♒ Водолей': 'aquarius',
    '♓ Рыбы': 'pisces'
}

def get_zodiac_keyboard():
    """Возвращает клавиатуру со знаками зодиака"""
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True, one_time_keyboard=False)
    signs_list = list(zodiac_signs.keys())
    col1 = signs_list[:6]
    col2 = signs_list[6:]
    markup.add(*col1)
    markup.add(*col2)
    return markup

def get_cancel_keyboard():
    """Возвращает клавиатуру с кнопкой Отменить"""
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True, one_time_keyboard=True)
    markup.add(types.KeyboardButton("❌ Отменить"))
    return markup

def get_newsletter_actions_keyboard(nl_id):
    markup = types.InlineKeyboardMarkup()
    markup.add(types.InlineKeyboardButton("🚀 Начать рассылку", callback_data=f"start_nl_{nl_id}"))
    markup.add(types.InlineKeyboardButton("📋 Список рассылок", callback_data="list_newsletters"))
    return markup

def get_newsletters_list_keyboard(newsletters, page=1, per_page=5):
    markup = types.InlineKeyboardMarkup()

    total = len(newsletters)
    pages = (total + per_page - 1) // per_page

    start = (page - 1) * per_page
    end = start + per_page

    for nl in newsletters[start:end]:
        nl_id = nl[0]
        name = nl[1]
        state = nl[5]

        state_emoji = {
            STATE_CREATING: "🔄",
            STATE_READY: "✅",
            STATE_SENDING: "📨",
            STATE_COMPLETED: "✔️"
        }.get(state, "❓")

        markup.add(
            types.InlineKeyboardButton(
                f"{state_emoji} {name} (ID: {nl_id})",
                callback_data=f"view_nl_{nl_id}"
            )
        )

    nav = []
    if page > 1:
        nav.append(types.InlineKeyboardButton("⬅️", callback_data=f"nl_page_{page-1}"))
    if page < pages:
        nav.append(types.InlineKeyboardButton("➡️", callback_data=f"nl_page_{page+1}"))
    if nav:
        markup.row(*nav)

    markup.add(types.InlineKeyboardButton("➕ Создать новую", callback_data="create_newsletter"))
    return markup

def get_unfinished_newsletter_keyboard(nl_id):
    markup = types.InlineKeyboardMarkup()
    markup.add(types.InlineKeyboardButton("✅ Продолжить создание", callback_data=f"continue_nl_{nl_id}"))
    markup.add(types.InlineKeyboardButton("❌ Отменить и создать новую", callback_data=f"cancel_nl_{nl_id}"))
    return markup

def get_newsletter_type_keyboard():
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True, one_time_keyboard=True)
    markup.add("📝 Текстовая рассылка", "🖼 Фото + текст")
    markup.add("❌ Отменить")
    return markup

