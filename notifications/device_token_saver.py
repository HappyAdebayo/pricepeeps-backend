import logging
from flask import Blueprint, request, jsonify
from config import get_db_connection

notification_bp = Blueprint('notify', __name__)

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

@notification_bp.route('/save-device-token', methods=['POST'])
def save_device_token():
    data = request.get_json()
    device_token = data.get('token')
    print('Request data received:', data) 

    if not device_token:
        return jsonify({'message': 'Invalid data: token missing'}), 400

    conn = None
    cur = None

    try:
        conn = get_db_connection()
        cur = conn.cursor()

        cur.execute("SELECT 1 FROM device_tokens WHERE device_token = %s;", (device_token,))
        existing_token = cur.fetchone()

        if existing_token:
            logger.info(f"Token already exists: {device_token}")
            return jsonify({'message': 'Token already exists', 'token': device_token}), 200

        cur.execute(
            """
            INSERT INTO device_tokens (device_token) 
            VALUES (%s)
            ON CONFLICT (device_token) DO NOTHING;
            """,
            (device_token,)
        )
        conn.commit()

        logger.info(f"Token saved successfully: {device_token}")
        return jsonify({'message': 'Token saved successfully', 'token': device_token}), 201

    except Exception as e:
        logger.error(f"Error saving device token: {str(e)}")
        return jsonify({'message': 'Server error', 'error': str(e)}), 500

    finally:
        if cur:
            cur.close()
        if conn:
            conn.close()
