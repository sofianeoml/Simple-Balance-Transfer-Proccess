import os
import sqlite3

# Path to the database
DB_PATH = os.path.join(os.path.dirname(__file__), 'users.db')

def init_db():
    # Ensure the dbs directory exists
    os.makedirs(os.path.dirname(DB_PATH), exist_ok=True)

    # Connect to or create the database
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()

    # Create users table if it doesn't exist
    c.execute('''CREATE TABLE IF NOT EXISTS users (
        id INTEGER PRIMARY KEY,
        username TEXT UNIQUE NOT NULL,
        email TEXT UNIQUE NOT NULL,
        password TEXT NOT NULL,
        created_at INTEGER NOT NULL,
        balance REAL DEFAULT 0.0
    )''')

    conn.commit()
    conn.close()
    print(f"Database initialized at {DB_PATH}")

# Run init_db when this file is imported
init_db()