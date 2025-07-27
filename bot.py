# coding: utf8
from telebot.types import InlineKeyboardMarkup, InlineKeyboardButton
from telebot import types
from config import *
from parser import *
from db import *
import telebot

bot = telebot.TeleBot(TOKEN)

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

period_map = {
    'вчера': 'yesterday',
    'сегодня': 'today',
    'завтра': 'tomorrow',
    'неделя': 'week',
    'месяц': 'month',
    'год': 'year'
}

def get_zodiac_from_text(text):
    found_sign = None
    for sign_full, sign_eng in zodiac_signs.items():
        sign_name = sign_full.split()[-1].lower()
        if sign_name in text:
            found_sign = sign_eng
            break
    return found_sign

@bot.message_handler(commands=['start'])
def send_welcome(message):
    args = message.text.split()
    zodiac_arg = args[1] if len(args) > 1 else None

    # Создание клавиатуры
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True, one_time_keyboard=False)
    col1, col2 = [], []
    for sign in zodiac_signs:
        if len(col1) < 6:
            col1.append(sign)
        else:
            col2.append(sign)
    markup.add(*col1)
    markup.add(*col2)

    # Приветствие
    wlcmmsg = f'<b>👋 Привет {message.from_user.first_name}</b>\n\n'

    # Если передан знак зодиака — показать только гороскоп
    if zodiac_arg and zodiac_arg in zodiac_signs.values():
        wlcmmsg += getHoro(zodiac_arg, 'today')
    else:
        # Общая сводка + предложение выбрать знак
        wlcmmsg += getHoroTodayAll() + '\n\n⚛️ Выберите Ваш знак зодиака'

    bot.send_message(
        message.from_user.id,
        text=wlcmmsg,
        reply_markup=markup,
        parse_mode="html",
        disable_web_page_preview=True
    )

    # Регистрация
    tgidregister(message.from_user.id)


@bot.message_handler(commands=['chat'])
def send_chat(message):
    if message.chat.id == ADMIN and len(message.text.split()) > 1:
        new_link = message.text.split(' ', 1)[1].strip()
        set_chat_link(new_link)
        bot.send_message(ADMIN, "✅ Ссылка на чат обновлена.")
    else:
        chat_link = get_chat_link()
        if chat_link:
            chatmsg = f'<b> [Чат] ⚛️ Гороскоп на Сегодня</b>\n\n👉 <a href="{chat_link}">Нажми чтобы присоединиться</a>'
        else:
            chatmsg = "🔗 Ссылка на чат не задана."
        bot.send_message(message.chat.id, text=chatmsg, parse_mode="html", disable_web_page_preview=True)

@bot.message_handler(commands=['stat'])
def send_stat(message):
    if message.chat.id == ADMIN:
        stat = f'<b>📊 Статистика использования.</b>\n\n🔄 Количество пользователей: {countusers()}\n👥 Групп/чатов/форумов: {countgroups()}'
        bot.send_message(ADMIN, text=stat, parse_mode="html")

@bot.my_chat_member_handler()
def handle_chat_join(event):
    chat = event.chat
    new_status = event.new_chat_member.status

    if new_status in ['member', 'administrator']:
        register_group(chat.id, chat.type)

@bot.message_handler(content_types=['text'])
def process_step(message):
    text = message.text.lower().strip()

    if message.chat.type in ['group', 'supergroup']:
        bot_username = bot.get_me().username.lower()

        if f"@{bot_username}" in text:
            text = text.replace(f"@{bot_username}", "").strip()
            if not text:
                bot.reply_to(message, "Чтобы узнать гороскоп, напиши:\n\n@DHoroBot Рак сегодня\n@DHoroBot Лев завтра\n\nПериод можно не указывать, по умолчанию будет 'сегодня'.")
                return
            
            found_sign = get_zodiac_from_text(text)

            if found_sign:
                found_period = 'сегодня'
                for period in period_map:
                    if period in text:
                        found_period = period
                        break

                result = getHoro(found_sign, period_map[found_period])
                bot.reply_to(message, result, parse_mode="html", disable_web_page_preview=True)
            else:
                bot.reply_to(message, "Пример:\n@DHoroBot Рак сегодня")
            return

    sign = zodiac_signs.get(message.text)
    if sign:
        keyboard = types.InlineKeyboardMarkup()
        keyboard.add(*[InlineKeyboardButton(text=period, callback_data=f'{sign}|{period}') for period in period_map])
        bot.send_message(message.from_user.id, f'Получить гороскоп {message.text} на:', reply_markup=keyboard, parse_mode="html")

@bot.callback_query_handler(func=lambda call: True)
def callback_worker(call):
    el = call.data.split("|")
    bot.send_message(call.message.chat.id, getHoro(el[0], period_map[el[1]]), parse_mode="html", disable_web_page_preview=True)

bot.infinity_polling(interval=0)
