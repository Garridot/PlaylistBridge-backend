from functools import wraps
from flask import request, jsonify
from config import Config
from models.users import User 
import jwt
from jwt.exceptions import ExpiredSignatureError, InvalidTokenError

SECRET_KEY = Config.SECRET_KEY

def token_required(f):
    """
    Decorator to protect routes by requiring a valid JWT token in the request header.

    This decorator checks for the presence and validity of a JWT token in the request headers.
    If the token is valid, it allows the request to proceed with the authenticated user. 
    If invalid or missing, it returns an appropriate JSON response with an error message.

    Parameters:
    ----------
    f : function
        The function to be wrapped by this decorator.

    Returns:
    -------
    function : 
        The wrapped function if the token is valid; otherwise, returns a JSON error response.

    JSON Responses:
    ---------------
    403 : {'message': 'Token is missing.'}
        If no token is provided in the request headers.
    404 : {'message': 'User not found.'}
        If the token is valid but no user is found with the ID in the token.
    401 : {'message': 'Token expired. Please refresh your token.'}
        If the token has expired.
    403 : {'message': 'Invalid token.'}
        If the token is malformed or invalid.
    403 : {'message': 'Token is invalid or corrupted.'}
        For any other unexpected errors with the token.

    Usage:
    ------
    @token_required
    def protected_route(current_user):
        # Code for the protected route
    """
    @wraps(f)
    def decorated(*args, **kwargs):
        token = request.headers.get('x-access-token')
        
        if not token:
            return jsonify({'message': 'Token is missing.'}), 403

        try:
            # Decode the JWT token.
            data = jwt.decode(token, SECRET_KEY, algorithms=['HS256'])
            
            # Search for the user based on the user_id in the token.
            current_user = User.query.filter_by(id=data['user_id']).first()

            # Check if the user exists.
            if current_user is None:
                return jsonify({'message': 'User not found.'}), 404

        except ExpiredSignatureError:
            return jsonify({'message': 'Token expired. Please refresh your token.'}), 401
        except InvalidTokenError:
            return jsonify({'message': 'Invalid token.'}), 403
        except Exception as e:
            return jsonify({'message': 'Token is invalid or corrupted.', 'error': str(e)}), 403

        # Continue executing the function if the token is valid.
        return f(current_user, *args, **kwargs)

    return decorated

