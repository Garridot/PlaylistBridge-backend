from flask import Blueprint, jsonify, request
from services.youtube_service import YouTubeService
from connection.youtube_connection import YouTubeAuth
from decorators.route_protection import token_required
from decorators.stored_tokens_handler import stored_tokens_handler_errors
from token_handler.youtube_tokens import YouTubeTokenHandler

youtube_bp = Blueprint('youtube', __name__)
youtube_auth = YouTubeAuth()
youtube_service = YouTubeService()
youtube_tokens = YouTubeTokenHandler()

@youtube_bp.route('/auth/login')
@token_required
def login(user_id):
    """
    Generates the OAuth login URL for YouTube and returns it.

    Parameters:
    -----------
    user_id (str): The ID of the authenticated user.

    Returns:
    --------
    dict: Contains the URL to redirect the user to YouTube for authentication.
    """
    auth_url = youtube_auth.get_auth_url()
    return jsonify({"auth_url": auth_url})


@youtube_bp.route('/auth/callback')
@token_required
def callback(current_user):
    """
    Callback endpoint for handling the authorization code returned by YouTube and storing the access tokens.

    Args:
        current_user (object): The current authenticated user object.

    Returns:
        json: A JSON object containing the access and refresh tokens.
    """    
    code = request.args.get('code')    
    token_info = youtube_auth.get_token(code)        
    youtube_tokens.store_tokens(current_user.id, token_info)
    
    return jsonify({
        'message': 'YouTube authentication successful', 
        'access_token': token_info['access_token'],
        'refresh_token': token_info['refresh_token']
    })


@youtube_bp.route('/auth/logout')
@token_required
@stored_tokens_handler_errors
def logout(current_user):
    youtube_service.logout(current_user.id)
    return jsonify({'message': 'YouTube logout successful'})


@youtube_bp.route('/playlists', methods=['GET'])
@token_required
@stored_tokens_handler_errors
def get_playlists(current_user):
    playlists = youtube_service.get_user_playlists_list(current_user.id)
    return jsonify(playlists)

@youtube_bp.route('/playlists/<playlist_id>', methods=['GET'])
@token_required
# @stored_tokens_handler_errors
def get_playlist(current_user, playlist_id): 
    playlist = youtube_service.get_playlist(current_user.id, playlist_id)
    return jsonify(playlist)        


@youtube_bp.route('/playlists/<playlist_id>/tracks', methods=['GET'])
@token_required
@stored_tokens_handler_errors
def get_playlist_tracks(current_user, playlist_id):     
    tracks = youtube_service.get_playlist_tracks(current_user.id, playlist_id)
    return jsonify(tracks)
