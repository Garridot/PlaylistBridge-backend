from flask import request, jsonify
from werkzeug.security import generate_password_hash, check_password_hash
from token_handler.auth_tokens import generate_access_token, generate_refresh_token
from models.users import User
from extensions.auth_extensions import password_validator
from database.db_connection import db


def register_user(data):
    """
    Register a new user manually with email and password authentication.   

    Parameters:
    ----------
    data : dict
        A dictionary containing user registration details:
        - 'email': User's email address.
        - 'password': Password provided by the user.

    Returns:
    -------
    Response
        Flask JSON response indicating the status of the registration:
        - Success message (201) if registration is successful.
        - Error message (400) if user already exists or if password is weak.
    """

    email = data.get('email')
    password = data.get('password')

    # check if the user already exists in the database.
    if User.query.filter_by(email=email).first():
        return jsonify({"message": "User already exists"}), 400

    if not password_validator(password):
        return jsonify({"error": "Weak password"}), 400

    user = User(email=email)
    user.set_password(password)

    # save the user in the database.
    db.session.add(user)
    db.session.commit()

    return jsonify({"message": "User created successfully"}), 201


def login_user(data):
    """
    Authenticate a user and return access and refresh tokens for a valid login.
    Parameters:
    ----------
    data : dict
        A dictionary containing user login details:
        - 'email': User's email address.
        - 'password': Password provided by the user.

    Returns:
    -------
    Response
        Flask JSON response containing:
        - 'access_token': JWT access token for session management.
        - 'refresh_token': JWT refresh token for prolonged access.
        - 'user': A dictionary with user's ID and email.
        - If credentials are invalid, returns a 401 error with an "Invalid credentials" message.    
    """
    
    email = data.get('email')
    password = data.get('password')

    # check if the user already exists in the database.
    user = User.query.filter_by(email=email).first()
    
    if not user or not check_password_hash(user.password_hash, password):
        return jsonify({"message": "Invalid credentials"}), 401

    # generate Access Token and Refresh Token for the user.
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
