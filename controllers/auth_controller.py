from flask import Blueprint, request, jsonify, redirect
from models.users import User
from auth.manual_auth import register_user, login_user
from auth.google_auth import google_auth_user
from connection.google_connection import GoogleAuth
from auth.token_manager import refresh_access_token, revoke_refresh_token
from decorators.route_protection import token_required

auth_bp = Blueprint('auth', __name__)

@auth_bp.route('/register', methods=['POST'])
def register():
    data = request.get_json()
    user = register_user(data)
    return user

@auth_bp.route('/login', methods=['POST'])
def login():
    data = request.get_json()
    user = login_user(data)
    return user

@auth_bp.route('/logout', methods=['POST'])
@token_required  
def logout(current_user):
    refresh_token = request.headers.get('x-refresh-token')
    if refresh_token:
        user_id = current_user.id
        revoke_refresh_token(user_id)  # Revocar el token del usuario
    return jsonify({'message': 'Logged out successfully!'}), 200


@auth_bp.route('/refresh-token', methods=['POST'])
def refresh_token():
    refresh_token = request.headers.get('x-refresh-token')
    new_refresh_token = refresh_access_token(refresh_token)
    return new_refresh_token


google_auth = GoogleAuth()

@auth_bp.route('/google/login', methods=['GET'])
def google_login():
    auth_url = google_auth.get_auth_url()
    return redirect(auth_url)

@auth_bp.route('/google/callback', methods=['GET'])
def google_callback():
    code = request.args.get('code')
    token = google_auth.get_token(code)
    user_info = google_auth.get_google_user_info()
    google_auth_user(user_info)

    return jsonify(google_auth)


