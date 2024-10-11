import spotipy
from connection.spotify_connection import SpotifyAuth
from token_handler.spotify_tokens import SpotifyTokenHandler
from flask import jsonify

spotify_tokens= SpotifyTokenHandler()      

class SpotifyService:
    """
    Provides services for interacting with Spotify's API using Spotipy.
    
    Methods:
    --------
    get_user_playlists(user_id: str) -> list:
        Retrieves the playlists of the specified user.
    
    get_playlist_tracks(user_id: str, playlist_id: str) -> list:
        Retrieves the tracks of a specific playlist.
    """

    def __init__(self):
        """
        Initializes the SpotifyAuth object and sets up access to Spotify API via Spotipy.
        """
        self.spotify_auth = SpotifyAuth()

    def _get_spotify_client(self, user_id):
        """
        Internal method that retrieves the Spotify client using the user’s access token. If the token is expired or invalid, it refreshes it.
        
        Parameters:
        -----------
        user_id (str): The unique user identifier.

        Returns:
        -----------
        A Spotify object from the Spotipy library to make API requests.
        """
        token = spotify_tokens.get_access_token(user_id)
        if not token:
            raise NoRefreshTokenError()
        return spotipy.Spotify(auth=token)
        
    def get_user_playlists(self, user_id):
        """
        Retrieves the playlists of the specified user by making a request to Spotify’s API.
        
        Parameters:
        -----------
        user_id (str): The unique user identifier.

        Returns: 
        -----------
        A list of playlists owned by the user.
        """
        sp = self._get_spotify_client(user_id)
        playlists = sp.current_user_playlists()
        return playlists['items']

    def get_playlist_tracks(self, user_id, playlist_id):
        """
        Retrieves the tracks of the specified playlist from Spotify’s API.
        
        Parameters:
        -----------
        user_id (str): The unique user identifier.
        playlist_id (str): The ID of the playlist to retrieve tracks from.

        Returns: 
        -----------
        A list of tracks in the playlist.
        """
        sp = self._get_spotify_client(user_id)
        tracks = sp.playlist_tracks(playlist_id)
        return tracks['items']