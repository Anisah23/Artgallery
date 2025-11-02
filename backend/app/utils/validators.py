import re
from marshmallow import ValidationError

def validate_email(email):
    """Validate email format"""
    pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
    return bool(re.match(pattern, email))

def validate_password(password):
    """Validate password strength"""
    if len(password) < 8:
        return False
    if not any(c.isupper() for c in password):
        return False
    if not any(c.islower() for c in password):
        return False
    if not any(c.isdigit() for c in password):
        return False
    return True

def validate_price(price):
    """Validate price is positive"""
    if price <= 0:
        raise ValidationError('Price must be greater than 0')

def validate_category(category):
    """Validate artwork category"""
    valid_categories = ['painting', 'sculpture', 'photography', 'digital', 'mixed-media', 'textile']
    if category.lower() not in valid_categories:
        raise ValidationError(f'Category must be one of: {", ".join(valid_categories)}')