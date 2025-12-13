from keyboards import (
	get_personal_period_inline_keyboard,
	get_period_inline_keyboard,
	change_birthdate_keyboard,
	feedback_button_keyboard,
	get_zodiac_keyboard,
	get_cancel_keyboard,
	TEXT_CANCEL
)

from ai import get_openai_response, build_personal_horoscope_prompt

from api.horo import HoroAPI, ZODIAC_SIGNS, PERIOD_MAP

from config import TOKEN, USER_AGENT, ADMIN, BOT_LINK

from db import *

from utils import is_valid_birthdate, get_bot_username, get_period_text

import telebot

import random


bot = telebot.TeleBot(TOKEN)
horo = HoroAPI(USER_AGENT)


@bot.message_handler(commands=['start'])
def send_welcome(message):
	args = message.text.split()
	zodiac_arg = args[1] if len(args) > 1 else None

	user_id = message.from_user.id
	first_name = message.from_user.first_name

	# регистрируем пользователя (дата пишется внутри tgidregister)
	tgidregister(user_id, first_name)

	wlcMsg = f'<b>👋 Привет  {first_name}</b>\n\n'

	# если передан знак зодиака
	if zodiac_arg and zodiac_arg in ZODIAC_SIGNS:
		title, text = horo.get_horo(zodiac_arg, 'today')
		wlcMsg += f'<b>{title}</b>\n\n{text}\n\n'
	else:
		title, text = horo.get_today_all()
		wlcMsg += f'<b>{title}</b>\n\n{text}\n\n<b>⚛️ Выберите Ваш знак зодиака</b>'

	bot.send_message(
		user_id,
		wlcMsg,
		reply_markup=get_zodiac_keyboard(),
		parse_mode="html",
		disable_web_page_preview=True
	)



@bot.message_handler(commands=['name'])
def edit_name(message):
	current_name = get_name(message.from_user.id)
	
	if current_name:
		text = f"Ваше имя: <b>{current_name}</b>\n\nВведите имя или нажмите {TEXT_CANCEL}:"
	else:
		text = f"Введите Ваше имя или нажмите {TEXT_CANCEL}:"
	
	msg = bot.send_message(
		message.chat.id,
		text,
		parse_mode="html",
		reply_markup=get_cancel_keyboard()
	)
	bot.register_next_step_handler(msg, save_new_name)

def save_new_name(message):
	if message.text.strip() == TEXT_CANCEL:
		bot.send_message(
			message.chat.id,
			"❌ Изменение имени отменено.",
			reply_markup=get_zodiac_keyboard()
		)
		return
	
	new_name = message.text.strip()
	if not (2 <= len(new_name) <= 50):
		msg = bot.send_message(
			message.chat.id,
			f"Имя должно содержать от 2 до 50 символов. Попробуйте снова или нажмите {TEXT_CANCEL}:",
			reply_markup=get_cancel_keyboard()
		)
		bot.register_next_step_handler(msg, save_new_name)
		return
	
	set_name(message.from_user.id, new_name)
	bot.send_message(
		message.chat.id,
		f"✅ Имя изменено на: <b>{new_name}</b>",
		parse_mode="html",
		reply_markup=get_zodiac_keyboard()
	)




@bot.message_handler(commands=['birthday'])
def ask_birthdate(message):
	current_date = get_birthdate(message.from_user.id)
	
	if current_date:
		bot.send_message(
			message.chat.id,
			f"Вы уже указали дату рождения: <b>{current_date}</b>\n\n<i>Она используется для персонального гороскопа, используйте</i> /personal",
			parse_mode="html",
			reply_markup=change_birthdate_keyboard()
		)
	else:
		msg = bot.send_message(
			message.chat.id,
			f"Введите дату рождения в формате <b>ДЕНЬ.МЕСЯЦ.ГОД</b>\n\nПример: 3.5.1999 или 5.12.1998\n(Без нулей перед числами!)\n\nОна необходима для персонального гороскопа.\n\nИли нажмите {TEXT_CANCEL}",
			parse_mode="html",
			reply_markup=get_cancel_keyboard()
		)
		bot.register_next_step_handler(msg, save_birthdate)

def save_birthdate(message):
	if message.text.strip() == TEXT_CANCEL:
		bot.send_message(
			message.chat.id,
			"❌ Изменение даты рождения отменено.",
			reply_markup=get_zodiac_keyboard()
		)
		return
	
	date = message.text.strip()
	if not is_valid_birthdate(date):
		msg = bot.send_message(
			message.chat.id,
			f"Неверный формат даты! Введите снова в формате: <b>ДЕНЬ.МЕСЯЦ.ГОД</b>\nПример: 3.5.1999\n\nИли нажмите {TEXT_CANCEL}",
			parse_mode="html",
			reply_markup=get_cancel_keyboard()
		)
		bot.register_next_step_handler(msg, save_birthdate)
		return
	
	set_birthdate(message.from_user.id, date)
	bot.send_message(
		message.chat.id,
		f"✅ Ваша дата рождения сохранена: <b>{date}</b>",
		parse_mode="html",
		reply_markup=get_zodiac_keyboard()
	)

@bot.callback_query_handler(func=lambda call: call.data == "change_birthdate")
def change_birthdate(call):
	current_date = get_birthdate(call.from_user.id)
	text = f"Текущая дата рождения: <b>{current_date}</b>\n\nВведите дату рождения в формате <b>ДЕНЬ.МЕСЯЦ.ГОД</b>\nПример: 3.5.1999\n\nИли нажмите {TEXT_CANCEL}"
	
	msg = bot.send_message(
		call.message.chat.id,
		text,
		parse_mode="html",
		reply_markup=get_cancel_keyboard()
	)
	bot.register_next_step_handler(msg, save_birthdate)



@bot.message_handler(commands=['chat'])
def send_chat(message):
	chat_link = get_chat_link()
	if chat_link:
		chatmsg = f'<b>[Чат] ⚛️ Гороскоп на Сегодня</b>\n\n👉 <a href="{chat_link}">Нажми чтобы присоединиться</a>'
	else:
		chatmsg = "🔗 Ссылка на чат не задана."
	bot.send_message(message.chat.id, text=chatmsg, parse_mode="html", disable_web_page_preview=True)



@bot.message_handler(commands=['personal'])
def personal_horo_command(message):
	user_id = message.from_user.id
	name = get_name(user_id)
	birthdate = get_birthdate(user_id)

	if not birthdate:
		msg = bot.send_message(
			user_id,
			"⚠️ Для персонального гороскопа необходимо указать дату рождения.\nИспользуйте /birthday для её добавления."
		)
		return
	
	bot.send_message(
		user_id,
		"⭐️ Выберите период для персонального гороскопа:",
		reply_markup=get_personal_period_inline_keyboard()
	)


@bot.callback_query_handler(func=lambda call: call.data.startswith("personal_"))
def handle_personal_horo(call):
	user_id = call.from_user.id
	period_key = call.data.split("_")[1]

	name = get_name(user_id)
	birthdate = get_birthdate(user_id)

	if not birthdate:
		bot.send_message(user_id, "⚠️ Дата рождения не указана. Используйте /birthday")
		return

	bot.send_message(user_id, "⏳ Составляю ваш персональный гороскоп...")

	period_text = get_period_text(period_key)

	prompt = build_personal_horoscope_prompt(name, birthdate, period_key, period_text)
	text, _, _ = get_openai_response(prompt)
	horoscope_id = add_personal_horoscope(user_id, period_key, text)

	bot.send_message(
		user_id,
		f"<b>Персональный гороскоп</b>\n\n{text}",
		# Изменено: передаем horoscope_id
		reply_markup=feedback_button_keyboard(horoscope_id),
		parse_mode="html",
		disable_web_page_preview=True
	)


@bot.callback_query_handler(func=lambda call: call.data.startswith("rate_"))
def handle_rating(call):
	user_id = call.from_user.id
	
	parts = call.data.split("_")
	action = parts[1]
	horoscope_id = int(parts[2])
	message_id = call.message.message_id
	
	if action == "up":
		update_horoscope_rating(horoscope_id, 1)
		bot.answer_callback_query(call.id, text="Спасибо за 👍")
		
		# Обновляем кнопки: теперь будет только '✅ Понравилось'
		bot.edit_message_reply_markup(
			call.message.chat.id, 
			message_id, 
			reply_markup=feedback_button_keyboard(horoscope_id, disabled="up")
		)

	elif action == "down":
		update_horoscope_rating(horoscope_id, -1)
		bot.answer_callback_query(call.id, text="Спасибо за 👎")
		
		# Обновляем кнопки: теперь будет только '👎 Не понравилось'
		bot.edit_message_reply_markup(
			call.message.chat.id, 
			message_id, 
			reply_markup=feedback_button_keyboard(horoscope_id, disabled="down")
		)

		# ... (Код для запроса отзыва остается прежним)
		msg = bot.send_message(
			user_id,
			"🥲 Жаль, что не понравилось. Можете написать короткий отзыв, что не понравилось? Почему? (необязательно):",
			reply_markup=get_cancel_keyboard()
		)
		bot.register_next_step_handler(msg, lambda m: handle_feedback(m, horoscope_id))


def handle_feedback(message, horoscope_id):
	
	if message.text.strip() == TEXT_CANCEL:
		bot.send_message(
			message.chat.id,
			"🥰 Спасибо, что оценили гороскоп. Ваша оценка учтена.", # ИСПРАВЛЕНО: Признаем, что оценка (👎) была поставлена.
			reply_markup=get_zodiac_keyboard()
		)
		return
		
	# Если не отмена, то сохраняем отзыв
	update_horoscope_feedback(horoscope_id, message.text)
	bot.send_message(
		message.chat.id, 
		"🥰 Спасибо за ваш развернутый отзыв! Мы ценим ваше мнение и постараемся его учесть.", # Улучшенное сообщение о сохранении
		reply_markup=get_zodiac_keyboard() # Возврат к основной клавиатуре
	)


@bot.message_handler(commands=['admin'])
def admin_panel(message):
	if message.from_user.id != ADMIN:
		return
	
	admin_text = (
		"👑 Панель администратора\n\n"
		"/stat - статистика бота\n"
		"/setchatlink - добавить/изменить ссылку на чат\n"
		# "/newsletter - управление рассылками\n"
	)
	bot.reply_to(message, admin_text)



@bot.message_handler(commands=['stat'])
def send_stat(message):
	if message.from_user.id == ADMIN:  # ← изменено с message.chat.id
		stat = f'<b>📊 Статистика</b>\n\n🔄 Количество пользователей: {str(countusers())}\n👥 Групп/чатов/форумов: {str(countgroups())}'
		bot.send_message(ADMIN, text=stat, parse_mode="html")




@bot.message_handler(commands=['setchatlink'])
def set_chat_command(message):
	if message.chat.id != ADMIN:
		return

	current_link = get_chat_link()
	if current_link:
		msg_text = f"Текущая ссылка на чат: {current_link}\nВведите ссылку или нажмите {TEXT_CANCEL}:"
	else:
		msg_text = f"Ссылка на чат ещё не задана. Введите новую ссылку или нажмите {TEXT_CANCEL}:"

	bot.send_message(ADMIN, msg_text, reply_markup=get_cancel_keyboard())
	bot.register_next_step_handler(message, process_chat_link)

def process_chat_link(message):
	if message.chat.id != ADMIN:
		return

	text = message.text.strip()

	if text == TEXT_CANCEL:
		bot.send_message(ADMIN, "❌ Изменение ссылки отменено.", reply_markup=get_zodiac_keyboard())
		return

	# Проверка, что это ссылка на Telegram
	if not text.startswith("https://t.me/"):
		bot.send_message(ADMIN, f"⚠️ Неверный формат ссылки. Попробуйте снова или нажмите {TEXT_CANCEL}.", reply_markup=get_cancel_keyboard())
		bot.register_next_step_handler(message, process_chat_link)
		return

	set_chat_link(text)
	bot.send_message(ADMIN, "✅ Ссылка на чат обновлена.", reply_markup=get_zodiac_keyboard())




# Регистрация группы/супергруппы/канала
@bot.my_chat_member_handler()
def handle_chat_join(event):
	chat = event.chat
	new_status = event.new_chat_member.status

	# Регистрируем ТОЛЬКО группы и каналы
	if chat.type not in ('group', 'supergroup', 'channel'):
		return

	if new_status in ('member', 'administrator'):
		register_group(
			chat.id,
			chat.type,
			chat.title,
			chat.username
		)


# Обработка сообщений
@bot.message_handler(content_types=['text'])
def handle_message(message):
	chat_type = message.chat.type

	if chat_type == 'private':
		handle_private(message)
	elif chat_type in ('group', 'supergroup'):
		handle_group(message)


def handle_private(message):
	text = message.text.strip() # Не делаем lower() сразу, чтобы сохранить эмодзи если они важны, но для сравнения будем понижать
	
	# 1. Проверяем, является ли текст знаком зодиака
	# Нам нужно найти ключ (например 'cancer') по значению ('♋️ Рак')
	chosen_sign_key = None
	for key, value in ZODIAC_SIGNS.items():
		if value.lower() == text.lower():
			chosen_sign_key = key
			break

	if chosen_sign_key:
		# Если знак найден — отправляем вопрос с Inline-кнопками
		keyboard = get_period_inline_keyboard(chosen_sign_key)
		bot.send_message(
			message.chat.id,
			f"Получить гороскоп <b>{ZODIAC_SIGNS[chosen_sign_key]}</b> на:",
			reply_markup=keyboard,
			parse_mode="html",
		)
	else:
		# Если текст не распознан как знак, показываем обычную клавиатуру
		bot.send_message(
			message.chat.id, 
			"Пожалуйста, выберите знак зодиака:", 
			reply_markup=get_zodiac_keyboard()
		)

@bot.callback_query_handler(func=lambda call: call.data.startswith("horo_"))
def handle_horo_callback(call):
	data = call.data
	
	# Отвечаем на callback немедленно
	bot.answer_callback_query(call.id)

	try:
		# 1. Извлекаем данные
		parts = data.split("_")
		if len(parts) < 3:
			return 

		sign_key = parts[1]       # 'cancer'
		period_api_key = parts[2] # 'tomorrow'
		
		# Получаем русские названия для редактирования сообщения
		sign_name = ZODIAC_SIGNS.get(sign_key, "Неизвестный знак")
		
		# Обратный поиск русского названия периода
		period_ru = next(
			(ru for ru, api_key in PERIOD_MAP.items() if api_key == period_api_key), 
			period_api_key
		)
		
		# 2. Получаем гороскоп
		title, content = horo.get_horo(sign_key, period_api_key)

		title_with_emoji = f"☀️ {title}"

		# -------------------------------------------------------------
		# ДОБАВЛЕНИЕ СКРЫТОГО ТЕКСТА С КОМАНДОЙ /PERSONAL (Шанс 20%)
		# -------------------------------------------------------------
		if random.random() < 0.20: 
			hidden_text_snippet = (
				"\n\n" # Добавим отступы
				"<tg-spoiler>"
				"✨ Получите Ваш <b>персональный</b> гороскоп.\nВоспользуйтесь: /personal"
				"</tg-spoiler>"
			)
			content += hidden_text_snippet
		# -------------------------------------------------------------

		content += f"\n\n<a href='{BOT_LINK}'>⚛️ Гороскоп на Сегодня | {get_bot_username()}</a>"

		# 3. Редактируем старое сообщение
		edited_text = f"Вы выбрали: <b>{sign_name}</b> на <b>{period_ru.capitalize()}</b>."
		
		try:
			bot.edit_message_text(
				chat_id=call.message.chat.id,
				message_id=call.message.message_id,
				text=edited_text,
				parse_mode="html",
				reply_markup=None # Удаляем клавиатуру
			)
		except Exception as e:
			# Игнорируем ошибку, если сообщение не требует редактирования (например, если нет изменений)
			print(f"Failed to edit message text/remove keyboard: {e}") 

		# 4. Отправляем НОВОЕ сообщение с гороскопом
		text_response = f"<b>{title_with_emoji}</b>\n\n{content}"
		bot.send_message(
			chat_id=call.message.chat.id,
			text=text_response,
			parse_mode="html",
			disable_web_page_preview=True
		)


	except Exception as e:
		print("Horo callback error (final):", e)
		bot.send_message(call.message.chat.id, "К сожалению, не удалось получить гороскоп.")





def handle_group(message):
	bot_username = bot.get_me().username.lower()
	text = message.text.lower()

	if f"@{bot_username}" not in text:
		return

	text = text.replace(f"@{bot_username}", "").strip()
	if not text:
		bot.reply_to(message, f"Пример: @{get_bot_username()} Рак сегодня")
		return

	# Разделяем на знак и период
	words = text.split()
	if len(words) < 1:
		return

	sign_name = words[0]  # ожидаем "рак"
	period_name = words[1] if len(words) > 1 else 'сегодня'

	# ищем ключ знака
	sign_key = next((k for k,v in ZODIAC_SIGNS.items() if v.lower().endswith(sign_name)), None)
	period_key = PERIOD_MAP.get(period_name, 'today')

	if not sign_key:
		bot.reply_to(message, f"Не удалось определить знак. Пример: @{get_bot_username()} Рак сегодня")
		return

	title, text = horo.get_horo(sign_key, period_key)
	bot.reply_to(message, f"<b>{title}</b>\n\n{text}", parse_mode="html", disable_web_page_preview=True)


bot.infinity_polling(interval=0)