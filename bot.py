# coding: utf8
from keyboards import (
    get_zodiac_keyboard,
    get_cancel_keyboard,
    zodiac_signs,
    get_newsletter_actions_keyboard,
    get_newsletters_list_keyboard,
    get_unfinished_newsletter_keyboard,
    get_newsletter_type_keyboard
)

from telebot.types import InlineKeyboardMarkup, InlineKeyboardButton
from regular import is_valid_birthdate
from config import TOKEN, ADMIN
from telebot import types
from parser import *
from db import *
import telebot

from newsletter import (
    STATE_CREATING,
    STATE_READY,
    STATE_SENDING,
    STATE_COMPLETED,
    start_newsletter_async
)

bot = telebot.TeleBot(TOKEN)

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


# ==================== КОМАНДЫ РАССЫЛКИ ====================

@bot.message_handler(commands=['newsletter'])
def newsletter_command(message):
    if message.chat.id != ADMIN:
        return
    
    active_nl = get_active_newsletter_creation()

    # Если есть незавершённая — показываем меню
    if active_nl:
        nl_id = active_nl[0]
        bot.send_message(
            ADMIN,
            f"⚠️ У вас есть незавершенная рассылка:\n\n📝 {active_nl[1]}\n\nЧто делать?",
            parse_mode='HTML',
            reply_markup=get_unfinished_newsletter_keyboard(nl_id)
        )
        return
    
    # Если нет — показываем список со страницы 1
    show_newsletters_list(ADMIN, page=1)

@bot.callback_query_handler(func=lambda call: call.data.startswith("nl_page_"))
def newsletter_page(call):
    page = int(call.data.split("_")[2])
    newsletters = get_all_newsletters()

    markup = get_newsletters_list_keyboard(newsletters, page=page)

    bot.edit_message_reply_markup(
        call.message.chat.id,
        call.message.message_id,
        reply_markup=markup
    )

def show_newsletters_list(chat_id, page=1):
    newsletters = get_all_newsletters()

    if not newsletters:
        bot.send_message(chat_id, "📭 Рассылок пока нет.")
        return

    markup = get_newsletters_list_keyboard(newsletters, page=page)

    bot.send_message(
        chat_id,
        "📋 <b>Список рассылок:</b>\n\n🔄 - создается\n✅ - готова\n📨 - отправляется\n✔️ - завершена",
        parse_mode='HTML',
        reply_markup=markup
    )

@bot.callback_query_handler(func=lambda call: call.data.startswith("continue_nl_"))
def callback_continue_newsletter(call):
    nl_id = int(call.data.split("_")[2])
    newsletter = get_newsletter(nl_id)
    
    if not newsletter:
        bot.answer_callback_query(call.id, "❌ Рассылка не найдена")
        return
    
    step = newsletter[12]
    
    if step == 'name':
        msg = bot.send_message(
            ADMIN,
            f"📝 <b>Рассылка #{nl_id}</b>\n\nВведите название рассылки:",
            parse_mode='HTML',
            reply_markup=get_cancel_keyboard()
        )
        bot.register_next_step_handler(msg, ask_newsletter_name)

    elif step == 'type':
        msg = bot.send_message(
            ADMIN,
            f"📝 <b>Рассылка #{nl_id}</b>\nНазвание: <b>{newsletter[1]}</b>\n\nВыберите тип рассылки:",
            parse_mode='HTML',
            reply_markup=get_newsletter_type_keyboard()
        )
        bot.register_next_step_handler(msg, ask_newsletter_type)

    elif step == 'text':
        msg = bot.send_message(
            ADMIN,
            f"📝 <b>Рассылка #{nl_id}</b>\n\nВведите текст рассылки:",
            parse_mode='HTML',
            reply_markup=get_cancel_keyboard()
        )
        bot.register_next_step_handler(msg, save_newsletter_text)

    elif step == 'photo':
        msg = bot.send_message(
            ADMIN,
            f"🖼 <b>Рассылка #{nl_id}</b>\n\nОтправьте фото:",
            parse_mode='HTML',
            reply_markup=get_cancel_keyboard()
        )
        bot.register_next_step_handler(msg, save_newsletter_photo)

    elif step == 'caption':
        msg = bot.send_message(
            ADMIN,
            f"📝 <b>Рассылка #{nl_id}</b>\n\nВведите подпись к фото:",
            parse_mode='HTML',
            reply_markup=get_cancel_keyboard()
        )
        bot.register_next_step_handler(msg, save_newsletter_caption)

@bot.callback_query_handler(func=lambda call: call.data.startswith("cancel_nl_"))
def callback_cancel_newsletter(call):
    """Отменить создание рассылки"""
    nl_id = int(call.data.split("_")[2])
    cancel_newsletter_creation(nl_id)
    
    bot.answer_callback_query(call.id, "✅ Рассылка отменена")
    bot.delete_message(call.message.chat.id, call.message.message_id)
    
    # Создаем новую
    newsletter_command(call.message)

def ask_newsletter_name(message):
    if message.text and message.text.strip() == "❌ Отменить":
        active_nl = get_active_newsletter_creation()
        if active_nl:
            cancel_newsletter_creation(active_nl[0])
        bot.send_message(ADMIN, "❌ Создание рассылки отменено.", reply_markup=get_zodiac_keyboard())
        return
    
    if not message.text:
        msg = bot.send_message(ADMIN, "⚠️ Пожалуйста, введите текст.")
        bot.register_next_step_handler(msg, ask_newsletter_name)
        return
    
    name = message.text.strip()
    
    active_nl = get_active_newsletter_creation()
    if not active_nl:
        bot.send_message(ADMIN, "❌ Ошибка: рассылка не найдена")
        return
    
    nl_id = active_nl[0]
    update_newsletter_name(nl_id, name)
    update_newsletter_step(nl_id, 'type')
    
    msg = bot.send_message(
        ADMIN,
        f"✅ Название: <b>{name}</b>\n\n📋 Выберите тип рассылки:",
        parse_mode='HTML',
        reply_markup=get_newsletter_type_keyboard()
    )
    bot.register_next_step_handler(msg, ask_newsletter_type)

def ask_newsletter_type(message):
    """Запрос типа рассылки"""
    if message.text and message.text.strip() == "❌ Отменить":
        active_nl = get_active_newsletter_creation()
        if active_nl:
            cancel_newsletter_creation(active_nl[0])
        bot.send_message(ADMIN, "❌ Создание рассылки отменено.", reply_markup=get_zodiac_keyboard())
        return
    
    if message.text == "📝 Текстовая рассылка":
        nl_type = 'text'
    elif message.text == "🖼 Фото + текст":
        nl_type = 'caption'
    else:
        msg = bot.send_message(ADMIN, "⚠️ Пожалуйста, используйте кнопки для выбора типа рассылки.")
        bot.register_next_step_handler(msg, ask_newsletter_type)
        return
    
    active_nl = get_active_newsletter_creation()
    if not active_nl:
        bot.send_message(ADMIN, "❌ Ошибка: рассылка не найдена")
        return
    
    nl_id = active_nl[0]
    update_newsletter_type(nl_id, nl_type)
    
    if nl_type == 'text':
        update_newsletter_step(nl_id, 'text')
        msg = bot.send_message(
            ADMIN,
            "📝 <b>Введите текст рассылки</b>\n\nВы можете использовать HTML-форматирование:\n<code>&lt;b&gt;жирный&lt;/b&gt;</code>\n<code>&lt;i&gt;курсив&lt;/i&gt;</code>\n<code>&lt;u&gt;подчеркнутый&lt;/u&gt;</code>\n<code>&lt;a href='URL'&gt;ссылка&lt;/a&gt;</code>",
            parse_mode='HTML',
            reply_markup=get_cancel_keyboard()
        )
        bot.register_next_step_handler(msg, save_newsletter_text)
    else:
        update_newsletter_step(nl_id, 'photo')
        msg = bot.send_message(
            ADMIN,
            "🖼 <b>Отправьте фото для рассылки</b>",
            parse_mode='HTML',
            reply_markup=get_cancel_keyboard()
        )
        bot.register_next_step_handler(msg, save_newsletter_photo)

def save_newsletter_text(message):
    """Сохранение текста рассылки"""
    if message.text and message.text.strip() == "❌ Отменить":
        active_nl = get_active_newsletter_creation()
        if active_nl:
            cancel_newsletter_creation(active_nl[0])
        bot.send_message(ADMIN, "❌ Создание рассылки отменено.", reply_markup=get_zodiac_keyboard())
        return
    
    if not message.text:
        msg = bot.send_message(ADMIN, "⚠️ Пожалуйста, отправьте текстовое сообщение.")
        bot.register_next_step_handler(msg, save_newsletter_text)
        return
    
    text = message.html_text if hasattr(message, 'html_text') else message.text
    
    active_nl = get_active_newsletter_creation()
    if not active_nl:
        bot.send_message(ADMIN, "❌ Ошибка: рассылка не найдена")
        return
    
    nl_id = active_nl[0]
    update_newsletter_text(nl_id, text)
    set_newsletter_state(nl_id, STATE_READY)
    update_newsletter_step(nl_id, 'completed')
    
    bot.send_message(ADMIN, "Главное меню:", reply_markup=get_zodiac_keyboard())
    
    bot.send_message(
        ADMIN,
        f"✅ <b>Рассылка #{nl_id} создана!</b>\n\n📝 Название: {active_nl[1]}\n📋 Тип: Текстовая\n\n<b>Превью:</b>\n{text}",
        parse_mode='HTML',
        reply_markup=get_newsletter_actions_keyboard(nl_id),
        disable_web_page_preview=True
    )

def save_newsletter_photo(message):
    """Сохранение фото для рассылки"""
    if message.text and message.text.strip() == "❌ Отменить":
        active_nl = get_active_newsletter_creation()
        if active_nl:
            cancel_newsletter_creation(active_nl[0])
        bot.send_message(ADMIN, "❌ Создание рассылки отменено.", reply_markup=get_zodiac_keyboard())
        return
    
    if not message.photo:
        msg = bot.send_message(ADMIN, "⚠️ Пожалуйста, отправьте фото.")
        bot.register_next_step_handler(msg, save_newsletter_photo)
        return
    
    photo_file_id = message.photo[-1].file_id
    
    active_nl = get_active_newsletter_creation()
    if not active_nl:
        bot.send_message(ADMIN, "❌ Ошибка: рассылка не найдена")
        return
    
    nl_id = active_nl[0]
    update_newsletter_photo(nl_id, photo_file_id)
    update_newsletter_step(nl_id, 'caption')
    
    msg = bot.send_message(
        ADMIN,
        "📝 <b>Теперь введите подпись к фото</b>\n\nВы можете использовать HTML-форматирование:\n<code>&lt;b&gt;жирный&lt;/b&gt;</code>\n<code>&lt;i&gt;курсив&lt;/i&gt;</code>",
        parse_mode='HTML',
        reply_markup=get_cancel_keyboard()
    )
    bot.register_next_step_handler(msg, save_newsletter_caption)

def save_newsletter_caption(message):
    """Сохранение подписи к фото"""
    if message.text and message.text.strip() == "❌ Отменить":
        active_nl = get_active_newsletter_creation()
        if active_nl:
            cancel_newsletter_creation(active_nl[0])
        bot.send_message(ADMIN, "❌ Создание рассылки отменено.", reply_markup=get_zodiac_keyboard())
        return
    
    if not message.text:
        msg = bot.send_message(ADMIN, "⚠️ Пожалуйста, отправьте текст подписи.")
        bot.register_next_step_handler(msg, save_newsletter_caption)
        return
    
    text = message.html_text if hasattr(message, 'html_text') else message.text
    
    active_nl = get_active_newsletter_creation()
    if not active_nl:
        bot.send_message(ADMIN, "❌ Ошибка: рассылка не найдена")
        return
    
    nl_id = active_nl[0]
    update_newsletter_text(nl_id, text)
    set_newsletter_state(nl_id, STATE_READY)
    update_newsletter_step(nl_id, 'completed')
    
    newsletter = get_newsletter(nl_id)
    photo_file_id = newsletter[4]
    
    bot.send_message(ADMIN, "Главное меню:", reply_markup=get_zodiac_keyboard())
    bot.send_photo(
        ADMIN,
        photo_file_id,
        caption=f"✅ <b>Рассылка #{nl_id} создана!</b>\n\n📝 Название: {active_nl[1]}\n📋 Тип: Фото + текст\n\n<b>Превью подписи:</b>\n{text}",
        parse_mode='HTML',
        reply_markup=get_newsletter_actions_keyboard(nl_id)
    )

@bot.callback_query_handler(func=lambda call: call.data == "create_newsletter")
def callback_create_newsletter(call):
    """Callback для создания рассылки"""
    newsletter_command(call.message)

@bot.callback_query_handler(func=lambda call: call.data.startswith("view_nl_"))
def callback_view_newsletter(call):
    """Просмотр рассылки"""
    nl_id = int(call.data.split("_")[2])
    newsletter = get_newsletter(nl_id)
    
    if not newsletter:
        bot.answer_callback_query(call.id, "❌ Рассылка не найдена")
        return
    
    name = newsletter[1]
    nl_type = newsletter[2]
    text = newsletter[3]
    state = newsletter[5]
    created_at = newsletter[6]
    total = newsletter[9]
    successful = newsletter[10]
    failed = newsletter[11]
    
    state_text = {
        STATE_CREATING: "🔄 Создается",
        STATE_READY: "✅ Готова к отправке",
        STATE_SENDING: "📨 Отправляется",
        STATE_COMPLETED: "✔️ Завершена"
    }.get(state, "❓ Неизвестно")
    
    type_text = "📝 Текстовая" if nl_type == 'text' else "🖼 Фото + текст"
    
    info = f"""
<b>📊 Рассылка #{nl_id}</b>

📝 Название: {name}
📋 Тип: {type_text}
🔔 Статус: {state_text}
📅 Создана: {created_at}
"""
    
    if state == STATE_COMPLETED:
        info += f"\n📊 Всего: {total}\n✅ Успешно: {successful}\n❌ Ошибок: {failed}"
    
    markup = types.InlineKeyboardMarkup()
    
    if state == STATE_READY:
        markup.add(types.InlineKeyboardButton("🚀 Начать рассылку", callback_data=f"start_nl_{nl_id}"))
    
    markup.add(types.InlineKeyboardButton("◀️ Назад к списку", callback_data="list_newsletters"))
    
    bot.edit_message_text(
        info,
        call.message.chat.id,
        call.message.message_id,
        parse_mode='HTML',
        reply_markup=markup
    )

@bot.callback_query_handler(func=lambda call: call.data == "list_newsletters")
def callback_list_newsletters(call):
    show_newsletters_list(call.message.chat.id, page=1)
    bot.answer_callback_query(call.id)

@bot.callback_query_handler(func=lambda call: call.data.startswith("start_nl_"))
def callback_start_newsletter(call):
    """Запуск рассылки"""
    nl_id = int(call.data.split("_")[2])
    newsletter = get_newsletter(nl_id)
    
    if not newsletter:
        bot.answer_callback_query(call.id, "❌ Рассылка не найдена")
        return
    
    state = newsletter[5]
    
    if state == STATE_SENDING:
        bot.answer_callback_query(call.id, "⚠️ Рассылка уже отправляется!")
        return
    
    if state == STATE_COMPLETED:
        bot.answer_callback_query(call.id, "⚠️ Эта рассылка уже была отправлена!")
        return
    
    bot.answer_callback_query(call.id, "🚀 Запускаю рассылку...")
    
    # Запускаем рассылку в отдельном потоке
    start_newsletter_async(bot, nl_id, ADMIN)


# ==================== ОСНОВНЫЕ КОМАНДЫ БОТА ====================

@bot.message_handler(commands=['start'])
def send_welcome(message):
    args = message.text.split()
    zodiac_arg = args[1] if len(args) > 1 else None
    
    # Приветствие
    wlcMsg = f'<b>👋 Привет {message.from_user.first_name}</b>\n\n'
    
    # Если передан знак зодиака — показать только гороскоп
    if zodiac_arg and zodiac_arg in zodiac_signs.values():
        wlcMsg += getHoro(zodiac_arg, 'today')
    else:
        wlcMsg += getHoroTodayAll() + '\n\n⚛️ Выберите Ваш знак зодиака'
    
    bot.send_message(
        message.from_user.id,
        text=wlcMsg,
        reply_markup=get_zodiac_keyboard(),
        parse_mode="html",
        disable_web_page_preview=True
    )
    tgidregister(message.from_user.id, message.from_user.first_name)

@bot.message_handler(commands=['admin'])
def admin_panel(message):
    if message.from_user.id != ADMIN:
        return
    
    admin_text = (
        "👑 Панель администратора\n\n"
        "/stat - статистика бота\n"
        "/chat [link] - добавить/изменить ссылку на чат\n"
        "/newsletter - управление рассылками\n"
    )
    bot.reply_to(message, admin_text)

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
    current_name = get_name(message.from_user.id)
    
    if current_name:
        text = f"Ваше имя: <b>{current_name}</b>\n\nВведите новое имя или нажмите ❌ Отменить:"
    else:
        text = "Введите Ваше имя или нажмите ❌ Отменить:"
    
    msg = bot.send_message(
        message.chat.id,
        text,
        parse_mode="html",
        reply_markup=get_cancel_keyboard()
    )
    bot.register_next_step_handler(msg, save_new_name)

def save_new_name(message):
    if message.text.strip() == "❌ Отменить":
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
            "Имя должно содержать от 2 до 50 символов. Попробуйте снова или нажмите ❌ Отменить:",
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
            "Введите дату рождения в формате <b>ДЕНЬ.МЕСЯЦ.ГОД</b>\n\nПример: 3.5.1999 или 5.12.1998\n(Без нулей перед числами!)\n\nИли нажмите ❌ Отменить",
            parse_mode="html",
            reply_markup=get_cancel_keyboard()
        )
        bot.register_next_step_handler(msg, save_birthdate)

def save_birthdate(message):
    if message.text.strip() == "❌ Отменить":
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
            "Неверный формат даты! Введите снова в формате: <b>ДЕНЬ.МЕСЯЦ.ГОД</b>\nПример: 3.5.1999\n\nИли нажмите ❌ Отменить",
            parse_mode="html",
            reply_markup=get_cancel_keyboard()
        )
        bot.register_next_step_handler(msg, save_birthdate)
        return
    
    set_birthdate(message.from_user.id, date)
    bot.send_message(
        message.chat.id,
        f"✅ Дата рождения успешно сохранена: <b>{date}</b>",
        parse_mode="html",
        reply_markup=get_zodiac_keyboard()
    )

@bot.callback_query_handler(func=lambda call: call.data == "change_birthdate")
def change_birthdate(call):
    current_date = get_birthdate(call.from_user.id)
    text = f"Текущая дата рождения: <b>{current_date}</b>\n\nВведите новую дату рождения в формате <b>ДЕНЬ.МЕСЯЦ.ГОД</b>\nПример: 3.5.1999\n\nИли нажмите ❌ Отменить"
    
    msg = bot.send_message(
        call.message.chat.id,
        text,
        parse_mode="html",
        reply_markup=get_cancel_keyboard()
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
    
    # Обработка групповых чатов
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
        return  # ДОБАВИТЬ ЭТОТ RETURN!!! Чтобы не продолжать обработку для групп
    
    # Обработка личных сообщений
    sign = zodiac_signs.get(message.text)
    if sign:
        keyboard = types.InlineKeyboardMarkup()
        keyboard.add(*[InlineKeyboardButton(text=period, callback_data=f'{sign}|{period}') for period in period_map])
        bot.send_message(message.from_user.id, f'Получить гороскоп {message.text} на:', reply_markup=keyboard, parse_mode="html")

@bot.callback_query_handler(func=lambda call: True)
def callback_worker(call):
    data = call.data

    # Обрабатываем ТОЛЬКО гороскоп
    if data.startswith("horo_"):
        try:
            el = data.split("_")[1:]    
            if len(el) < 2:
                bot.answer_callback_query(call.id, "Ошибка: некорректные данные")
                return

            sign = el[0]
            period = el[1]

            bot.send_message(
                call.message.chat.id,
                getHoro(sign, period_map[period]),
                parse_mode="html",
                disable_web_page_preview=True
            )
        except Exception as e:
            print("Horo error:", e)
        return

bot.infinity_polling(interval=0)