# coding: utf8
from telebot import types

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