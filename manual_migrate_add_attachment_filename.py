"""
Manual migration script to add attachment_filename column to appraisals table.
"""
import sqlite3

DB_PATH = "appraisal.db"  # Change this if your DB file is named differently

def migrate():
    conn = sqlite3.connect(DB_PATH)
    cur = conn.cursor()
    # Check if column already exists
    cur.execute("PRAGMA table_info(appraisals)")
    columns = [row[1] for row in cur.fetchall()]
    if "attachment_filename" not in columns:
        # Add the column, allowing NULL values initially
        cur.execute("ALTER TABLE appraisals ADD COLUMN attachment_filename TEXT")
        print("Added attachment_filename column to appraisals table.")
    else:
        print("attachment_filename column already exists.")
    conn.commit()
    conn.close()

if __name__ == "__main__":
    migrate()
