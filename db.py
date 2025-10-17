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

        cur.execute("PRAGMA table_info(users);")
        columns = [col[1] for col in cur.fetchall()]

        if 'name' not in columns:
            cur.execute("ALTER TABLE users ADD COLUMN name TEXT;")
        if 'birthdate' not in columns:
            cur.execute("ALTER TABLE users ADD COLUMN birthdate TEXT;")

        conn.commit()
    except Exception as e:
        print(e)

init_db()

def tgidregister(tid):
    try:
        cur = conn.cursor()
        cur.execute("INSERT OR IGNORE INTO users (tgid) VALUES(?);", (tid,))
        conn.commit()
    except Exception as e:
        print(e)

def countusers(): # для админа
    try:
        cur = conn.cursor()
        cur.execute("SELECT COUNT(*) FROM users;")
        countusers = cur.fetchall()[0][0]
        return str(countusers)
    except Exception as e:
        print(e)

def getusers(): # для админа
    try:
        cur = conn.cursor()
        cur.execute("SELECT * FROM users;")
        getuser = cur.fetchall()
        return getuser
    except Exception as e:
        print(e)

def set_chat_link(link):
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

def register_group(chat_id, chat_type):
    try:
        cur = conn.cursor()
        cur.execute("INSERT OR IGNORE INTO groups (chat_id, chat_type) VALUES (?, ?);", (chat_id, chat_type))
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