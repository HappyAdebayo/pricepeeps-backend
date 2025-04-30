from flask import Blueprint, request, jsonify
from config import get_db_connection
from utils.utils import validate_email,generate_verification_code
from utils.email_sender import send_verification_email
from datetime import datetime, timezone,timedelta

verification_bp = Blueprint('verification', __name__)

@verification_bp.route('/verify', methods=['POST'])

def verify_code():
    data = request.json
    email = data.get('email', '').strip()
    input_code = data.get('verification_code', '').strip()

    if not all([email, input_code]):
        return jsonify({'error': 'Missing fields'}), 400

    if not validate_email(email):
        return jsonify({'error': 'Invalid email format'}), 400

    try:
        conn = get_db_connection()
        cur = conn.cursor()

        cur.execute("SELECT id FROM users WHERE email = %s", (email,))
        user = cur.fetchone()
        if not user:
            return jsonify({'error': 'User not found'}), 404

        user_id = user[0]

        cur.execute(
            "SELECT verification_code, expiration_date FROM verifications WHERE user_id = %s ORDER BY created_at DESC LIMIT 1",
            (user_id,)
        )
        verification = cur.fetchone()

        if not verification:
            return jsonify({'error': 'Verification code not found'}), 404

        stored_code, expiration_date = verification

        if datetime.now(timezone.utc) > expiration_date:
           return jsonify({'error': 'Verification code has expired'}), 400

        if input_code != stored_code:
            return jsonify({'error': 'Invalid verification code'}), 400

        cur.execute("UPDATE users SET is_verified = TRUE WHERE id = %s", (user_id,))
        
        cur.execute("DELETE FROM verifications WHERE user_id = %s", (user_id,))

        conn.commit()

        cur.close()
        conn.close()

        return jsonify({'message': 'Verification successful!'}), 201

    except Exception as e:
        return jsonify({'error': str(e)}), 500



@verification_bp.route('/resend_verification_code', methods=['POST'])

def resend_verification_code():
    data = request.json
    email = data.get('email', '').strip()

    if not email:
        return jsonify({'error': 'Email is required'}), 400

    if not validate_email(email):
        return jsonify({'error': 'Invalid email format'}), 400

    try:
        conn = get_db_connection()
        cur = conn.cursor()

        cur.execute("SELECT id, is_verified FROM users WHERE email = %s", (email,))
        user = cur.fetchone()

        if not user:
            return jsonify({'error': 'User not found'}), 404

        user_id, is_verified = user

        if is_verified:
            return jsonify({'message': 'User is already verified'}), 400

        new_verification_code = generate_verification_code()
        new_expiration_date = datetime.now(timezone.utc) + timedelta(minutes=15)

        cur.execute(
            """
            UPDATE verifications
            SET verification_code = %s, expiration_date = %s
            WHERE user_id = %s
            """,
            (new_verification_code, new_expiration_date, user_id)
        )


        conn.commit()
        cur.close()
        conn.close()

        if not send_verification_email(email, new_verification_code):
            return jsonify({'error': 'Failed to send verification email'}), 500

        return jsonify({'message': 'A new verification code has been sent to your email.'}), 201

    except Exception as e:
        return jsonify({'error': str(e)}), 500