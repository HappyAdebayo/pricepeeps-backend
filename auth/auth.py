from flask import Blueprint, request, jsonify
from config import get_db_connection
from utils.utils import validate_email,generate_verification_code
from utils.email_sender import send_verification_email
import bcrypt
from datetime import datetime, timedelta,timezone

auth_bp = Blueprint('auth', __name__)

# SIGNUP

@auth_bp.route('/signup', methods=['POST'])

def signup():
    data = request.json
    email = data.get('email', '').strip()  
    password = data.get('password', '').strip()

    if not all([email, password]):
        return jsonify({'error': 'Missing fields'}), 400

    if not validate_email(email):
        return jsonify({'error': 'Invalid email format'}), 400

    hashed_password = bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt()).decode('utf-8')

    try:
        conn = get_db_connection()
        cur = conn.cursor()

        cur.execute("SELECT COUNT(*) FROM users WHERE email = %s", (email,))
        email_count = cur.fetchone()[0]
        
        if email_count > 0:
            return jsonify({'error': 'Email already registered'}), 400

        cur.execute(
            "INSERT INTO users (email, password, onboarding, is_verified) VALUES (%s, %s, %s, %s) RETURNING id",
            (email, hashed_password, False, False)
        )
        user_id = cur.fetchone()[0]

        cur.execute(
            "INSERT INTO settings (notification, user_id) VALUES (%s, %s)",
            (True, user_id)
        )

        verification_code = generate_verification_code()
        expiration_date = datetime.now(timezone.utc) + timedelta(minutes=15)

        cur.execute(
            "INSERT INTO verifications (user_id, verification_code, expiration_date) VALUES (%s, %s, %s)",
            (user_id, verification_code, expiration_date)
        )

        conn.commit()
        cur.close()
        conn.close()

        if not send_verification_email(email, verification_code):
            return jsonify({'error': 'User created, but failed to send verification email'}), 500

        return jsonify({'message': 'User registered successfully. Please check your email for the verification code.'}), 201
    except Exception as e:
        return jsonify({'error': str(e)}), 500
    


# LOGIN

@auth_bp.route('/login', methods=['POST'])
def login():
    data = request.json
    email = data.get('email', '').strip()
    password = data.get('password', '').strip()

    if not all([email, password]):
        return jsonify({'error': 'Missing fields'}), 400

    if not validate_email(email):
        return jsonify({'error': 'Invalid email format'}), 400

    try:
        conn = get_db_connection()
        cur = conn.cursor()

        cur.execute("SELECT id, password, is_verified,onboarding,email FROM users WHERE email = %s", (email,))
        user = cur.fetchone()

        if not user:
            return jsonify({'error': 'Invalid email or password'}), 401

        user_id, stored_password, is_verified, onboarding,user_email = user

        if not stored_password.startswith('$2b$') and not stored_password.startswith('$2a$'):
            return jsonify({'error': 'Invalid password hash format in DB'}), 500

        if not bcrypt.checkpw(password.encode('utf-8'), stored_password.encode('utf-8')):
            return jsonify({'error': 'Invalid email or password'}), 401

        if not is_verified:
            return jsonify({'message':'verification','error': 'User not verified. Please verify your email.', 'status': False}), 400

        if not onboarding:
            return jsonify({'message':'questionnaire','error': 'User has not completed onboarding. Please complete onboarding first.', 'status': False,'user_id': user_id}), 400


        print(f"Stored password hash from DB: {stored_password}")


        cur.close()
        conn.close()

        return jsonify({
            'message': 'Login successful!',
            'status': True,
            'user': {
                'id': user_id,
                'email': user_email,
                'is_verified': is_verified,
                'onboarding': onboarding
            }
        }), 200

    except Exception as e:
        print(f"Error during login: {str(e)}")
        return jsonify({'error': str(e)}), 500

# DELETE ACCOUNT
@auth_bp.route('/delete_account', methods=['POST'])
def delete_account_from_db():
    data = request.json
    user_id = data.get('id', '')

    try:
        conn = get_db_connection()
        cur = conn.cursor()

        cur.execute("DELETE FROM wishlists WHERE user_id = %s", (user_id,))
        cur.execute("DELETE FROM onboarding WHERE user_id = %s", (user_id,))
        cur.execute("DELETE FROM users WHERE id = %s", (user_id,))

        conn.commit()

        return jsonify({'message': 'Account deleted successfully'}), 201
    except Exception as e:
        print(f"Error deleting account: {str(e)}")
        return jsonify({'error': 'Failed to delete account'}), 500
    finally:
        cur.close()
        conn.close()