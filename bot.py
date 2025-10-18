# coding: utf8
from telebot.types import InlineKeyboardMarkup, InlineKeyboardButton
from regular import is_valid_birthdate
from dotenv import load_dotenv
from telebot import types
from parser import *
from db import *
import telebot
import os

load_dotenv()

TOKEN = os.getenv("TOKEN")
ADMIN = int(os.getenv("ADMIN", "0"))

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
        wlcmmsg += getHoroTodayAll() + '\n\n⚛️ Выберите Ваш знак зодиака'

    bot.send_message(
        message.from_user.id,
        text=wlcmmsg,
        reply_markup=markup,
        parse_mode="html",
        disable_web_page_preview=True
    )

    tgidregister(message.from_user.id, message.from_user.first_name)

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

@bot.message_handler(commands=['name'])
def edit_name(message):
    msg = bot.send_message(
        message.chat.id,
        "Введите Ваше имя:"
    )
    bot.register_next_step_handler(msg, save_new_name)

def save_new_name(message):
    new_name = message.text.strip()
    if not (2 <= len(new_name) <= 50):
        bot.send_message(
            message.chat.id,
            "Имя должно содержать от 2 до 50 символов. Попробуйте снова командой /name."
        )
        return

    set_name(message.from_user.id, new_name)

    bot.send_message(
        message.chat.id,
        f"Имя изменено на: <b>{new_name}</b>",
        parse_mode="html"
    )

@bot.message_handler(commands=['birthdate'])
def ask_birthdate(message):
    current_date = get_birthdate(message.from_user.id)

    if current_date:
        markup = types.InlineKeyboardMarkup()
        markup.add(types.InlineKeyboardButton("Изменить дату рождения", callback_data="change_birthdate"))
        bot.send_message(
            message.chat.id,
            f"Вы уже указали дату рождения: <b>{current_date}</b>",
            parse_mode="html",
            reply_markup=markup
        )
    else:
        msg = bot.send_message(
            message.chat.id,
            "Введите дату рождения в формате <b>ДЕНЬ.МЕСЯЦ.ГОД</b>\n\nПример: 3.5.1999 или 5.12.1998\n(Без нулей перед числами!)",
            parse_mode="html"
        )
        bot.register_next_step_handler(msg, save_birthdate)

def save_birthdate(message):
    date = message.text.strip()

    if not is_valid_birthdate(date):
        msg = bot.send_message(
            message.chat.id,
            "Неверный формат даты! Введите снова в формате: <b>ДЕНЬ.МЕСЯЦ.ГОД</b>\nПример: 3.5.1999",
            parse_mode="html"
        )
        bot.register_next_step_handler(msg, save_birthdate)
        return

    set_birthdate(message.from_user.id, date)
    bot.send_message(
        message.chat.id,
        f"Дата рождения успешно сохранена: <b>{date}</b>",
        parse_mode="html"
    )

@bot.callback_query_handler(func=lambda call: call.data == "change_birthdate")
def change_birthdate(call):
    msg = bot.send_message(
        call.message.chat.id,
        "Введите дату рождения в формате <b>ДЕНЬ.МЕСЯЦ.ГОД</b>\nПример: 3.5.1999",
        parse_mode="html"
    )
    bot.register_next_step_handler(msg, save_birthdate)

@bot.my_chat_member_handler()
def handle_chat_join(event):
    chat = event.chat
    new_status = event.new_chat_member.status

    if new_status in ['member', 'administrator']:
        register_group(
            chat.id,
            chat.type,
            getattr(chat, "title", None),
            getattr(chat, "username", None)
        )

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
