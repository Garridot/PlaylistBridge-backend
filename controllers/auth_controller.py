from flask import Blueprint, request, jsonify, redirect
from models.users import User
from auth.manual_auth import register_user, login_user
from auth.google_auth import google_auth_user
from connection.google_connection import GoogleAuth

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


