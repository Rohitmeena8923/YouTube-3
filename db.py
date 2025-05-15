import sqlite3
from datetime import datetime

def init_db():
    conn = sqlite3.connect("botdata.db")
    c = conn.cursor()
    c.execute('''CREATE TABLE IF NOT EXISTS logs (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        user_id INTEGER,
        query TEXT,
        timestamp TEXT
    )''')
    conn.commit()
    conn.close()

def log_search(user_id, query):
    conn = sqlite3.connect("botdata.db")
    c = conn.cursor()
    c.execute("INSERT INTO logs (user_id, query, timestamp) VALUES (?, ?, ?)",
              (user_id, query, datetime.utcnow().isoformat()))
    conn.commit()
    conn.close()

init_db()