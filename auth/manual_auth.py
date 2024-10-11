from flask import request, jsonify
from werkzeug.security import generate_password_hash, check_password_hash
from token_handler.auth_tokens import generate_access_token, generate_refresh_token
from models.users import User
from extensions.auth_extensions import password_validator
from database.db_connection import db


def register_user(data):

    email = data.get('email')
    password = data.get('password')

    if User.query.filter_by(email=email).first():
        return jsonify({"message": "User already exists"}), 400

    if not password_validator(password):
        return jsonify({"error": "Weak password"}), 400

    user = User(email=email)
    user.set_password(password)

    db.session.add(user)
    db.session.commit()

    return jsonify({"message": "User created successfully"}), 201


def login_user(data):
    email = data.get('email')
    password = data.get('password')

    # Buscar al usuario por correo electrónico
    user = User.query.filter_by(email=email).first()
    
    if not user or not check_password_hash(user.password_hash, password):
        return jsonify({"message": "Invalid credentials"}), 401

    # Generar Access Token y Refresh Token
    access_token = generate_access_token(user.id)
    refresh_token = generate_refresh_token(user.id)    

    return jsonify({
        'access_token': access_token,
        'refresh_token': refresh_token,
        'user': {
            'id': user.id,
            'email': user.email,
        }
    }), 200
