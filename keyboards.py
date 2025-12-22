# coding: utf8
from telebot import types
from api.horo import ZODIAC_SIGNS, PERIOD_MAP
from db import check_free_horoscope_today
from utils import personal_horoscope_text

TEXT_CANCEL = "❌ Отменить"

def get_zodiac_keyboard():
	"""
	Создает клавиатуру со знаками зодиака.
	"""
	markup = types.ReplyKeyboardMarkup(
		resize_keyboard=True,
		one_time_keyboard=False
	)

	signs = list(ZODIAC_SIGNS.values())

	row1 = signs[:6]
	row2 = signs[6:]

	markup.add(*row1)
	markup.add(*row2)

	return markup


def get_period_inline_keyboard(sign_key):
	"""
	Создает клавиатуру с периодами (сегодня, завтра...) под сообщением.
	"""
	markup = types.InlineKeyboardMarkup(row_width=3) # 3 кнопки в ряд
	buttons = []

	for text_ru, period_api_key in PERIOD_MAP.items():
		cb_data = f"horo_{sign_key}_{period_api_key}"
		
		buttons.append(
			types.InlineKeyboardButton(
				text=text_ru.capitalize(), 
				callback_data=cb_data
			)
		)

	markup.add(*buttons)
	return markup


def get_cancel_keyboard():
	"""Возвращает клавиатуру с кнопкой Отменить"""
	markup = types.ReplyKeyboardMarkup(resize_keyboard=True, one_time_keyboard=True)
	markup.add(types.KeyboardButton(TEXT_CANCEL))
	return markup



def change_birthdate_keyboard():
	markup = types.InlineKeyboardMarkup()
	markup.add(types.InlineKeyboardButton("Изменить дату рождения", callback_data="change_birthdate"))
	return markup



def get_stars_payment_keyboard():
	"""Клавиатура тарифов для команды /tariffs"""
	markup = types.InlineKeyboardMarkup(row_width=1)

	markup.add(
		types.InlineKeyboardButton(f"{personal_horoscope_text(1)} — ⭐️ 10 Stars", callback_data="buy_1_10"),
		types.InlineKeyboardButton(f"{personal_horoscope_text(3)} — ⭐️ 25 Stars", callback_data="buy_3_25"),
		types.InlineKeyboardButton(f"{personal_horoscope_text(5)} — ⭐️ 40 Stars", callback_data="buy_5_40")
	)
	return markup


def get_personal_period_inline_keyboard(user_id):
	"""
	Клавиатура выбора периода для /personal.
	Если 'сегодня' доступно бесплатно — помечаем это.
	"""
	markup = types.InlineKeyboardMarkup(row_width=2)
	buttons = []

	is_free_today = not check_free_horoscope_today(user_id)

	for period_ru, api_key in PERIOD_MAP.items():
		if period_ru == 'вчера':
			continue

		cb_data = f"personal_{api_key}"
		text = period_ru.capitalize()

		if api_key == 'today' and is_free_today:
			text = f"🎁 {text} (Бесплатно)"

		buttons.append(types.InlineKeyboardButton(text=text, callback_data=cb_data))

	markup.add(*buttons)
	return markup


def feedback_button_keyboard(horoscope_id, disabled=None):
	"""
	Создает клавиатуру для оценки.
	disabled: None, 'up' или 'down' — какая кнопка уже была нажата.
	"""
	markup = types.InlineKeyboardMarkup()

	if disabled is None:
		up_cb = f"rate_up_{horoscope_id}"
		down_cb = f"rate_down_{horoscope_id}"
		up_btn = types.InlineKeyboardButton("👍", callback_data=up_cb)
		down_btn = types.InlineKeyboardButton("👎", callback_data=down_cb)
		markup.add(up_btn, down_btn)

	elif disabled == "up":
		up_btn_final = types.InlineKeyboardButton("🥰 Понравилось", callback_data="none")
		markup.add(up_btn_final)

	elif disabled == "down":
		down_btn_final = types.InlineKeyboardButton("👎 Не понравилось", callback_data="none")
		markup.add(down_btn_final)

	return markup




