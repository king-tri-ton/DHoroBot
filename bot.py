# coding: utf8
from telebot.types import InlineKeyboardMarkup, InlineKeyboardButton
from telebot import types
from config import *
from parser import *
from db import *
import telebot

bot = telebot.TeleBot(TOKEN)

# Словарь соответствия между текстом сообщения и знаками зодиака
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

@bot.message_handler(commands=['start'])
def send_welcome(message):
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True, one_time_keyboard=False)  # Здесь изменено значение параметра
    col1, col2 = [], []
    for sign in zodiac_signs:
        if len(col1) < 6:
            col1.append(sign)
        else:
            col2.append(sign)
    markup.add(*col1)
    markup.add(*col2)
    wlcmmsg = '<b>👋 Привет ' + message.from_user.first_name + '</b>\n\n' + getHoroTodayAll() + '\n\n⚛️ Выберите Ваш знак зодиака'
    bot.send_message(message.from_user.id, text=wlcmmsg, reply_markup=markup, parse_mode="html", disable_web_page_preview=True)
    tgidregister(message.from_user.id)

@bot.message_handler(commands=['chat'])
def send_chat(message):
    chatmsg = '<b> [Чат] ⚛️ Гороскоп на Сегодня</b>\n\n👉 <a href="https://t.me/+I7-8qO-hf-UyMzE6">Нажми чтобы присоединиться</a>'
    bot.send_message(message.from_user.id, text=chatmsg, parse_mode="html", disable_web_page_preview=True)

# for admin
@bot.message_handler(commands=['all'])
def send_all(message):
    if message.chat.id == ADMIN:
        wlcmmsg = '<b>👋 Всем привет</b>\n\n' + getHoroTodayAll()
        bot.send_message(GROUP, text=wlcmmsg, parse_mode="html", disable_web_page_preview=True)

# for admin
@bot.message_handler(commands=['stat'])
def send_stat(message):
    if message.chat.id == ADMIN:
        stat = f'<b>📊 Статистика использования.</b>\n\n🔄 Количество пользователей: {countusers()}'
        bot.send_message(ADMIN, text=stat, parse_mode="html")

@bot.message_handler(content_types=['text'])
def process_step(message):
    sign = zodiac_signs.get(message.text)
    if sign:
        keyboard = types.InlineKeyboardMarkup()
        keyboard.add(*[InlineKeyboardButton(text=period, callback_data=f'{sign}|{period}') for period in ['вчера', 'сегодня', 'завтра', 'неделя', 'месяц', 'год']])
        bot.send_message(message.from_user.id, f'Получить гороскоп {message.text} на:', reply_markup=keyboard, parse_mode="html")

@bot.callback_query_handler(func=lambda call: True)
def callback_worker(call):
    el = call.data.split("|")
    period_text = {
        'вчера': 'yesterday',
        'сегодня': 'today',
        'завтра': 'tomorrow',
        'неделя': 'week',
        'месяц': 'month',
        'год': 'year'
    }
    bot.send_message(call.message.chat.id, getHoro(el[0], period_text[el[1]]), parse_mode="html", disable_web_page_preview=True)

bot.infinity_polling(interval=0)
