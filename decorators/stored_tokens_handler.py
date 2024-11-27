from functools import wraps
from flask import jsonify
from errors.custom_exceptions import NoRefreshTokenError, InvalidTokenError

def stored_tokens_handler_errors(func):
    """
    Decorator to handle errors related to stored tokens when refreshing or accessing tokens.

    This decorator catches specific custom exceptions related to token handling, such as 
    missing refresh tokens or invalid tokens. It returns a JSON response with an error 
    message and the appropriate status code. Any other unexpected errors will return a 
    generic error message and a 500 status code.

    Parameters:
    ----------
    func : function
        The function to be wrapped by this decorator.

    Returns:
    -------
    function : 
        The wrapped function with error handling for token-related operations.

    JSON Responses:
    ---------------
    Custom : {"error": e.message}
        Returns a JSON error message and status code as defined by the raised exceptions.
    500 : {"error": "An unexpected error occurred"}
        For any unexpected errors.

    Exceptions Handled:
    -------------------
    NoRefreshTokenError : Raised when no refresh token is available.
    InvalidTokenError : Raised when a token is malformed or invalid.

    Usage:
    ------
    @stored_tokens_handler_errors
    def some_token_related_function():
        # Code for the function
    """
    @wraps(func)
    def wrapper(*args, **kwargs):
        try:
            return func(*args, **kwargs)
        except NoRefreshTokenError as e:
            return jsonify({"error": e.message}), e.status_code
        except InvalidTokenError as e:
            return jsonify({"error": e.message}), e.status_code
        except Exception as e:
            return jsonify({"error": f"An unexpected error occurred: {e}"}), 500
    return wrapper

