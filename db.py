import sqlite3
from datetime import datetime, timedelta
from contextlib import contextmanager
from config import UTC

DB_PATH = 'horo.db'

@contextmanager
def get_db():
	"""Создает новое соединение для каждой операции"""
	conn = sqlite3.connect(DB_PATH, timeout=10)
	try:
		yield conn
		conn.commit()
	except Exception as e:
		conn.rollback()
		print(f"Database error: {e}")
		raise
	finally:
		conn.close()


def init_db():
	with get_db() as conn:
		cur = conn.cursor()
		
		# --- USERS ---
		cur.execute("""
			CREATE TABLE IF NOT EXISTS users (
				id INTEGER PRIMARY KEY AUTOINCREMENT,
				tgid INTEGER UNIQUE
			);
		""")
		
		# Проверяем и добавляем колонки
		cur.execute("PRAGMA table_info(users);")
		user_columns = [col[1] for col in cur.fetchall()]
		
		if 'name' not in user_columns:
			cur.execute("ALTER TABLE users ADD COLUMN name TEXT;")
		if 'birthdate' not in user_columns:
			cur.execute("ALTER TABLE users ADD COLUMN birthdate TEXT;")
		if 'registered_at' not in user_columns:
			cur.execute("ALTER TABLE users ADD COLUMN registered_at TEXT;")
		
		# !!! НОВАЯ КОЛОНКА ДЛЯ БАЛАНСА !!!
		if 'balance' not in user_columns:
			cur.execute("ALTER TABLE users ADD COLUMN balance INTEGER DEFAULT 0;")

		# --- SETTINGS ---
		cur.execute("""
			CREATE TABLE IF NOT EXISTS settings (
				key TEXT PRIMARY KEY,
				value TEXT
			);
		""")

		# --- GROUPS ---
		cur.execute("""
			CREATE TABLE IF NOT EXISTS groups (
				id INTEGER PRIMARY KEY AUTOINCREMENT,
				chat_id INTEGER UNIQUE,
				chat_type TEXT
			);
		""")
		cur.execute("PRAGMA table_info(groups);")
		group_columns = [col[1] for col in cur.fetchall()]
		if 'title' not in group_columns:
			cur.execute("ALTER TABLE groups ADD COLUMN title TEXT;")
		if 'username' not in group_columns:
			cur.execute("ALTER TABLE groups ADD COLUMN username TEXT;")
		if 'registered_at' not in group_columns:
			cur.execute("ALTER TABLE groups ADD COLUMN registered_at TEXT;")

		# --- PERSONAL HOROSCOPES ---
		cur.execute("""
			CREATE TABLE IF NOT EXISTS personal_horoscopes (
				id INTEGER PRIMARY KEY AUTOINCREMENT,
				tgid INTEGER NOT NULL,
				period_key TEXT NOT NULL,
				horoscope_text TEXT NOT NULL,
				created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
				rating INTEGER DEFAULT 0,
				feedback TEXT
			);
		""")
		
		# --- PAYMENTS (Таблица для истории платежей - полезно иметь) ---
		cur.execute("""
			CREATE TABLE IF NOT EXISTS payments (
				id INTEGER PRIMARY KEY AUTOINCREMENT,
				tgid INTEGER NOT NULL,
				amount_stars INTEGER NOT NULL,
				requests_added INTEGER NOT NULL,
				created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
				payment_id TEXT
			);
		""")

		conn.commit()
		
		# Индексы
		cur.execute("CREATE INDEX IF NOT EXISTS idx_users_tgid ON users(tgid);")
		cur.execute("CREATE INDEX IF NOT EXISTS idx_groups_chat_id ON groups(chat_id);")

init_db()



# ==================== ФУНКЦИЯ РЕГИСТРАЦИИ ПОЛЬЗОВАТЕЛЯ ====================

def tgidregister(tid, name=None):
	"""Регистрация пользователя"""
	with get_db() as conn:  # ← используем with get_db()
		cur = conn.cursor()
		now = datetime.utcnow() + timedelta(hours=UTC)
		cur.execute("""
			INSERT OR IGNORE INTO users (tgid, registered_at)
			VALUES (?, ?);
		""", (tid, now.isoformat()))
		
		if name:
			cur.execute("SELECT name FROM users WHERE tgid = ?;", (tid,))
			row = cur.fetchone()
			if not row or not row[0]:
				cur.execute("UPDATE users SET name = ? WHERE tgid = ?;", (name, tid))

def countusers():
	"""Для админа"""
	with get_db() as conn:  # ← используем with get_db()
		cur = conn.cursor()
		cur.execute("SELECT COUNT(*) FROM users;")
		return cur.fetchone()[0]  # возвращаем int




# ==================== ФУНКЦИИ РЕГИСТРАЦИИ ГРУПП ====================

def register_group(chat_id, chat_type, title=None, username=None):
	with get_db() as conn:  # ← используем with get_db()
		cur = conn.cursor()
		now = datetime.utcnow() + timedelta(hours=UTC)
		cur.execute("""
			INSERT OR IGNORE INTO groups
			(chat_id, chat_type, title, username, registered_at)
			VALUES (?, ?, ?, ?, ?);
		""", (chat_id, chat_type, title, username, now.isoformat()))

def countgroups():
	with get_db() as conn:  # ← используем with get_db()
		cur = conn.cursor()
		cur.execute("SELECT COUNT(*) FROM groups;")
		return cur.fetchone()[0]  # возвращаем int




# ==================== ФУНКЦИИ ДЛЯ ИМЕНИ ====================

def get_name(tgid):
	"""Получить имя пользователя"""
	with get_db() as conn:  # ← используем with get_db()
		cur = conn.cursor()
		cur.execute("SELECT name FROM users WHERE tgid = ?;", (tgid,))
		row = cur.fetchone()
		return row[0] if row else None

def set_name(tgid, name):
	with get_db() as conn:  # ← используем with get_db()
		cur = conn.cursor()
		cur.execute("UPDATE users SET name = ? WHERE tgid = ?;", (name, tgid))


# ==================== ФУНКЦИИ ДЛЯ ДАТЫ РОЖДЕНИЯ ====================

def get_birthdate(tgid):
	with get_db() as conn:  # ← используем with get_db()
		cur = conn.cursor()
		cur.execute("SELECT birthdate FROM users WHERE tgid = ?;", (tgid,))
		row = cur.fetchone()
		return row[0] if row else None

def set_birthdate(tgid, date):
	with get_db() as conn:  # ← используем with get_db()
		cur = conn.cursor()
		cur.execute("UPDATE users SET birthdate = ? WHERE tgid = ?;", (date, tgid))



# ==================== ФУНКЦИИ ДЛЯ НАСТРОЕК ====================

def set_chat_link(link):
	"""Для админа"""
	with get_db() as conn:  # ← используем with get_db()
		cur = conn.cursor()
		cur.execute("INSERT OR REPLACE INTO settings (key, value) VALUES ('chat_link', ?);", (link,))

def get_chat_link():
	with get_db() as conn:  # ← используем with get_db()
		cur = conn.cursor()
		cur.execute("SELECT value FROM settings WHERE key = 'chat_link';")
		row = cur.fetchone()
		return row[0] if row else None




# ==================== ФУНКЦИИ БАЛАНСА ====================

def get_user_balance(tgid):
	"""Получить текущий баланс пользователя"""
	with get_db() as conn:
		cur = conn.cursor()
		cur.execute("SELECT balance FROM users WHERE tgid = ?;", (tgid,))
		row = cur.fetchone()
		# Если balance NULL (для старых юзеров), вернем 0
		return row[0] if row and row[0] is not None else 0

def update_user_balance(tgid, amount):
	"""
	Изменить баланс. 
	amount > 0 для начисления, 
	amount < 0 для списания.
	"""
	with get_db() as conn:
		cur = conn.cursor()
		# COALESCE превращает NULL в 0, если поле было пустым
		cur.execute("""
			UPDATE users 
			SET balance = COALESCE(balance, 0) + ? 
			WHERE tgid = ?;
		""", (amount, tgid))

def add_payment_record(tgid, stars, requests, payment_id):
	"""Записать факт оплаты в историю"""
	with get_db() as conn:
		cur = conn.cursor()
		cur.execute("""
			INSERT INTO payments (tgid, amount_stars, requests_added, payment_id)
			VALUES (?, ?, ?, ?)
		""", (tgid, stars, requests, payment_id))




def add_personal_horoscope(tgid, period_key, horoscope_text):
	"""Добавляем сгенерированный персональный гороскоп в базу"""
	with get_db() as conn:
		cur = conn.cursor()
		cur.execute("""
			INSERT INTO personal_horoscopes (tgid, period_key, horoscope_text)
			VALUES (?, ?, ?)
		""", (tgid, period_key, horoscope_text))
		return cur.lastrowid  # возвращаем id записи

def get_personal_horoscope(horoscope_id):
	"""Получаем гороскоп по id"""
	with get_db() as conn:
		cur = conn.cursor()
		cur.execute("""
			SELECT id, tgid, period_key, horoscope_text, rating, feedback
			FROM personal_horoscopes
			WHERE id = ?
		""", (horoscope_id,))
		return cur.fetchone()

def update_horoscope_rating(horoscope_id, rating):
	"""Обновляем оценку гороскопа (1 или -1)"""
	with get_db() as conn:
		cur = conn.cursor()
		cur.execute("""
			UPDATE personal_horoscopes SET rating = ? WHERE id = ?
		""", (rating, horoscope_id))

def update_horoscope_feedback(horoscope_id, feedback):
	"""Добавляем текстовый отзыв к гороскопу"""
	with get_db() as conn:
		cur = conn.cursor()
		cur.execute("""
			UPDATE personal_horoscopes SET feedback = ? WHERE id = ?
		""", (feedback, horoscope_id))


def check_free_horoscope_today(tgid):
	"""
	Проверяет, получал ли пользователь бесплатный персональный гороскоп (период 'today') 
	за последние 24 часа.
	Возвращает True, если уже получал, False, если нет.
	"""
	with get_db() as conn:
		cur = conn.cursor()
		
		# Получаем текущее время по UTC + ваша зона для сравнения
		now = datetime.utcnow() + timedelta(hours=UTC)
		yesterday = (now - timedelta(days=1)).isoformat()
		
		cur.execute("""
			SELECT COUNT(*) FROM personal_horoscopes 
			WHERE tgid = ? AND period_key = 'today' AND created_at > ?
		""", (tgid, yesterday))
		
		count = cur.fetchone()[0]
		return count > 0 # Если count > 0, значит, уже получал
