import jwt
from datetime import datetime, timedelta
from config import Config  # Asegúrate de tener tus claves secretas en config.py
from flask import jsonify
from database.redis_connection import get_redis_connection

# Secretos para firmar los tokens
JWT_SECRET = Config.SECRET_KEY
JWT_ALGORITHM = 'HS256'
REFRESH_TOKEN_EXPIRATION = 30 # en dias

redis = get_redis_connection()

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
        'exp': datetime.utcnow() + timedelta(days=REFRESH_TOKEN_EXPIRATION),  # Refresh Token expira en 30 días
        'iat': datetime.utcnow()
    }

    refresh_token = jwt.encode(payload, JWT_SECRET, algorithm=JWT_ALGORITHM)
    
    # Guardar el Refresh Token en Redis (usamos 'user_id' como clave)
    save_refresh_token_in_redis(user_id, refresh_token)
    
    return refresh_token

def save_refresh_token_in_redis(user_id, refresh_token):    
    try:
        # Configuramos el tiempo de expiración en Redis (en segundos)
        refresh_token_expires_in_seconds = REFRESH_TOKEN_EXPIRATION * 24 * 60 * 60        
        # Guardamos el Refresh Token en Redis con el 'user_id' como clave
        redis.setex(f"refresh_token:{user_id}", refresh_token_expires_in_seconds, refresh_token)
    except RedisError as e:
        print(f"Error saving refresh token to Redis: {e}")


# Obtener Refresh Token desde Redis
def get_refresh_token_from_redis(user_id):  
    try:
        return redis.get(f"refresh_token:{user_id}") 
    except RedisError as e:
        print(f"Error getting refresh token to Redis: {e}")   

def refresh_access_token(refresh_token):
    if not refresh_token:
        return jsonify({'message': 'Refresh token is missing!'}), 403
        
    try:
        # Decodificar y validar el refresh token
        decoded_token = jwt.decode(refresh_token, JWT_SECRET, algorithms=[JWT_ALGORITHM])
        user_id = decoded_token['user_id']

        stored_token = get_refresh_token_from_redis(decoded_token['user_id'])
        
        # Verificar si el Refresh Token existe en Redis
        if stored_token != refresh_token:      
            return jsonify({'message': 'Token is invalid.'})

        # Generar un nuevo access token
        new_access_token = generate_access_token(user_id)

        return jsonify({
            'access_token': new_access_token,
            'refresh_token': refresh_token
            }), 200
    
    except jwt.ExpiredSignatureError:
        return jsonify({'message': 'Refresh token has expired!'}), 403
    except Exception as e:
        return jsonify({'message': 'Token is invalid.', 'error': str(e)}), 403


def revoke_refresh_token(user_id):
    # Eliminar el Refresh Token de Redis        
    try:
        redis.delete(f"refresh_token:{user_id}")
    except RedisError as e:
        print(f"Error removin refresh token to Redis: {e}")   