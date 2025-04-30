"""
Manual migration script to add department_id column to users table.
"""
import sqlite3

DB_PATH = "appraisal.db"  # Change this if your DB file is named differently

def migrate():
    conn = sqlite3.connect(DB_PATH)
    cur = conn.cursor()
    # Check if column already exists
    cur.execute("PRAGMA table_info(users)")
    columns = [row[1] for row in cur.fetchall()]
    if "department_id" not in columns:
        cur.execute("ALTER TABLE users ADD COLUMN department_id INTEGER")
        print("Added department_id column to users table.")
    else:
        print("department_id column already exists.")
    conn.commit()
    conn.close()

if __name__ == "__main__":
    migrate()
