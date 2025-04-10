import sqlite3
import os
import uuid
import time

DB_PATH = os.path.join(os.path.dirname(__file__), 'transactions.db')

def init_db():
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    
    # Create transactions table
    c.execute('''CREATE TABLE IF NOT EXISTS transactions (
        id TEXT PRIMARY KEY,
        amount REAL NOT NULL,
        sender_id INTEGER NOT NULL,
        receiver_id INTEGER NOT NULL,
        created_at INTEGER NOT NULL
    )''')
    
    conn.commit()
    conn.close()

# Initialize the database when this module is imported
if not os.path.exists(DB_PATH):
    init_db()

# Function to add a transaction
def add_transaction(amount, sender_id, receiver_id):
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    
    transaction_id = str(uuid.uuid4())  # Random UUID
    created_at = int(time.time() * 1000)  # Current time in milliseconds
    
    c.execute('INSERT INTO transactions (id, amount, sender_id, receiver_id, created_at) VALUES (?, ?, ?, ?, ?)',
              (transaction_id, amount, sender_id, receiver_id, created_at))
    
    conn.commit()
    conn.close()
    return transaction_id