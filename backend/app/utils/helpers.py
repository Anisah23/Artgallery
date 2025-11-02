from flask_sqlalchemy import pagination

def paginate_query(query, page: int = 1, per_page: int = 20):
    page = max(1, int(page))
    per_page = max(1, int(per_page))
    pagination = query.paginate(page=page, per_page=per_page, error_out=False)
    return pagination

def validate_email(email: str) -> bool:
    import re
    pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
    return re.match(pattern, email) is not None

def validate_password(password: str) -> bool:
    if len(password) < 8:
        return False
    if not any(c.isupper() for c in password):
        return False
    if not any(c.islower() for c in password):
        return False
    if not any(c.isdigit() for c in password):
        return False
    return True