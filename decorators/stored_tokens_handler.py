from functools import wraps
from flask import jsonify
from errors.custom_exceptions import NoRefreshTokenError, InvalidTokenError

def stored_tokens_handler_errors(func):
    @wraps(func)
    def wrapper(*args, **kwargs):
        try:
            return func(*args, **kwargs)
        except NoRefreshTokenError as e:
            return jsonify({"error": e.message}), e.status_code
        except InvalidTokenError as e:
            return jsonify({"error": e.message}), e.status_code
        except Exception as e:
            return jsonify({"error": "An unexpected error occurred"}), 500
    return wrapper
