from flask import Flask
from auth.auth import auth_bp
from auth.verification import verification_bp
from auth.onboarding import onboarding_bp
from auth.password_reset import password_reset_bp
from products.wishlist import wishlist_bp
from settings.setting import settings_bp
from notifications.device_token_saver import notification_bp

app = Flask(__name__)

# AUTH
app.register_blueprint(auth_bp, url_prefix='/auth')  
app.register_blueprint(verification_bp, url_prefix='/auth/verification')
app.register_blueprint(password_reset_bp, url_prefix='/auth/password')
app.register_blueprint(onboarding_bp)  


#PRODUCT
app.register_blueprint(wishlist_bp, url_prefix='/product')

# SETTING
app.register_blueprint(settings_bp, url_prefix='/setting')

# PUSH NOTIFICATION
app.register_blueprint(notification_bp)  
# app.register_blueprint(push_notification_bp)


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)