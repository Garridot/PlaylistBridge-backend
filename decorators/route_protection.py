from flask import request, jsonify
from functools import wraps
import jwt
from models.users import User


from config import Config
SECRET_KEY = Config.SECRET_KEY

def token_required(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        token = request.headers.get('x-access-token')        
        if not token:
            return jsonify({'message': 'Token is missing.'}), 403

        try:
            data = jwt.decode(token, SECRET_KEY, algorithms=['HS256'])            
            current_user = User.query.filter_by(id=data['user_id']).first()
        except ExpiredSignatureError:
            return jsonify({'message': 'Token expired. Please refresh your token.'}), 401
        except InvalidTokenError:
            return jsonify({'message': 'Invalid token.'}), 403

        return f(current_user, *args, **kwargs)
    return decorated
