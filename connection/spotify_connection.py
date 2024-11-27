from spotipy.oauth2 import SpotifyOAuth
from config import Config

class SpotifyAuth:
    """
    Manages Spotify OAuth2 authentication for user login and playlist access.

    This class handles the OAuth2 flow for Spotify, allowing users to authenticate 
    and retrieve an access token and refresh token for playlist access and modification.
    """

    def __init__(self):
        """
        Initializes the OAuth2 flow for Spotify using provided client configuration
        and a specified scope for playlist read and modification access.
        """
        self.sp_oauth = SpotifyOAuth(
            client_id=Config.SPOTIFY_CLIENT_ID,
            client_secret=Config.SPOTIFY_CLIENT_SECRET,
            redirect_uri=Config.SPOTIFY_REDIRECT_URI,
            scope="playlist-read-private playlist-modify-private playlist-modify-public"
        )

    def get_auth_url(self):
        """
        Generates the Spotify authorization URL for user consent.

        Returns:
        -------
        str : 
            The URL for user authorization via Spotify.
        """
        return self.sp_oauth.get_authorize_url()

    def get_token(self, code):
        """
        Exchanges the authorization code for access and refresh tokens.

        Parameters:
        ----------
        code : str
            The authorization code returned after user consent.

        Returns:
        -------
        dict : 
            A dictionary containing the access token, refresh token, and token expiration details.
        """
        token_info = self.sp_oauth.get_access_token(code)   
        return token_info





