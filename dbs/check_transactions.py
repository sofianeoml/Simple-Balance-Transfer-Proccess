import sqlite3
import os
from datetime import datetime

# Database paths
TRANSACTIONS_DB_PATH = os.path.join(os.path.dirname(__file__), 'transactions.db')
USERS_DB_PATH = os.path.join(os.path.dirname(__file__), 'users.db')

# Reasonable timestamp range (e.g., after 2020 and before 2030 in milliseconds)
MIN_TIMESTAMP = int(datetime(2020, 1, 1).timestamp() * 1000)  # 1577836800000
MAX_TIMESTAMP = int(datetime(2030, 1, 1).timestamp() * 1000)  # 1893456000000

def check_and_fix_transactions():
    # Connect to both databases
    transactions_conn = sqlite3.connect(TRANSACTIONS_DB_PATH)
    users_conn = sqlite3.connect(USERS_DB_PATH)
    
    t_cursor = transactions_conn.cursor()
    u_cursor = users_conn.cursor()
    
    # Fetch all transactions
    t_cursor.execute('SELECT id, amount, sender_id, receiver_id, created_at FROM transactions')
    transactions = t_cursor.fetchall()
    
    # Track invalid transactions
    invalid_transactions = []
    
    for transaction in transactions:
        transaction_id, amount, sender_id, receiver_id, created_at = transaction
        is_invalid = False
        
        # Check 1: User IDs exist
        u_cursor.execute('SELECT COUNT(*) FROM users WHERE id = ?', (sender_id,))
        sender_exists = u_cursor.fetchone()[0] > 0
        u_cursor.execute('SELECT COUNT(*) FROM users WHERE id = ?', (receiver_id,))
        receiver_exists = u_cursor.fetchone()[0] > 0
        
        if not sender_exists or not receiver_exists:
            print(f"Transaction {transaction_id}: User ID not found (Sender: {sender_id}, Receiver: {receiver_id})")
            is_invalid = True
        
        # Check 2: Amount error (should be positive, negative is a bug)
        if amount <= 0:
            print(f"Transaction {transaction_id}: Invalid amount ({amount})")
            is_invalid = True
        
        # Check 3: Time invalid
        if created_at < MIN_TIMESTAMP or created_at > MAX_TIMESTAMP:
            print(f"Transaction {transaction_id}: Invalid timestamp ({created_at})")
            is_invalid = True
        
        if is_invalid:
            invalid_transactions.append(transaction)
    
    # Process invalid transactions
    for transaction in invalid_transactions:
        transaction_id, amount, sender_id, receiver_id, created_at = transaction
        
        # Reverse the transaction in users table
        try:
            u_cursor.execute('UPDATE users SET balance = balance + ? WHERE id = ?', (amount, sender_id))
            u_cursor.execute('UPDATE users SET balance = balance - ? WHERE id = ?', (amount, receiver_id))
            print(f"Reversed transaction {transaction_id}: Sender {sender_id} +{amount}, Receiver {receiver_id} -{amount}")
        except sqlite3.Error as e:
            print(f"Error reversing transaction {transaction_id}: {e}")
        
        # Delete the transaction
        t_cursor.execute('DELETE FROM transactions WHERE id = ?', (transaction_id,))
        print(f"Deleted transaction {transaction_id}")
    
    # Commit changes
    users_conn.commit()
    transactions_conn.commit()
    
    # Close connections
    transactions_conn.close()
    users_conn.close()
    
    if not invalid_transactions:
        print("No invalid transactions found.")

if __name__ == '__main__':
    check_and_fix_transactions()