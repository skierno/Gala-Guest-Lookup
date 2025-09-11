# import_csv.py
import sqlite3, csv, os

DB = "guests.db"

# Create table if it doesn’t exist
def create_table(conn):
    conn.execute("""
    CREATE TABLE IF NOT EXISTS guests (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        first_name TEXT NOT NULL,
        last_name TEXT NOT NULL,
        full_name TEXT NOT NULL UNIQUE,
        table_number TEXT,
        paid INTEGER DEFAULT 0
    );
    """)
    conn.commit()

with sqlite3.connect(DB) as conn:
    create_table(conn)
    cur = conn.cursor()
    with open("guests.csv", newline='', encoding='utf-8') as f:
        reader = csv.DictReader(f)
        count = 0
        for row in reader:
            full = f"{row['first_name'].strip()} {row['last_name'].strip()}"
            cur.execute(
                "INSERT OR REPLACE INTO guests (first_name,last_name,full_name,table_number,paid) VALUES (?, ?, ?, ?, ?)",
                (row['first_name'].strip(), row['last_name'].strip(), full, row['table_number'].strip(), int(row['paid']))
            )
            count += 1
    conn.commit()
print(f"Imported {count} guests into {DB}")
