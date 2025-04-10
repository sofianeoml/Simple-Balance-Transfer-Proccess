import hashlib
import sqlite3
from flask import Blueprint, request, jsonify, make_response
from dbs.users import DB_PATH
import jwt

login_bp = Blueprint('login', __name__)
SECRET_KEY = '1XSEC'

@login_bp.route('/login', methods=['POST'])
def login():
    data = request.get_json()
    username = data.get('username')
    password = data.get('password')

    if not all([username, password]):
        return jsonify({'result': False, 'message': 'Username and password are required'}), 400

    hashed_password = hashlib.md5(password.encode()).hexdigest()

    try:
        conn = sqlite3.connect(DB_PATH)
        c = conn.cursor()
        c.execute('SELECT id, username, email, created_at, balance FROM users WHERE username = ? AND password = ?', 
                  (username, hashed_password))
        user = c.fetchone()
        conn.close()

        if user:
            user_id, username, email, created_at, balance = user
            token = jwt.encode({'user_id': user_id}, SECRET_KEY, algorithm='HS256')
            response = make_response(jsonify({'result': True, 'message': f'Welcome back, {username}!'}))
            response.set_cookie('Authorization', token, httponly=True, secure=False)
            return response
        else:
            return jsonify({'result': False, 'message': 'Invalid username or password'}), 401
    except Exception as e:
        return jsonify({'result': False, 'message': f'Error: {str(e)}'}), 500