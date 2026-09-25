# migrate_db.py
import sqlite3
import os

DB = "expenses.db"

conn = sqlite3.connect(DB)
c = conn.cursor()

# Create history table if it doesn't exist
c.execute("""CREATE TABLE IF NOT EXISTS history (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    expense_id INTEGER,
    action TEXT,
    title TEXT,
    amount REAL,
    category TEXT,
    date TEXT,
    modified_at TEXT
)""")

# Ensure modified_at column exists in expenses
c.execute("PRAGMA table_info(expenses)")
cols = [row[1] for row in c.fetchall()]
if 'modified_at' not in cols:
    try:
        c.execute("ALTER TABLE expenses ADD COLUMN modified_at TEXT")
        print("Added modified_at column to expenses.")
    except Exception as e:
        print("Could not add column (maybe table missing):", e)
else:
    print("modified_at column already present.")

conn.commit()
conn.close()
print("Migration complete.")
