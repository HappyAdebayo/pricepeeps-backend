from flask import Blueprint, request, jsonify
from config import get_db_connection

onboarding_bp = Blueprint('onboarding', __name__)

@onboarding_bp.route('/onboarding', methods=['POST'])

def submit_onboarding():
    data = request.json
    user_id = data.get('user_id')
    reason = data.get('reason_for_using', '').strip()
    how_heard = data.get('how_heard_about', '').strip()

    if not all([user_id, reason, how_heard]):
        return jsonify({'error': 'Missing fields'}), 400

    try:
        conn = get_db_connection()
        cur = conn.cursor()

        cur.execute("""
            INSERT INTO onboarding (user_id, reason_for_using, how_heard_about)
            VALUES (%s, %s, %s)
        """, (user_id, reason, how_heard))

        cur.execute("""
            UPDATE users SET onboarding = TRUE WHERE id = %s
        """, (user_id,))

        cur.execute("""
            SELECT id, email, is_verified, onboarding
            FROM users WHERE id = %s
        """, (user_id,))

        user = cur.fetchone()

        conn.commit()
        cur.close()
        conn.close()

        if not user:
            return jsonify({'error': 'User not found'}), 404

        user_id, email, is_verified, onboarding = user

        return jsonify({
            'message': 'Onboarding completed successfully',
            'status': True,
            'user': {
                'id': user_id,
                'email': email,
                'is_verified': is_verified,
                'onboarding': onboarding
            }
        }), 201

    except Exception as e:
        print(f"Onboarding error: {str(e)}")
        return jsonify({'error': 'Server error'}), 500
