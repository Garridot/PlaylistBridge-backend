from flask import Blueprint, jsonify, request, redirect
from services.spotify_service import SpotifyService
from connection.spotify_connection import SpotifyAuth
from decorators.route_protection import token_required
from decorators.stored_tokens_handler import stored_tokens_handler_errors
from token_handler.spotify_tokens import SpotifyTokenHandler

spotify_bp = Blueprint('spotify', __name__)
spotify_auth = SpotifyAuth()
spotify_service = SpotifyService()
spotify_tokens= SpotifyTokenHandler()

@spotify_bp.route('/auth/login')
@token_required
def login(user_id):
    """
    Generates the Spotify login URL where the user needs to authenticate.
    
    Returns:
    --------
    JSON response containing the Spotify authorization URL.
    """
    auth_url = spotify_auth.get_auth_url()
    return jsonify({"auth_url":auth_url})

@spotify_bp.route('/auth/callback')
@token_required
def callback(current_user):
    """
    Handles the callback from Spotify after successful authentication and stores access/refresh tokens.
    
    Parameters:
    -----------
    current_user: User
        The current user object (from token authentication).
    
    Returns:
    --------
    JSON response confirming successful authentication with Spotify and returns access and refresh tokens.
    """
    code = request.args.get('code')
 
    token_info = spotify_auth.get_token(code)

    spotify_tokens.stored_access_token(current_user.id, token_info)
    spotify_tokens.stored_refresh_token(current_user.id, token_info)

    return jsonify({
        'message': 'Spotify authentication successful', 
        'access_token': token_info['access_token'],
        'refresh_token': token_info["refresh_token"]
        })

@spotify_bp.route('/auth/logout')
@token_required
def logout(current_user): 
    spotify_tokens.revoke_access_token(current_user.id)
    spotify_tokens.revoke_refresh_token(current_user.id)
    return jsonify({'message': 'Spotify logout successful' })       

@spotify_bp.route('/playlists', methods=['GET'])
@token_required
@stored_tokens_handler_errors
def get_playlists(current_user): 
    playlists = spotify_service.get_user_playlists(current_user.id)
    return jsonify(playlists)

@spotify_bp.route('/playlists/<playlist_id>/tracks', methods=['GET'])
@token_required
@stored_tokens_handler_errors
def get_playlist_tracks(current_user, playlist_id):      
    tracks = spotify_service.get_playlist_tracks(current_user.id, playlist_id)
    return jsonify(tracks)
