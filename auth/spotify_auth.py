from spotipy.oauth2 import SpotifyOAuth
from config import Config

class SpotifyAuth:
    def __init__(self):
        self.sp_oauth = SpotifyOAuth(
            client_id=Config.SPOTIFY_CLIENT_ID,
            client_secret=Config.SPOTIFY_CLIENT_SECRET,
            redirect_uri=Config.SPOTIFY_REDIRECT_URI,
            scope="playlist-read-private playlist-modify-private"
        )

    def get_auth_url(self):
        return self.sp_oauth.get_authorize_url()

    def get_token(self, code):
        token_info = self.sp_oauth.get_access_token(code)
        return token_info['access_token']





