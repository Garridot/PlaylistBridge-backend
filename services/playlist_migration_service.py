from services.spotify_service import SpotifyService
from services.youtube_service import YouTubeService
from errors.playlist_exceptions import PlaylistNotFoundError,TrackNotFoundError,AuthenticationError,APIRequestError,InvalidPlatformError
import logging
import time  

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
        tracks_migrated = [] # a list to store the results of the migrated songs.    
        try:   
            # Retrieve details of a Spotify playlist and its tracks.            
            spotify_playlist = self.spotify_service.get_playlist(current_user, playlist_id)            
            spotify_tracks = self.spotify_service.get_playlist_tracks(current_user, playlist_id)   

            # Create playlist on YouTube
            youtube_playlist = self.youtube_service.create_playlist(current_user, spotify_playlist["name"],spotify_playlist["description"])

            for i, track in enumerate(spotify_tracks): 
                
                time.sleep(5)
                youtube_result = self.youtube_service.search_track(current_user, track) 

                if youtube_result:    
                    # Add each song from the Spotify playlist to the new YouTube playlist.                    
                    self.youtube_service.add_track_to_playlist(current_user, youtube_playlist["id"], youtube_result["id"]["videoId"])

                    tracks_migrated.append(youtube_result)                                 
            
            logger.info(f"Playlist '{spotify_playlist['name']}' migrated successfully from Spotify to YouTube.")            
            return {"playlist_created": youtube_playlist, "tracks_migrated": tracks_migrated}

        except PlaylistNotFoundError as e:
            logger.error(f"Playlist not found on Spotify: {e}")
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

        tracks_migrated = [] # a list to store the results of the migrated songs.    
        try:
            
            # Retrieve details of a YouTube playlist and its tracks.            
            youtube_playlist = self.youtube_service.get_playlist(current_user, playlist_id)                         
            youtube_tracks = self.youtube_service.get_playlist_tracks(current_user, playlist_id)            

            # Create playlist on Spotify
            spotify_playlist = self.spotify_service.create_playlist(current_user, youtube_playlist["items"][0]["snippet"]["title"], youtube_playlist["items"][0]["snippet"]["description"])

            for i, track in enumerate(youtube_tracks): 
                time.sleep(5)                
                track_query = f'{track["snippet"]["title"]}'
                spotify_result = self.spotify_service.search_track(current_user, track_query)                

                if spotify_result: 
                    
                    # Add each song from the YouTube playlist to the new Spotify playlist.                                          
                    self.spotify_service.add_track_to_playlist(current_user, spotify_playlist["id"], spotify_result['id'])   
                    tracks_migrated.append(spotify_result)    
            
            return {"playlist_created": spotify_playlist, "tracks_migrated": tracks_migrated}            

        except PlaylistNotFoundError as e:
            logger.error(f"Playlist not found on YouTube: {e}")
            raise        
        except APIRequestError as e:
            logger.error(f"API request error during migration: {e}")
            raise
        except AuthenticationError as e:
            logger.error(f"Authentication error with YouTube or Spotify: {e}")
            raise