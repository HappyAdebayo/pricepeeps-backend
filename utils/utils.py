import re
import random

def validate_email(email):
    email_regex = r'^[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+$'
    return re.match(email_regex, email)


def generate_verification_code():
    return str(random.randint(100000, 999999))

def generate_reset_code():
    return str(random.randint(100000, 999999))
