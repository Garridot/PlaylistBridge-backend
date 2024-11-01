from flask import Blueprint, request, jsonify
from services.playlist_migration_service import PlaylistMigration
from errors.playlist_exceptions import PlaylistNotFoundError, TrackNotFoundError, APIRequestError, AuthenticationError
from decorators.route_protection import token_required
from decorators.stored_tokens_handler import stored_tokens_handler_errors

migration_bp = Blueprint('migration_controller', __name__)
playlist_migration_service = PlaylistMigration()

@migration_bp.route('/spotify-to-youtube/<playlist_id>', methods=['POST'])
@token_required
@stored_tokens_handler_errors
def migrate_spotify_to_youtube(current_user, playlist_id):
    """
    Endpoint to migrate a Spotify playlist to YouTube.   
    """  
    try:
        result = playlist_migration_service.migrate_spotify_to_youtube(user_id, playlist_id)
        return jsonify(result), 200
    except (PlaylistNotFoundError, TrackNotFoundError) as e:
        return jsonify({"error": str(e)}), 404
    except APIRequestError as e:
        return jsonify({"error": str(e)}), 500
    except AuthenticationError as e:
        return jsonify({"error": str(e)}), 401
    except Exception as e:
        return jsonify({"error": "An unexpected error occurred"}), 500


@migration_bp.route('/youtube-to-spotify/<playlist_id>', methods=['POST'])
@token_required
@stored_tokens_handler_errors
def migrate_youtube_to_spotify(current_user, playlist_id):
    """
    Endpoint to migrate a YouTube playlist to Spotify.
    """

    try:
        result = playlist_migration_service.migrate_youtube_to_spotify(user_id, playlist_id)
        return jsonify(result), 200
    except (PlaylistNotFoundError, TrackNotFoundError) as e:
        return jsonify({"error": str(e)}), 404
    except APIRequestError as e:
        return jsonify({"error": str(e)}), 500
    except AuthenticationError as e:
        return jsonify({"error": str(e)}), 401
    except Exception as e:
        return jsonify({"error": "An unexpected error occurred"}), 500
