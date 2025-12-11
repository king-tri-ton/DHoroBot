import sqlite3

conn = sqlite3.connect('horo.db', check_same_thread=False)

def init_db():
    try:
        cur = conn.cursor()
        cur.execute("""
            CREATE TABLE IF NOT EXISTS users (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                tgid INTEGER UNIQUE
            );
        """)
        cur.execute("""
            CREATE TABLE IF NOT EXISTS settings (
                key TEXT PRIMARY KEY,
                value TEXT
            );
        """)
        cur.execute("""
            CREATE TABLE IF NOT EXISTS groups (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                chat_id INTEGER UNIQUE,
                chat_type TEXT
            );
        """)
        cur.execute("""
            CREATE TABLE IF NOT EXISTS newsletters (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT NOT NULL,
                type TEXT,
                text TEXT,
                photo_file_id TEXT,
                state INTEGER DEFAULT 0,
                created_at TEXT,
                started_at TEXT,
                completed_at TEXT,
                total_users INTEGER DEFAULT 0,
                successful INTEGER DEFAULT 0,
                failed INTEGER DEFAULT 0,
                step TEXT DEFAULT 'name'
            );
        """)
        
        # Проверка и добавление новых колонок в таблице users
        cur.execute("PRAGMA table_info(users);")
        user_columns = [col[1] for col in cur.fetchall()]
        
        if 'name' not in user_columns:
            cur.execute("ALTER TABLE users ADD COLUMN name TEXT;")
        if 'birthdate' not in user_columns:
            cur.execute("ALTER TABLE users ADD COLUMN birthdate TEXT;")
        
        # Проверяем поля у groups
        cur.execute("PRAGMA table_info(groups);")
        group_columns = [col[1] for col in cur.fetchall()]
        
        if 'title' not in group_columns:
            cur.execute("ALTER TABLE groups ADD COLUMN title TEXT;")
        if 'username' not in group_columns:
            cur.execute("ALTER TABLE groups ADD COLUMN username TEXT;")
        
        # Проверяем поле step у newsletters
        cur.execute("PRAGMA table_info(newsletters);")
        nl_columns = [col[1] for col in cur.fetchall()]
        
        if 'step' not in nl_columns:
            cur.execute("ALTER TABLE newsletters ADD COLUMN step TEXT DEFAULT 'name';")
        
        conn.commit()
    except Exception as e:
        print(e)

init_db()

# ==================== ФУНКЦИИ ДЛЯ ПОЛЬЗОВАТЕЛЕЙ ====================

def tgidregister(tid, name=None):
    try:
        cur = conn.cursor()
        cur.execute("INSERT OR IGNORE INTO users (tgid) VALUES(?);", (tid,))
        cur.execute("SELECT name FROM users WHERE tgid = ?;", (tid,))
        row = cur.fetchone()
        current_name = row[0] if row else None
        
        if not current_name and name:
            cur.execute("UPDATE users SET name = ? WHERE tgid = ?;", (name, tid))
        
        conn.commit()
    except Exception as e:
        print(e)

def get_name(tgid):
    """Получить имя пользователя"""
    try:
        cur = conn.cursor()
        cur.execute("SELECT name FROM users WHERE tgid = ?;", (tgid,))
        row = cur.fetchone()
        return row[0] if row else None
    except Exception as e:
        print(e)
        return None

def set_name(tgid, name):
    try:
        cur = conn.cursor()
        cur.execute("UPDATE users SET name = ? WHERE tgid = ?;", (name, tgid))
        conn.commit()
    except Exception as e:
        print(e)

def get_birthdate(tgid):
    try:
        cur = conn.cursor()
        cur.execute("SELECT birthdate FROM users WHERE tgid = ?;", (tgid,))
        row = cur.fetchone()
        return row[0] if row else None
    except Exception as e:
        print(e)
        return None

def set_birthdate(tgid, date):
    try:
        cur = conn.cursor()
        cur.execute("UPDATE users SET birthdate = ? WHERE tgid = ?;", (date, tgid))
        conn.commit()
    except Exception as e:
        print(e)

def countusers():
    """Для админа"""
    try:
        cur = conn.cursor()
        cur.execute("SELECT COUNT(*) FROM users;")
        countusers = cur.fetchall()[0][0]
        return str(countusers)
    except Exception as e:
        print(e)

def getusers():
    """Для админа"""
    try:
        cur = conn.cursor()
        cur.execute("SELECT * FROM users;")
        getuser = cur.fetchall()
        return getuser
    except Exception as e:
        print(e)

def get_all_users_tgid():
    """Получить список всех tgid для рассылки"""
    try:
        cur = conn.cursor()
        cur.execute("SELECT tgid FROM users;")
        return [row[0] for row in cur.fetchall()]
    except Exception as e:
        print(f"Ошибка получения пользователей: {e}")
        return []

# ==================== ФУНКЦИИ ДЛЯ НАСТРОЕК ====================

def set_chat_link(link):
    """Для админа"""
    try:
        cur = conn.cursor()
        cur.execute("INSERT OR REPLACE INTO settings (key, value) VALUES ('chat_link', ?);", (link,))
        conn.commit()
    except Exception as e:
        print(e)

def get_chat_link():
    try:
        cur = conn.cursor()
        cur.execute("SELECT value FROM settings WHERE key = 'chat_link';")
        row = cur.fetchone()
        return row[0] if row else None
    except Exception as e:
        print(e)
        return None

# ==================== ФУНКЦИИ ДЛЯ ГРУПП ====================

def register_group(chat_id, chat_type, title=None, username=None):
    try:
        cur = conn.cursor()
        cur.execute(
            "INSERT OR IGNORE INTO groups (chat_id, chat_type, title, username) VALUES (?, ?, ?, ?);",
            (chat_id, chat_type, title, username)
        )
        conn.commit()
    except Exception as e:
        print(e)

def countgroups():
    try:
        cur = conn.cursor()
        cur.execute("SELECT COUNT(*) FROM groups;")
        return str(cur.fetchone()[0])
    except Exception as e:
        print(e)
        return "0"

# ==================== ФУНКЦИИ ДЛЯ РАССЫЛКИ ====================

def create_newsletter_initial():
    """Создать начальную запись рассылки"""
    try:
        from datetime import datetime
        cur = conn.cursor()
        created_at = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        cur.execute(
            "INSERT INTO newsletters (name, state, created_at, step) VALUES (?, ?, ?, ?);",
            ('Новая рассылка', 0, created_at, 'name')
        )
        conn.commit()
        return cur.lastrowid
    except Exception as e:
        print(f"Ошибка создания рассылки: {e}")
        return None

def get_active_newsletter_creation(admin_id=None):
    """Получить активную создаваемую рассылку"""
    try:
        cur = conn.cursor()
        cur.execute("SELECT * FROM newsletters WHERE state = 0 ORDER BY id DESC LIMIT 1;")
        return cur.fetchone()
    except Exception as e:
        print(f"Ошибка получения активной рассылки: {e}")
        return None

def update_newsletter_stats(nl_id, field, value):
    """Обновить любое поле рассылки"""
    try:
        cur = conn.cursor()
        cur.execute(f"UPDATE newsletters SET {field} = ? WHERE id = ?;", (value, nl_id))
        conn.commit()
        return True
    except Exception as e:
        print(f"Ошибка обновления поля {field}: {e}")
        return False

def update_newsletter_name(nl_id, name):
    """Обновить название рассылки"""
    return update_newsletter_stats(nl_id, 'name', name)

def update_newsletter_type(nl_id, nl_type):
    """Обновить тип рассылки"""
    return update_newsletter_stats(nl_id, 'type', nl_type)

def update_newsletter_text(nl_id, text):
    """Обновить текст рассылки"""
    return update_newsletter_stats(nl_id, 'text', text)

def update_newsletter_photo(nl_id, file_id):
    """Обновить file_id фото"""
    return update_newsletter_stats(nl_id, 'photo_file_id', file_id)

def update_newsletter_step(nl_id, step):
    """Обновить текущий шаг создания"""
    return update_newsletter_stats(nl_id, 'step', step)

def set_newsletter_state(nl_id, state):
    """Изменить состояние рассылки"""
    return update_newsletter_stats(nl_id, 'state', state)

def get_newsletter(nl_id):
    """Получить рассылку по ID"""
    try:
        cur = conn.cursor()
        cur.execute("SELECT * FROM newsletters WHERE id = ?;", (nl_id,))
        return cur.fetchone()
    except Exception as e:
        print(f"Ошибка получения рассылки: {e}")
        return None

def get_all_newsletters():
    """Получить все рассылки"""
    try:
        cur = conn.cursor()
        cur.execute("SELECT * FROM newsletters ORDER BY id DESC;")
        return cur.fetchall()
    except Exception as e:
        print(f"Ошибка получения рассылок: {e}")
        return []

def cancel_newsletter_creation(nl_id):
    """Отменить создание рассылки (удалить из БД)"""
    try:
        cur = conn.cursor()
        cur.execute("DELETE FROM newsletters WHERE id = ? AND state = 0;", (nl_id,))
        conn.commit()
        return True
    except Exception as e:
        print(f"Ошибка отмены создания: {e}")
        return False