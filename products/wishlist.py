from flask import Blueprint, request, jsonify
from config import get_db_connection

wishlist_bp=Blueprint('wishlist', __name__)

@wishlist_bp.route('/wishlist', methods=['POST'])

def add_to_wishlist():
    data = request.json
    user_id = data.get('user_id')
    product_name= data.get('product_name', '').strip()
    product_link= data.get('product_link', '').strip()
    product_price= data.get('product_price', '').strip()
    product_image_link= data.get('product_image_link', '').strip()

    if not all([user_id,product_name, product_image_link, product_price, product_link]):
        return jsonify({'error': 'mising fields'}), 400
    
    try:
        conn=get_db_connection()
        cur= conn.cursor()
        cur.execute("""
            SELECT 1 FROM wishlists
            WHERE user_id = %s
            AND product_name = %s
            AND product_link = %s
            AND product_price = %s
            AND product_image_link = %s
            LIMIT 1
        """, (user_id,product_name, product_link, product_price, product_image_link))
        
        existing = cur.fetchone()

        if existing:
            return jsonify({'error': 'Product already in wishlist'}), 409
        
        cur.execute("""
           INSERT INTO wishlists (user_id,product_name, product_link, product_price, product_image_link)
           VALUES (%s,%s,%s,%s,%s)
        """, (user_id,product_name, product_link, product_price, product_image_link))

        conn.commit()

        return jsonify({'message':'Product added to wishlist successfully'}), 201

    except Exception as e:
        print(f"Error adding to wishlist {str(e)}")
        return jsonify({'error': str({e})}), 500
    finally:
        cur.close()
        conn.close()


# REMOVE PRODUCT FROM WISHLIST
@wishlist_bp.route('/wishlist/remove', methods=['POST'])

def remove_from_wishlist():
    data = request.json
    wishlist_id = data.get('id')

    if not wishlist_id:
        return jsonify({'error': 'Wishlist ID is required'}), 400

    try:
        conn = get_db_connection()
        cur = conn.cursor()

        cur.execute("DELETE FROM wishlists WHERE id = %s", (wishlist_id,))
        conn.commit()

        if cur.rowcount == 0:
            return jsonify({'error': 'Wishlist item not found'}), 404

        return jsonify({'message': 'Product removed from wishlist successfully'}), 200

    except Exception as e:
        print(f"Error removing from wishlist: {str(e)}")
        return jsonify({'error': str(e)}), 500
    finally:
        cur.close()
        conn.close()