from models.users import User  # Suponiendo que tienes un modelo User
from auth.token_manager import generate_access_token, generate_refresh_token
from connection.google_connection import GoogleAuth
from database.db_connection import db


def google_auth_user(user_info):    
    
    # Verificar si el usuario ya existe en la base de datos
    user = User.query.filter_by(email=user_info['email']).first()
    
    if not user:

        # Crear nuevo usuario si no existe
        user = User(
            email=user_info['email'],
            is_google_auth=True, # Indicamos que es un usuario autenticado por Google    
        )         

        db.session.add(user)
        db.session.commit()
    
    # Generar Access Token y Refresh Token para el usuario
    access_token = generate_access_token(user.id)
    refresh_token = generate_refresh_token(user.id)

    return {
        'access_token': access_token,
        'refresh_token': refresh_token,
        'user': user_info
    }
