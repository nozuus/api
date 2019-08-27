from functools import wraps

from flask import jsonify
import core.services.config_service as config_service


def check_permissions(*permissions):
    def decorator(fn):
        @wraps(fn)
        def wrapper(*args, **kwargs):
            if config_service.check_permissions(permissions):
                return fn(*args, **kwargs)
            else:
                return jsonify(
                    msg='User is not authorized to access this endpoint'), 401
        return wrapper
    return decorator
