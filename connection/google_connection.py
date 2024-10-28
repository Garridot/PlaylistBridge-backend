from googleapiclient.discovery import build
from google_auth_oauthlib.flow import InstalledAppFlow
from config import Config

client_config = {
    "web": {
        "client_id": Config.GOOGLE_CLIENT_ID,
        "project_id": "playlistbridge-api",
        "auth_uri": "https://accounts.google.com/o/oauth2/auth",
        "token_uri": "https://oauth2.googleapis.com/token",
        "auth_provider_x509_cert_url": "https://www.googleapis.com/oauth2/v1/certs",
        "client_secret": Config.GOOGLE_CLIENT_SECRET,
        "redirect_uris": [Config.GOOGLE_REDIRECT_URI]
    }
}

GOOGLE_API_SCOPES = [
    'openid', 
    'https://www.googleapis.com/auth/userinfo.profile', 
    'https://www.googleapis.com/auth/userinfo.email'
]

class GoogleAuth:
    """
    Manages Google OAuth2 authentication for user login and profile access.

    This class handles the OAuth2 flow for Google, allowing users to authenticate 
    and retrieve an access token, refresh token, and profile information.
    """

    def __init__(self):
        """
        Initializes the OAuth2 flow for Google using provided client configuration 
        and specified scopes for profile and email access.
        """
        self.flow = InstalledAppFlow.from_client_config(
            client_config, GOOGLE_API_SCOPES
        )
        self.flow.redirect_uri = Config.GOOGLE_REDIRECT_URI

    def get_auth_url(self):
        """
        Generates the Google authorization URL for user consent.

        Returns:
        -------
        str : 
            The URL for user authorization via Google.
        """
        auth_url, _ = self.flow.authorization_url(prompt='consent')
        return auth_url

    def get_token(self, code):
        """
        Exchanges the authorization code for an access token.

        Parameters:
        ----------
        code : str
            The authorization code returned after user consent.

        Returns:
        -------
        str : 
            The access token for authenticated requests.
        """
        self.flow.fetch_token(code=code)
        credentials = self.flow.credentials
        print(credentials)
        return credentials.token

    def get_google_user_info(self):
        """
        Retrieves the authenticated user's Google profile information.

        Returns:
        -------
        dict : 
            A dictionary containing the user's email and name.
        """
        credentials = self.flow.credentials  
        service = build('oauth2', 'v2', credentials=credentials)        
        user_info = service.userinfo().get().execute()        
        return {
            "email": user_info['email'],
            "name": user_info.get('name'),
        }
