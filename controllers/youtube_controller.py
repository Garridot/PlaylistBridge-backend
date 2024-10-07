from flask import Blueprint, jsonify, request, redirect
from services.youtube_service import YouTubeService
from auth.youtube_auth import YouTubeAuth
from google.oauth2.credentials import Credentials

youtube_bp = Blueprint('youtube', __name__)
youtube_auth = YouTubeAuth()
youtube_service = YouTubeService()

@youtube_bp.route('/auth/login')
def login():
    auth_url = youtube_auth.get_auth_url()
    return redirect(auth_url)

@youtube_bp.route('/auth/callback')
def callback():
    code = request.args.get('code')
    token = youtube_auth.get_token(code)
    return jsonify({'youtube_token': token})

@youtube_bp.route('/playlists', methods=['GET'])
def get_playlists():
    token = request.headers.get('Authorization')   
    credentials = Credentials(token=token) 
    playlists = youtube_service.get_user_playlists(credentials)
    return jsonify(playlists)

@youtube_bp.route('/playlists/<playlist_id>/tracks', methods=['GET'])
def get_playlist_tracks(playlist_id):
    token = request.headers.get('Authorization')
    credentials = Credentials(token=token)
    tracks = youtube_service.get_playlist_tracks(credentials, playlist_id)
    return jsonify(tracks)
