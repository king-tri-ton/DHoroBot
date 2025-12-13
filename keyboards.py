# coding: utf8
from telebot import types
from api.horo import ZODIAC_SIGNS, PERIOD_MAP

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
		# Формируем callback: horo_знак_период
		# Например: horo_aries_today
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



def get_personal_period_inline_keyboard():
	"""
	Создает инлайн-клавиатуру для выбора периода (Сегодня, Завтра, Неделя, Месяц)
	для персонального гороскопа.
	"""
	markup = types.InlineKeyboardMarkup(row_width=3)
	buttons = []
	
	for period_ru, api_key in PERIOD_MAP.items():
		if period_ru == 'вчера':  # Пропускаем 'вчера'
			continue
			
		# Формируем callback: personal_период (например: personal_today)
		cb_data = f"personal_{api_key}"
		
		buttons.append(
			types.InlineKeyboardButton(
				text=period_ru.capitalize(), 
				callback_data=cb_data
			)
		)
	
	# Добавляем кнопки в разметку, можно по 3 в ряд, если их много
	markup.add(*buttons)
	
	return markup


def feedback_button_keyboard(horoscope_id, disabled=None):
    """
    Создает клавиатуру для оценки.
    disabled: None, 'up' или 'down' — какая кнопка уже была нажата.
    """
    markup = types.InlineKeyboardMarkup()
    
    # 1. Если оценка еще не была дана (disabled=None): возвращаем обе активные кнопки
    if disabled is None:
        up_cb = f"rate_up_{horoscope_id}"
        down_cb = f"rate_down_{horoscope_id}"
        up_btn = types.InlineKeyboardButton("👍", callback_data=up_cb)
        down_btn = types.InlineKeyboardButton("👎", callback_data=down_cb)
        markup.add(up_btn, down_btn)
    
    # 2. Если пользователь поставил Лайк (disabled='up'): возвращаем только '✅'
    elif disabled == "up":
        # Кнопка '✅' не должна иметь callback_data, чтобы быть неактивной
        up_btn_final = types.InlineKeyboardButton("🥰 Понравилось", callback_data="none")
        markup.add(up_btn_final)
        
    # 3. Если пользователь поставил Дизлайк (disabled='down'): возвращаем только '👎' (как неактивную)
    elif disabled == "down":
        # Кнопка '👎' не должна иметь callback_data, чтобы быть неактивной
        down_btn_final = types.InlineKeyboardButton("👎 Не понравилось", callback_data="none")
        # Добавляем кнопку для отзыва, если хотите (она уже была в bot.py, но можно добавить сюда)
        # review_btn = types.InlineKeyboardButton("✍️ Оставить отзыв", callback_data=f"review_{horoscope_id}")
        markup.add(down_btn_final)
        
    return markup



