from flask import Blueprint, jsonify, request, redirect
from services.spotify_service import SpotifyService
from auth.spotify_auth import SpotifyAuth

spotify_bp = Blueprint('spotify', __name__)
spotify_auth = SpotifyAuth()
spotify_service = SpotifyService()

@spotify_bp.route('/auth/login')
def login():
    auth_url = spotify_auth.get_auth_url()
    return redirect(auth_url)

@spotify_bp.route('/auth/callback')
def callback():
    code = request.args.get('code')
    token = spotify_auth.get_token(code)
    return jsonify({'spotify_token': token})

@spotify_bp.route('/playlists', methods=['GET'])
def get_playlists():
    token = request.headers.get('Authorization')
    playlists = spotify_service.get_user_playlists(token)
    return jsonify(playlists)

@spotify_bp.route('/playlists/<playlist_id>/tracks', methods=['GET'])
def get_playlist_tracks(playlist_id):
    token = request.headers.get('Authorization')
    tracks = spotify_service.get_playlist_tracks(token, playlist_id)
    return jsonify(tracks)
