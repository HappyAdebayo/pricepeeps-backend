from flask import Blueprint, request, jsonify
from utils.email_sender import send_reset_email
from utils.utils import generate_reset_code
from config import get_db_connection
from datetime import datetime, timedelta, timezone
import bcrypt

password_reset_bp = Blueprint('password_reset', __name__)

@password_reset_bp.route('/passwordrequest', methods=['POST'])

def request_password_reset():
    data = request.json
    email = data.get('email', '').strip().lower()

    if not email:
        return jsonify({'error': 'Missing email'}), 400

    try:
        conn = get_db_connection()
        cur = conn.cursor()

        cur.execute("SELECT id FROM users WHERE email = %s", (email,))
        user = cur.fetchone()

        if not user:
            return jsonify({'error': 'Email not found'}), 404

        user_id = user[0]
        reset_code = generate_reset_code()
        expiration_date = datetime.now(timezone.utc) + timedelta(hours=1)

        # FIXED QUERY
        cur.execute(
            "SELECT id FROM password_resets WHERE user_id = %s AND expired = FALSE AND expires_at > NOW()",
            (user_id,)
        )
        existing_reset = cur.fetchone()

        if existing_reset:
            cur.execute(
                "UPDATE password_resets SET verification_code = %s, expires_at = %s WHERE id = %s",
                (reset_code, expiration_date, existing_reset[0])
            )
        else:
            cur.execute(
                "INSERT INTO password_resets (user_id, verification_code, expired, expires_at) VALUES (%s, %s, %s, %s)",
                (user_id, reset_code, False, expiration_date)
            )

        conn.commit()

        if send_reset_email(email, reset_code):
            return jsonify({'message': 'Password reset email sent.'}), 201
        else:
            conn.rollback()
            return jsonify({'error': 'Failed to send reset email'}), 500

    except Exception as e:
        print(f"Error during password reset request: {str(e)}")
        return jsonify({'error': str(e)}), 500

    finally:
        cur.close()
        conn.close()



# Reset password route
@password_reset_bp.route('/passwordreset', methods=['POST'])
def reset_password():
    data = request.json
    reset_code = data.get('reset_code', '').strip()
    new_password = data.get('new_password', '').strip()
    email = data.get('email', '').strip()

    if not all([email, reset_code, new_password]):
      return jsonify({'error': 'Missing fields'}), 400

    try:
        conn = get_db_connection()
        cur = conn.cursor()

        cur.execute("""
        SELECT pr.user_id, pr.expired, pr.created_at
        FROM password_resets pr
        JOIN users u ON pr.user_id = u.id
        WHERE pr.verification_code = %s AND u.email = %s
        """, (reset_code, email))

        reset_record = cur.fetchone()

        if not reset_record:
            return jsonify({'error': 'Invalid reset code or email'}), 400

        user_id, expired,created_at = reset_record

        if expired:
            return jsonify({'error': 'Reset code expired'}), 400

        if datetime.now(timezone.utc) - created_at > timedelta(hours=1):
            return jsonify({'error': 'Reset code has expired'}), 400

        hashed_password = bcrypt.hashpw(new_password.encode('utf-8'), bcrypt.gensalt()).decode('utf-8')
        
        cur.execute("UPDATE users SET password = %s WHERE id = %s", (hashed_password, user_id))

        cur.execute("UPDATE password_resets SET expired = %s WHERE verification_code = %s", (True, reset_code))

        cur.execute("DELETE FROM password_resets WHERE verification_code = %s", (reset_code,))

        conn.commit()

        return jsonify({'message': 'Password reset successfully'}), 201

    except Exception as e:
        print(f"Error during password reset: {str(e)}")
        return jsonify({'error': str(e)}), 500
    finally:
        cur.close()
        conn.close()
