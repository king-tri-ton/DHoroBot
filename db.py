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