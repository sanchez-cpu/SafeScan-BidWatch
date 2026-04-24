import sqlite3
import pandas as pd
from datetime import datetime

DB = "bids.db"

def init_db():
    conn = sqlite3.connect(DB)
    conn.execute("""
        CREATE TABLE IF NOT EXISTS bids (
            id TEXT PRIMARY KEY,
            title TEXT,
            agency TEXT,
            url TEXT,
            due_date TEXT,
            description TEXT,
            keywords_matched TEXT,
            first_seen TEXT,
            status TEXT DEFAULT 'New'
        )
    """)
    conn.commit()
    conn.close()
    print("✅ Database initialized.")

def save_bid(bid):
    init_db()  # Ensure DB exists
    conn = sqlite3.connect(DB)
    try:
        conn.execute("""
            INSERT OR IGNORE INTO bids 
            (id, title, agency, url, due_date, description, keywords_matched, first_seen, status)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, (
            bid['id'], bid['title'], bid['agency'], bid['url'],
            bid.get('due_date', ''), bid.get('description', ''),
            bid.get('keywords_matched', ''), datetime.now().isoformat(), 'New'
        ))
        conn.commit()
        return True
    except Exception as e:
        print(f"Save error: {e}")
        return False
    finally:
        conn.close()

def get_all_bids():
    init_db()
    conn = sqlite3.connect(DB)
    df = pd.read_sql("SELECT * FROM bids ORDER BY first_seen DESC", conn)
    conn.close()
    return df