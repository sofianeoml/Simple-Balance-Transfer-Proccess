import jwt
import sqlite3
from flask import render_template, request, abort, redirect, jsonify
from apis.signup_api import signup_bp
from apis.login_api import login_bp
from apis.logout_api import logout_bp
from dbs.users import DB_PATH as USERS_DB_PATH
from dbs.transactions import DB_PATH as TRANSACTIONS_DB_PATH, add_transaction
from datetime import datetime

SECRET_KEY = '1XSEC'
MIN_TIMESTAMP = int(datetime(2020, 1, 1).timestamp() * 1000)  # 1577836800000
MAX_TIMESTAMP = int(datetime(2030, 1, 1).timestamp() * 1000)  # 1893456000000

def init_routes(app):
    app.register_blueprint(signup_bp, url_prefix='/api')
    app.register_blueprint(login_bp, url_prefix='/api')
    app.register_blueprint(logout_bp)

    @app.route('/')
    def home():
        token = request.cookies.get('Authorization')
        if token:
            return redirect('/profile')
        else:
            return redirect('/login')

    @app.route('/signup')
    def signup():
        token = request.cookies.get('Authorization')
        if token:
            return redirect('/profile')
        else:
            return render_template('signup.html')

    @app.route('/login')
    def login():
        token = request.cookies.get('Authorization')
        if token:
            return redirect('/profile')
        else:
            return render_template('login.html')

    @app.route('/profile')
    def profile():
        token = request.cookies.get('Authorization')
        if not token:
            return redirect('/logout')

        try:
            payload = jwt.decode(token, SECRET_KEY, algorithms=['HS256'])
            user_id = payload['user_id']

            conn = sqlite3.connect(USERS_DB_PATH)
            c = conn.cursor()
            c.execute('SELECT username, email, created_at, balance FROM users WHERE id = ?', (user_id,))
            current_user = c.fetchone()

            c.execute('SELECT id, username, balance FROM users WHERE id != ? LIMIT 5', (user_id,))
            other_users = c.fetchall()
            conn.close()

            if current_user:
                username, email, created_at, balance = current_user
                return render_template('profile.html', 
                                      username=username, 
                                      email=email, 
                                      created_at=created_at, 
                                      balance=balance, 
                                      other_users=other_users,
                                      offset=5)
            else:
                return redirect('/logout')
        except jwt.InvalidTokenError:
            return redirect('/logout')

    @app.route('/api/users', methods=['GET'])
    def get_users():
        token = request.cookies.get('Authorization')
        if not token:
            return jsonify({'error': 'Unauthorized'}), 401

        try:
            payload = jwt.decode(token, SECRET_KEY, algorithms=['HS256'])
            user_id = payload['user_id']

            offset = int(request.args.get('offset', 0))
            conn = sqlite3.connect(USERS_DB_PATH)
            c = conn.cursor()
            c.execute('SELECT id, username, balance FROM users WHERE id != ? LIMIT 5 OFFSET ?', 
                      (user_id, offset))
            users = c.fetchall()
            conn.close()

            return jsonify({'users': [{'id': u[0], 'username': u[1], 'balance': u[2]} for u in users]})
        except jwt.InvalidTokenError:
            return jsonify({'error': 'Invalid token'}), 401

    @app.route('/api/transfer', methods=['POST'])
    def transfer_balance():
        token = request.cookies.get('Authorization')
        if not token:
            return jsonify({'error': 'Unauthorized'}), 401

        try:
            payload = jwt.decode(token, SECRET_KEY, algorithms=['HS256'])
            sender_id = payload['user_id']

            data = request.get_json()
            recipient_username = data.get('username')
            amount = float(data.get('amount', 0))

            conn = sqlite3.connect(USERS_DB_PATH)
            c = conn.cursor()

            c.execute('SELECT balance FROM users WHERE id = ?', (sender_id,))
            sender_balance = c.fetchone()
            if not sender_balance:
                conn.close()
                return jsonify({'result': False, 'message': 'Sender not found'}), 404
            sender_balance = sender_balance[0]

            if sender_balance < amount:
                conn.close()
                return jsonify({'result': False, 'message': 'Insufficient balance'}), 400

            c.execute('SELECT id FROM users WHERE username = ?', (recipient_username,))
            recipient = c.fetchone()
            if not recipient:
                conn.close()
                return jsonify({'result': False, 'message': 'Username not found'}), 404
            recipient_id = recipient[0]

            if recipient_id == sender_id:
                conn.close()
                return jsonify({'result': False, 'message': 'Cannot transfer to yourself'}), 400

            c.execute('UPDATE users SET balance = balance - ? WHERE id = ?', (amount, sender_id))
            c.execute('UPDATE users SET balance = balance + ? WHERE id = ?', (amount, recipient_id))
            
            transaction_id = add_transaction(amount, sender_id, recipient_id)
            
            conn.commit()
            conn.close()

            return jsonify({
                'result': True, 
                'message': f'Successfully transferred ${amount:.2f} to {recipient_username}', 
                'transaction_id': transaction_id
            })
        except jwt.InvalidTokenError:
            return jsonify({'error': 'Invalid token'}), 401
        except ValueError:
            return jsonify({'result': False, 'message': 'Invalid amount'}), 400

    @app.route('/check_transaction')
    def check_transaction():
        token = request.cookies.get('Authorization')
        if not token:
            return redirect('/login')
        try:
            jwt.decode(token, SECRET_KEY, algorithms=['HS256'])
        except jwt.InvalidTokenError:
            return redirect('/logout')
        return render_template('check_transaction.html')

    @app.route('/api/check_transactions', methods=['POST'])
    def api_check_transactions():
        token = request.cookies.get('Authorization')
        if not token:
            return jsonify({'error': 'Unauthorized'}), 401
        
        try:
            jwt.decode(token, SECRET_KEY, algorithms=['HS256'])
        except jwt.InvalidTokenError:
            return jsonify({'error': 'Invalid token'}), 401

        transactions_conn = sqlite3.connect(TRANSACTIONS_DB_PATH)
        users_conn = sqlite3.connect(USERS_DB_PATH)
        t_cursor = transactions_conn.cursor()
        u_cursor = users_conn.cursor()

        t_cursor.execute('SELECT id, amount, sender_id, receiver_id, created_at FROM transactions')
        transactions = t_cursor.fetchall()
        
        results = []
        
        for transaction in transactions:
            transaction_id, amount, sender_id, receiver_id, created_at = transaction
            errors = []

            u_cursor.execute('SELECT COUNT(*) FROM users WHERE id = ?', (sender_id,))
            if u_cursor.fetchone()[0] == 0:
                errors.append(f"Sender ID {sender_id} not found")

            u_cursor.execute('SELECT COUNT(*) FROM users WHERE id = ?', (receiver_id,))
            if u_cursor.fetchone()[0] == 0:
                errors.append(f"Receiver ID {receiver_id} not found")

            if amount <= 0:
                errors.append(f"Invalid amount: {amount}")

            if created_at < MIN_TIMESTAMP or created_at > MAX_TIMESTAMP:
                errors.append(f"Invalid timestamp: {created_at}")

            if errors:
                try:
                    u_cursor.execute('UPDATE users SET balance = balance + ? WHERE id = ?', (amount, sender_id))
                    u_cursor.execute('UPDATE users SET balance = balance - ? WHERE id = ?', (amount, receiver_id))
                    t_cursor.execute('DELETE FROM transactions WHERE id = ?', (transaction_id,))
                    results.append({
                        'transaction_id': transaction_id,
                        'errors': errors,
                        'status': 'Reversed and deleted'
                    })
                except sqlite3.Error as e:
                    results.append({
                        'transaction_id': transaction_id,
                        'errors': errors,
                        'status': f"Error reversing: {str(e)}"
                    })
        
        transactions_conn.commit()
        users_conn.commit()
        transactions_conn.close()
        users_conn.close()

        if not results:
            results.append({'transaction_id': None, 'errors': [], 'status': 'No invalid transactions found'})
        
        return jsonify({'results': results})