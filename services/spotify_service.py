import spotipy
from connection.spotify_connection import SpotifyAuth
from token_handler.spotify_tokens import SpotifyTokenHandler
from flask import jsonify
from errors.playlist_exceptions import PlaylistNotFoundError, TrackNotFoundError
from errors.custom_exceptions import NoRefreshTokenError

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
            return {
                "name": playlist["name"],
                "description": playlist["description"],
                "tracks": playlist["tracks"]["items"]
            }
        except spotipy.exceptions.SpotifyException as e:
            if e.http_status == 404:
                raise PlaylistNotFoundError(f"Playlist with ID '{playlist_id}' not found on Spotify.")
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
        tracks = sp.playlist_tracks(playlist_id)
        return tracks['items']

    def create_playlist(self, user_id, name, public=True):
        """
        Creates a new playlist for the specified user on Spotify.

        Parameters:
        -----------
        user_id (str): The unique user identifier.
        name (str): The name of the new playlist.
        public (bool): Visibility of the playlist, public or private.

        Returns: 
        -----------
        str: The ID of the created playlist.
        """
        sp = self._get_spotify_client(user_id)
        playlist = sp.user_playlist_create(user=user_id, name=name, public=public)
        return playlist['id'] 

    def add_track_to_playlist(self, user_id, playlist_id, track_name, artist_name):
        """
        Adds a track to the specified playlist by searching for the track on Spotify.

        Parameters:
        -----------
        user_id (str): The unique user identifier.
        playlist_id (str): The ID of the playlist to add the track to.
        track_name (str): The name of the track.
        artist_name (str): The name of the track's artist.

        Raises:
        -----------
        TrackNotFoundError: If the track could not be found on Spotify.
        """
        sp = self._get_spotify_client(user_id)
        
        # Search for the track
        query = f"track:{track_name} artist:{artist_name}"
        result = sp.search(q=query, type='track', limit=1)
        
        if not result['tracks']['items']:
            raise TrackNotFoundError(f"Track '{track_name}' by '{artist_name}' not found on Spotify.")
        
        # Get track ID and add to playlist
        track_id = result['tracks']['items'][0]['id']
        sp.playlist_add_items(playlist_id, [track_id])   


    def batch_search_tracks(self, current_user, track_queries):
        # Divide los tracks en lotes de 50
        track_batches = [track_queries[i:i + 50] for i in range(0, len(track_queries), 50)]
        results = []
        
        for batch in track_batches:
            query = " OR ".join(batch)
            batch_results = self.spotify.search(query, limit=50, type="track")
            results.extend(batch_results["tracks"]["items"])
        return results
       