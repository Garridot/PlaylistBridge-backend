import jwt
from datetime import datetime, timedelta
from config import Config  # Asegúrate de tener tus claves secretas en config.py

# Secretos para firmar los tokens
JWT_SECRET = Config.SECRET_KEY
JWT_ALGORITHM = 'HS256'

def generate_access_token(user_id):
    payload = {
        'user_id': user_id,
        'exp': datetime.utcnow() + timedelta(minutes=30),  # Duración de Access Token (30 mins)
        'iat': datetime.utcnow()
    }
    return jwt.encode(payload, JWT_SECRET, algorithm=JWT_ALGORITHM)

def generate_refresh_token(user_id):
    payload = {
        'user_id': user_id,
        'exp': datetime.utcnow() + timedelta(days=30),  # Duración de Refresh Token (30 días)
        'iat': datetime.utcnow()
    }
    return jwt.encode(payload, JWT_SECRET, algorithm=JWT_ALGORITHM)
