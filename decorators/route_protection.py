from functools import wraps
from flask import request, jsonify
from config import Config
from models.users import User 
import jwt
from jwt.exceptions import ExpiredSignatureError, InvalidTokenError

SECRET_KEY = Config.SECRET_KEY

def token_required(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        token = request.headers.get('x-access-token')
        
        if not token:
            return jsonify({'message': 'Token is missing.'}), 403

        try:
            # Decodificar el token JWT
            data = jwt.decode(token, SECRET_KEY, algorithms=['HS256'])
            
            # Buscar el usuario basado en el user_id del token
            current_user = User.query.filter_by(id=data['user_id']).first()

            # Verificar si el usuario existe
            if current_user is None:
                return jsonify({'message': 'User not found.'}), 404

        # Manejar casos específicos de errores de JWT
        except ExpiredSignatureError:
            return jsonify({'message': 'Token expired. Please refresh your token.'}), 401
        except InvalidTokenError:
            return jsonify({'message': 'Invalid token.'}), 403
        except Exception as e:
            return jsonify({'message': 'Token is invalid or corrupted.', 'error': str(e)}), 403

        # Continuar con la ejecución de la función si el token es válido
        return f(current_user, *args, **kwargs)

    return decorated
