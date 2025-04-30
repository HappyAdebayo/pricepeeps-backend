from flask import Blueprint, request, jsonify
from config import get_db_connection

settings_bp = Blueprint('settings', __name__)

@settings_bp.route('/notifications', methods=['POST'])
def update_notifications():
    data = request.json
    user_id = data.get('user_id')
    notifications_enabled = data.get('notification') 
    print(notifications_enabled)
    notification_value = True if notifications_enabled else False

    if user_id is None or notifications_enabled is None:
        return jsonify({'error': 'Missing user_id or notification status'}), 400

    try:
        conn = get_db_connection()
        cur = conn.cursor()

        cur.execute(
            "UPDATE settings SET notification = %s WHERE user_id = %s",
            (notification_value, user_id)
        )

        conn.commit()
        cur.close()
        conn.close()

        return jsonify({'message': 'Notification setting updated successfully'}), 200

    except Exception as e:
        print(f"Error updating notification setting: {e}")
        return jsonify({'error': str(e)}), 500


# GETTING NOTIFICATIONS
@settings_bp.route('/notifications', methods=['GET'])

def get_notification():
    userId = request.args.get('id')

    if not userId:
       return jsonify({'error':'Missing user_id'}),400
    
    try:
        conn=get_db_connection()
        cur=conn.cursor()

        cur.execute("""
          SELECT notification FROM settings WHERE user_id = %s
        """,(userId,))

        notification_setting = cur.fetchone()

        if notification_setting is None:
            return jsonify({'error': 'Settings not found for this user'}), 404

        notification = notification_setting[0]


        return jsonify({
            'message': 'Notification fetched successfully!',
            'notification':notification
        }), 200

    
    except Exception as e:
        print(f"Error fetching notification setting: {str(e)}")
        return jsonify({'error': str({e})}), 500
    finally :
        cur.close()
        conn.close()