from functools import wraps
from flask_jwt_extended import get_jwt_claims, verify_jwt_in_request
from flask import jsonify


def check_permissions(*permissions):
    def decorator(fn):
        @wraps(fn)
        def wrapper(*args, **kwargs):
            verify_jwt_in_request()
            claims = get_jwt_claims()
            user_permissions = claims["permissions"]
            if "full_admin" in user_permissions or len(list(set(user_permissions) & set(permissions))) > 0:
                return fn(*args, **kwargs)
            else:
                return jsonify(
                    msg='User is not authorized to access this endpoint'), 401
        return wrapper
    return decorator
