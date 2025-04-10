import random
import hashlib
import time
import sqlite3
from flask import Blueprint, request, jsonify, make_response
from dbs.users import DB_PATH
import jwt

signup_bp = Blueprint('signup', __name__)
SECRET_KEY = '1XSEC'

def generate_unique_id():
    while True:
        new_id = random.randint(10000000, 99999999)
        conn = sqlite3.connect(DB_PATH)
        c = conn.cursor()
        c.execute('SELECT id FROM users WHERE id = ?', (new_id,))
        if not c.fetchone():
            conn.close()
            return new_id
        conn.close()

@signup_bp.route('/signup', methods=['POST'])
def signup():
    data = request.get_json()
    username = data.get('username')
    email = data.get('email')
    password = data.get('password')

    if not all([username, email, password]):
        return jsonify({'result': False, 'message': 'All fields are required'}), 400

    hashed_password = hashlib.md5(password.encode()).hexdigest()
    user_id = generate_unique_id()
    created_at = int(time.time() * 1000)

    try:
        conn = sqlite3.connect(DB_PATH)
        c = conn.cursor()
        c.execute('INSERT INTO users (id, username, email, password, created_at, balance) VALUES (?, ?, ?, ?, ?, ?)',
                  (user_id, username, email, hashed_password, created_at, 0.0))
        conn.commit()
        conn.close()

        token = jwt.encode({'user_id': user_id}, SECRET_KEY, algorithm='HS256')
        response = make_response(jsonify({'result': True, 'message': f'Welcome aboard, {username}! Your ID is {user_id}'}))
        response.set_cookie('Authorization', token, httponly=True, secure=False)
        return response
    except sqlite3.IntegrityError as e:
        conn.close()
        if 'username' in str(e):
            return jsonify({'result': False, 'message': 'Username already taken'}), 400
        elif 'email' in str(e):
            return jsonify({'result': False, 'message': 'Email already taken'}), 400
        return jsonify({'result': False, 'message': 'Database error'}), 500
    except Exception as e:
        return jsonify({'result': False, 'message': f'Error: {str(e)}'}), 500