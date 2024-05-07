import sqlite3

conn = sqlite3.connect('horo.db', check_same_thread=False)

def tgidregister(tid):
	try:
		cur = conn.cursor()
		cur.execute("INSERT INTO users (tgid) VALUES(?);", (tid, ))
		conn.commit()
	except Exception as e:
		print(e)

def countusers(): # for admin
	try:
		cur = conn.cursor()
		cur.execute("SELECT COUNT(*) FROM users;")
		conn.commit()
		countusers = cur.fetchall()[0][0]
		return str(countusers)
	except Exception as e:
		print(e)

def getusers(): # for admin
	try:
		cur = conn.cursor()
		cur.execute("SELECT * FROM users;")
		conn.commit()
		getuser = cur.fetchall()
		return getuser
	except Exception as e:
		print(e)