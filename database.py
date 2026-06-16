import sqlite3

conn = sqlite3.connect("chaos.db", check_same_thread=False)

cursor = conn.cursor()

cursor.execute("""
CREATE TABLE IF NOT EXISTS experiments (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    experiment TEXT,
    namespace TEXT,
    target TEXT,
    status TEXT
)
""")

conn.commit()