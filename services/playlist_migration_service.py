from services.spotify_service import SpotifyService
from services.youtube_service import YouTubeService
from errors.playlist_exceptions import PlaylistNotFoundError,TrackNotFoundError,AuthenticationError,APIRequestError,InvalidPlatformError
import logging

logger = logging.getLogger(__name__)

spotify_service = SpotifyService()
youtube_service = YouTubeService()

class PlaylistMigration:
    def __init__(self, spotify_service, youtube_service):
        self.spotify_service = spotify_service
        self.youtube_service = youtube_service

    def migrate_spotify_to_youtube(self, current_user, playlist_id):
        """
        Migrates a Spotify playlist to YouTube.

        Parameters:
        - current_user: User instance containing the user's ID
        - playlist_id: ID of the Spotify playlist to migrate
        """
        try:   
            # Obtener detalles de la playlist y sus pistas
            playlist = self.spotify_service.get_playlist(current_user.id, playlist_id)
            tracks = self.spotify_service.get_playlist_tracks(current_user, playlist_id)

            # Crear playlist en YouTube
            youtube_playlist_id = self.youtube_service.create_playlist(current_user, playlist["name"])

            print(tracks)

            search_results = self.youtube_service.search_and_buffer_tracks(current_user, tracks)
            
            # Agregar cada canción de la playlist de Spotify a la nueva playlist en YouTube
            for track in search_results:
                track_name = track["track"]["name"]
                artist = track["track"]["artists"][0]["name"]
                self.youtube_service.add_track_to_playlist(current_user, youtube_playlist_id, track_name, artist)

            logger.info(f"Playlist '{playlist['name']}' migrated successfully from Spotify to YouTube.")
            return youtube_playlist_id

        except PlaylistNotFoundError as e:
            logger.error(f"Playlist not found on Spotify: {e}")
            raise
        except TrackNotFoundError as e:
            logger.error(f"Track not found on YouTube: {e}")
            raise
        except APIRequestError as e:
            logger.error(f"API request error during migration: {e}")
            raise
        except AuthenticationError as e:
            logger.error(f"Authentication error with Spotify or YouTube: {e}")
            raise

    def migrate_youtube_to_spotify(self, current_user, playlist_id):
        """
        Migrates a YouTube playlist to Spotify.

        Parameters:
        - current_user: User instance containing the user's ID
        - playlist_id: ID of the YouTube playlist to migrate
        """
        try:
            
            # Obtener detalles de la playlist y sus pistas            
            playlist = self.youtube_service.get_playlist(current_user, playlist_id)            
            tracks = self.youtube_service.get_playlist_tracks(current_user, playlist_id)

            # Crear playlist en Spotify            
            spotify_playlist_id = self.spotify_service.create_playlist(current_user, playlist["snippet"]["title"])            

            
            track_queries = [f"{track['track']['name']} {track['track']['artists'][0]['name']}" for track in tracks]            
            batch_results = self.spotify_service.batch_search_tracks(current_user, track_queries)            
            
            # Agregar cada canción de la playlist de YouTube a la nueva playlist en Spotify
            for track in batch_results:
                print(track)                
                track_name = track['track']['name']                
                artist = track['track']['artists'][0]['name']                
                self.spotify_service.add_track_to_playlist(current_user, spotify_playlist_id, track_name, artist)

            logger.info(f"Playlist '{playlist['snippet']['title']}' migrated successfully from YouTube to Spotify.")
            return spotify_playlist_id


        except PlaylistNotFoundError as e:
            logger.error(f"Playlist not found on YouTube: {e}")
            raise
        except TrackNotFoundError as e:
            logger.error(f"Track not found on Spotify: {e}")
            raise
        except APIRequestError as e:
            logger.error(f"API request error during migration: {e}")
            raise
        except AuthenticationError as e:
            logger.error(f"Authentication error with YouTube or Spotify: {e}")
            raise