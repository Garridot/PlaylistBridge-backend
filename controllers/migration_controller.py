from flask import Blueprint, request, jsonify
from services.playlist_migration_service import PlaylistMigration
from services.youtube_service import YouTubeService
from services.spotify_service import SpotifyService
from errors.playlist_exceptions import PlaylistNotFoundError, TrackNotFoundError, APIRequestError, AuthenticationError
from decorators.route_protection import token_required
from decorators.stored_tokens_handler import stored_tokens_handler_errors

migration_bp = Blueprint('migration_controller', __name__)
spotify_service = SpotifyService()
youtube_service = YouTubeService()
playlist_migration_service = PlaylistMigration(
    spotify_service,
    youtube_service
)

@migration_bp.route('/spotify-to-youtube/<playlist_id>', methods=['POST'])
@token_required
@stored_tokens_handler_errors
def migrate_spotify_to_youtube(current_user, playlist_id):
    """
    Endpoint to migrate a Spotify playlist to YouTube.   
    """      
    result = playlist_migration_service.migrate_spotify_to_youtube(current_user.id, playlist_id)
    return jsonify(result), 200
   


@migration_bp.route('/youtube-to-spotify/<playlist_id>', methods=['POST'])
@token_required
@stored_tokens_handler_errors
def migrate_youtube_to_spotify(current_user, playlist_id):
    """
    Endpoint to migrate a YouTube playlist to Spotify.
    """    
    result = playlist_migration_service.migrate_youtube_to_spotify(current_user.id, playlist_id)
    return jsonify(result), 200
        
