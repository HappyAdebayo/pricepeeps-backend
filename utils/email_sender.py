import smtplib

import os
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from dotenv import load_dotenv

load_dotenv()


def send_verification_email(to_email, code):
    try:
        email_user = os.getenv("EMAIL_HOST_USER")
        email_password = os.getenv("EMAIL_HOST_PASSWORD")
        email_host = os.getenv("EMAIL_HOST")
        email_port = int(os.getenv("EMAIL_PORT"))

        msg = MIMEMultipart()
        msg['From'] = email_user
        msg['To'] = to_email
        msg['Subject'] = 'Your Pricepeeps Verification Code'

        body = f"""
        <html>
        <body style="font-family: Arial, sans-serif; background-color: #f8f8f8; padding: 20px;">
            <div style="max-width: 500px; margin: auto; background-color: white; padding: 30px; border-radius: 8px; box-shadow: 0 2px 8px rgba(0,0,0,0.1);">
            <h2 style="color: #DB3022;">Welcome to PricePeeps!</h2>
            <p style="font-size: 16px;">Thanks for signing up! Use the verification code below to complete your registration:</p>
            <div style="text-align: center; margin: 30px 0;">
                <span style="display: inline-block; font-size: 24px; background-color: #DB3022; color: white; padding: 12px 24px; border-radius: 6px; letter-spacing: 2px;">
                {code}
                </span>
            </div>
            <p style="font-size: 14px; color: #888;">If you didn’t sign up for PricePeeps, you can ignore this email.</p>
            </div>
        </body>
        </html>
        """
        msg.attach(MIMEText(body, 'html'))

        server = smtplib.SMTP(email_host, email_port)
        server.starttls()
        server.login(email_user, email_password)
        server.send_message(msg)
        server.quit()
        return True
    except Exception as e:
        print(f"Error sending email: {e}")
        return False

# RESET CODE FOR PASSWORD
def send_reset_email(user_email, reset_code):
    """Send the password reset email to the user."""

    subject = "Password Reset Request"
    body = f"""
    <html>
    <head>
        <style>
            body {{
                font-family: Arial, sans-serif;
                margin: 0;
                padding: 0;
                background-color: #f4f4f4;
            }}
            .email-container {{
                width: 100%;
                max-width: 600px;
                margin: 0 auto;
                background-color: #ffffff;
                border-radius: 8px;
                padding: 20px;
                box-shadow: 0 4px 8px rgba(0, 0, 0, 0.1);
            }}
            .email-header {{
                text-align: center;
                color: #DB3022;
            }}
            .email-content {{
                margin-top: 20px;
                font-size: 16px;
                color: #333333;
            }}
            .email-footer {{
                margin-top: 30px;
                font-size: 12px;
                color: #999999;
                text-align: center;
            }}
            .reset-code {{
                display: inline-block;
                padding: 10px 20px;
                font-size: 18px;
                background-color: #DB3022;
                color: #ffffff;
                border-radius: 5px;
                margin-top: 10px;
                font-weight: bold;
            }}
            .footer-link {{
                color: #DB3022;
                text-decoration: none;
            }}
        </style>
    </head>
    <body>
        <div class="email-container">
            <div class="email-header">
                <h2>Password Reset Request</h2>
            </div>
            <div class="email-content">
                <p>Hi,</p>
                <p>You requested a password reset. Please use the following code to reset your password:</p>
                <p class="reset-code">{reset_code}</p>
                <p>If you did not request this, please ignore this email.</p>
                <p>This code will expire in 15 minutes.</p>
            </div>
            <div class="email-footer">
                <p>If you have any questions, please contact us at <a href="mailto:support@example.com" class="footer-link">support@example.com</a>.</p>
                <p>&copy; 2025 Your Company. All rights reserved.</p>
            </div>
        </div>
    </body>
    </html>
    """

    email_user = os.getenv("EMAIL_HOST_USER")
    email_password = os.getenv("EMAIL_HOST_PASSWORD")
    email_host = os.getenv("EMAIL_HOST")
    email_port = int(os.getenv("EMAIL_PORT"))

    msg = MIMEMultipart()
    msg['From'] = email_user
    msg['To'] = user_email
    msg['Subject'] = subject
    msg.attach(MIMEText(body, 'html'))

    try:
        with smtplib.SMTP(email_host, email_port) as server:
            server.starttls()
            server.login(email_user, email_password)
            text = msg.as_string()
            server.sendmail(email_user, user_email, text)
            print("Password reset email sent successfully.")
            return True

    except Exception as e:
        print(f"Failed to send email: {str(e)}")
        return False