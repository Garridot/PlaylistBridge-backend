import spotipy
from connection.spotify_connection import SpotifyAuth
from token_handler.spotify_tokens import SpotifyTokenHandler
from flask import jsonify
from errors.playlist_exceptions import PlaylistNotFoundError, TrackNotFoundError, APIRequestError, InvalidPlaylistIDError
from errors.custom_exceptions import NoRefreshTokenError
from concurrent.futures import ThreadPoolExecutor
from spotipy.exceptions import SpotifyException
import logging

logger = logging.getLogger(__name__)

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

    def get_user_info(self, user_id):
        """
        Retrieves details of the user account.

        Parameters:
        -----------
        user_id (str): The unique user identifier.        

        Returns:
        -----------
        dict: Details of the user account including name, followers, profile picture, etc.
        """
        sp = self._get_spotify_client(user_id)
        try:
            return sp.me()
        except SpotifyException as e:
            raise APIRequestError(f"Error retrieving details of the user account: {e}")

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
        try:
            playlists = sp.current_user_playlists()            

            # Filter the playlists that belong to the user.
            user_playlists = [
                playlist for playlist in playlists['items'] if playlist != None and playlist['owner']['id'] == sp.me()['id']
            ]
            return user_playlists

        except SpotifyException as e:
            raise APIRequestError(f"Error retrieving playlists: {e}")

    def get_playlist(self, user_id, playlist_id):
        """
        Retrieves details of a specific playlist by its ID.

        Parameters:
        -----------
        user_id (str): The unique user identifier.
        playlist_id (str): The ID of the playlist to retrieve.

        Returns:
        -----------
        dict: Details of the playlist including name, description, and tracks.

        Raises:
        -----------
        PlaylistNotFoundError: If the playlist could not be found on Spotify.
        """
        sp = self._get_spotify_client(user_id)
        
        try:
            playlist = sp.playlist(playlist_id)
            return playlist
        except SpotifyException as e:
            if e.http_status == 404:
                raise PlaylistNotFoundError(f"Playlist with ID '{playlist_id}' not found on Spotify.")
            elif e.http_status == 400:
                raise InvalidPlaylistIDError(f"The playlist ID '{playlist_id}' is invalid.")
            else:
                raise APIRequestError(f"Failed to retrieve playlist: {str(e)}")   

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
        try:            
            tracks = sp.playlist_tracks(playlist_id)
            return tracks["items"]
        except SpotifyException as e:
            if e.http_status == 404:
                raise PlaylistNotFoundError(f"Playlist with ID '{playlist_id}' not found on Spotify.")
            else:
                raise APIRequestError(f"Error retrieving playlist tracks: {e}")

    def create_playlist(self, user_id, name, description, public=True):
        """
        Creates a new playlist for the specified user on Spotify.

        Parameters:
        -----------
        user_id (str): The unique user identifier.
        name (str): The name of the new playlist.
        description (str): The description of the new playlist.
        public (bool): Visibility of the playlist, public or private.

        Returns: 
        -----------
        str: The ID of the created playlist.
        """
        sp = self._get_spotify_client(user_id)
        try:
            current_user_id = sp.me()['id']
            playlist = sp.user_playlist_create(user=current_user_id, name=name, description=description, public=public)
            return playlist['id']
        except SpotifyException as e:
            raise APIRequestError(f"Error creating playlist: {e}")        

    def add_track_to_playlist(self, user_id, playlist_id, track_id):
        """
        Adds a track to the specified playlist by searching for the track on Spotify.

        Parameters:
        -----------
        user_id (str): The unique user identifier.
        playlist_id (str): The ID of the playlist to add the track to.        
        track_id (str): The ID of the track to add to..

        Raises:
        -----------
        TrackNotFoundError: If the track could not be found on Spotify.
        """
        sp = self._get_spotify_client(user_id)
        
        try:
            sp.playlist_add_items(playlist_id, [track_id])
        except SpotifyException as e:
            if e.http_status == 404:
                raise TrackNotFoundError(f"Track with ID '{track_id}' not found on Spotify.")
            else:
                raise APIRequestError(f"Error adding track to playlist: {e}")  

    def search_track(self, user_id, track_query):                
        """
        Search for a specific song by its title and return the first result.
        """
        sp = self._get_spotify_client(user_id)
        try:
            result = sp.search(track_query, limit=1, type="track")
            if result['tracks']['items']:
                return result['tracks']['items'][0]
            else:
                raise TrackNotFoundError(f"No results found for '{track_query}'.")
        except SpotifyException as e:
            raise APIRequestError(f"Error searching for track: {e}")       