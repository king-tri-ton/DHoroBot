import threading
import time
from datetime import datetime

# Состояния рассылки
STATE_CREATING  = 0
STATE_READY     = 1
STATE_SENDING   = 3
STATE_COMPLETED = 4

def send_newsletter(bot, nl_id, admin_id):
    """Отправка рассылки в отдельном потоке"""
    from db import (
        get_newsletter, 
        set_newsletter_state, 
        update_newsletter_stats,
        get_all_users_tgid
    )
    
    try:
        # Получаем данные рассылки
        newsletter = get_newsletter(nl_id)
        if not newsletter:
            bot.send_message(admin_id, "❌ Рассылка не найдена!")
            return
        
        nl_type = newsletter[2]
        text = newsletter[3]
        photo_file_id = newsletter[4]
        
        # Получаем всех пользователей
        users = get_all_users_tgid()
        
        if not users:
            bot.send_message(admin_id, "❌ Нет пользователей для рассылки!")
            set_newsletter_state(nl_id, STATE_READY)
            return
        
        # Обновляем статус на "отправка"
        set_newsletter_state(nl_id, STATE_SENDING)
        started_at = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        update_newsletter_stats(nl_id, 'started_at', started_at)
        update_newsletter_stats(nl_id, 'total_users', len(users))
        
        bot.send_message(admin_id, f"📨 Начинаю рассылку!\nВсего пользователей: {len(users)}")
        
        successful = 0
        failed = 0
        
        for i, user_id in enumerate(users, 1):
            try:
                if nl_type == 'text':
                    bot.send_message(user_id, text, parse_mode='HTML', disable_web_page_preview=True)
                elif nl_type == 'caption' and photo_file_id:
                    bot.send_photo(user_id, photo_file_id, caption=text, parse_mode='HTML')
                
                successful += 1
                
                # Обновляем прогресс каждые 50 сообщений
                if i % 50 == 0:
                    bot.send_message(admin_id, f"📊 Прогресс: {i}/{len(users)}")
                
                time.sleep(0.05) # Небольшая задержка
                
            except Exception as e:
                failed += 1
                print(f"Ошибка отправки пользователю {user_id}: {e}")
        
        # Завершаем рассылку
        completed_at = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        set_newsletter_state(nl_id, STATE_COMPLETED)
        update_newsletter_stats(nl_id, 'completed_at', completed_at)
        update_newsletter_stats(nl_id, 'successful', successful)
        update_newsletter_stats(nl_id, 'failed', failed)
        
        # Отправляем отчет админу
        report = f"""
✅ <b>Рассылка завершена!</b>

📊 <b>Статистика:</b>
• Всего пользователей: {len(users)}
• Успешно: {successful}
• Ошибок: {failed}
• Процент успеха: {(successful/len(users)*100):.2f}%

⏰ Время начала: {started_at}
⏰ Время завершения: {completed_at}
"""
        bot.send_message(admin_id, report, parse_mode='HTML')
        
    except Exception as e:
        print(f"Критическая ошибка рассылки: {e}")
        bot.send_message(admin_id, f"❌ Критическая ошибка: {e}")
        from db import set_newsletter_state
        set_newsletter_state(nl_id, STATE_READY)

def start_newsletter_async(bot, nl_id, admin_id):
    """Запуск рассылки в отдельном потоке"""
    thread = threading.Thread(target=send_newsletter, args=(bot, nl_id, admin_id))
    thread.daemon = True
    thread.start()