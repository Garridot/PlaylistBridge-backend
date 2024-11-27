from googleapiclient.discovery import build
from google_auth_oauthlib.flow import InstalledAppFlow
from config import Config
from errors.custom_exceptions import InvalidTokenError
import requests

client_config = {
    "web": {
        "client_id": Config.YOUTUBE_CLIENT_ID,
        "project_id": "playlistbridge-api",
        "auth_uri": "https://accounts.google.com/o/oauth2/auth",
        "token_uri": "https://oauth2.googleapis.com/token",
        "auth_provider_x509_cert_url": "https://www.googleapis.com/oauth2/v1/certs",
        "client_secret": Config.YOUTUBE_CLIENT_SECRET,
        "redirect_uris": [Config.YOUTUBE_REDIRECT_URI]
    }
}

YOUTUBE_API_SCOPES = [
    "https://www.googleapis.com/auth/youtube",
    "https://www.googleapis.com/auth/youtube.readonly"
]

class YouTubeAuth:
    """
    Manages YouTube OAuth2 authentication for user login and channel access.

    This class handles the OAuth2 flow for YouTube, allowing users to authenticate 
    and retrieve an access token, refresh token, and other token details.
    """

    def __init__(self):
        """
        Initializes the OAuth2 flow for YouTube using provided client configuration 
        and specified scopes for YouTube data access.
        """
        self.flow = InstalledAppFlow.from_client_config(
            client_config, YOUTUBE_API_SCOPES
        )
        self.flow.redirect_uri = Config.YOUTUBE_REDIRECT_URI

    def get_auth_url(self):
        """
        Generates the YouTube authorization URL for user consent.

        Returns:
        -------
        str : 
            The URL for user authorization via YouTube.
        """
        auth_url, _ = self.flow.authorization_url(prompt='consent', access_type='offline')
        return auth_url

    def get_token(self, code):
        """
        Exchanges the authorization code for an access token, refresh token, and other details.

        Parameters:
        ----------
        code : str
            The authorization code returned after user consent.

        Returns:
        -------
        dict : 
            A dictionary containing access token, refresh token, token expiry, and ID token.
        """
        self.flow.fetch_token(code=code)
        credentials = self.flow.credentials 

        # Returns a dictionary with the key values ​​of the credentials object
        return {
            "access_token": credentials.token,
            "refresh_token": credentials.refresh_token,
            "token_expiry": credentials.expiry,
            "id_token": credentials.id_token
        }

    def refresh_access_token(self, refresh_token):       
        """        
        Uses the stored refresh token to obtain a new access token.

        Parameters:
        -----------
        user_id (str): The ID of the user.
        refresh_token (str): The refresh token for the user's YouTube account.

        Returns:
        --------
        dict: A dictionary containing the new access token and expiration details.
        
        Raises:
        -------
        InvalidTokenError: If the refresh token request fails.
        """        
        params = {
            "client_id": Config.YOUTUBE_CLIENT_ID,
            "client_secret": Config.YOUTUBE_CLIENT_SECRET,
            "refresh_token": refresh_token,
            "grant_type": "refresh_token"
        }        

        authorization_url = "https://oauth2.googleapis.com/token"

        response = requests.post(authorization_url, data=params)
        
        if response.ok:
            return response.json()
        else:
            error_msg = response.json().get("error_description", "Unknown error")
            raise InvalidTokenError(f"Failed to refresh the access token: {error_msg}")