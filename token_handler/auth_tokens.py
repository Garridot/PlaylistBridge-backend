import jwt
from datetime import datetime, timedelta
from config import Config  # Ensure your secret keys are in config.py
from flask import jsonify
from database.redis_connection import get_redis_connection

# Token signing secrets
JWT_SECRET = Config.SECRET_KEY
JWT_ALGORITHM = 'HS256'
REFRESH_TOKEN_EXPIRATION = 30 # days

redis = get_redis_connection()

def generate_access_token(user_id):
    """
    Creates a short-lived access token that expires after 30 minutes.

    Parameters: 
        user_id (int) – The unique ID of the user.
    Returns:
        Encoded JWT access token (str).
    """
    payload = {
        'user_id': user_id,
        'exp': datetime.utcnow() + timedelta(minutes=30),  # access token duration (30 mins).
        'iat': datetime.utcnow()
    }
    return jwt.encode(payload, JWT_SECRET, algorithm=JWT_ALGORITHM)

def generate_refresh_token(user_id):
    """
    Creates a long-lived refresh token with a 30-day expiration.

    Parameters: 
        user_id (int) – The unique ID of the user.
    Returns:
        Encoded JWT access token (str).
    """
    payload = {
        'user_id': user_id,
        'exp': datetime.utcnow() + timedelta(days=REFRESH_TOKEN_EXPIRATION),  # refresh token expires in 30 days.
        'iat': datetime.utcnow()
    }

    refresh_token = jwt.encode(payload, JWT_SECRET, algorithm=JWT_ALGORITHM)
    
    # save the refresh token in redis (we use 'user_id' as key).
    save_refresh_token_in_redis(user_id, refresh_token)
    
    return refresh_token

def save_refresh_token_in_redis(user_id, refresh_token):  
    """
    Saves the refresh token to Redis for secure storage and associates it with the user ID.

    Parameters: 
        user_id (int) – The unique ID of the user.
        refresh_token (str) – The JWT refresh token to store.

    Exceptions: 
        Catches Redis errors to prevent failures in token saving.
    """  
    try:
        # configure the expiration time in Redis (in seconds).
        refresh_token_expires_in_seconds = REFRESH_TOKEN_EXPIRATION * 24 * 60 * 60        
        # save fresh token in redis with 'user_id' as key.
        redis.setex(f"refresh_token:{user_id}", refresh_token_expires_in_seconds, refresh_token)
    except RedisError as e:
        print(f"Error saving refresh token to Redis: {e}")


def get_refresh_token_from_redis(user_id):  
    """
    Retrieves the stored refresh token from Redis.

    Parameters: 
        user_id (int) – The unique ID of the user.
    Returns:
        Stored refresh token (str) or None if not found.
    """
    try:
        return redis.get(f"refresh_token:{user_id}") 
    except RedisError as e:
        print(f"Error getting refresh token to Redis: {e}")   

def refresh_access_token(refresh_token):
    """
    Verifies the refresh token and generates a new access token.

    Parameters: 
        user_id (int) – The unique ID of the user.
    Returns:
        JSON with a new access token if valid, or an error message if invalid or expired.
    """
    if not refresh_token:
        return jsonify({'message': 'Refresh token is missing!'}), 403
        
    try:
        # decode and validate the refresh token.
        decoded_token = jwt.decode(refresh_token, JWT_SECRET, algorithms=[JWT_ALGORITHM])
        user_id = decoded_token['user_id']

        stored_token = get_refresh_token_from_redis(decoded_token['user_id'])
        
        # check if the refresh token exists in redis.
        if stored_token != refresh_token:      
            return jsonify({'message': 'Token is invalid.'})

        # generate a new access token
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
    """
    Deletes the refresh token associated with the user ID in Redis, effectively revoking it.

    Parameters: 
        user_id (int) – The unique ID of the user.
    Exceptions: 
        Catches Redis errors to handle token revocation failures.
    """
    # remove refresh token from redis.    
    try:
        redis.delete(f"refresh_token:{user_id}")
    except RedisError as e:
        print(f"Error removin refresh token to Redis: {e}")   