from database.db import get_connection

def create_tables():
    conn = get_connection()
    cur = conn.cursor()

    cur.execute("""
    CREATE TABLE IF NOT EXISTS users (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        username TEXT UNIQUE,
        password TEXT
    )
    """)

    cur.execute("""
    CREATE TABLE IF NOT EXISTS goals (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        user_id INTEGER,
        name TEXT
    )
    """)

    cur.execute("""
    CREATE TABLE IF NOT EXISTS sub_goals (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        goal_id INTEGER,
        name TEXT,
        active INTEGER DEFAULT 1
    )
    """)

    cur.execute("""
    CREATE TABLE IF NOT EXISTS daily_logs (
        sub_goal_id INTEGER,
        date TEXT,
        completed INTEGER,
        PRIMARY KEY (sub_goal_id, date)
    )
    """)

    conn.commit()
    conn.close()
