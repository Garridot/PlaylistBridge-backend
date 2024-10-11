from googleapiclient.discovery import build
from token_handler.youtube_tokens import YouTubeTokenHandler

class YouTubeService:
    """
    Service layer for interacting with the YouTube API.

    Methods:
    --------
    get_auth_url():
        Returns the URL for user authentication with YouTube (Google OAuth).

    get_token(user_id, code):
        Exchanges the authorization code for tokens and stores them.

    logout(user_id):
        Revokes the user's YouTube tokens.

    get_user_playlists(user_id):
        Retrieves a list of YouTube playlists for the authenticated user.
        Returns:
            list: A list of playlists .
        Raises:
            HttpError: If the YouTube API call fails.

    get_playlist_tracks(user_id, playlist_id):
        Retrieves the tracks from a specific YouTube playlist.
        Parameters:
        -----------
        playlist_id (str): The ID of the playlist.
    """
    
    def __init__(self):
        self.api_service_name = "youtube"
        self.api_version = "v3"
        self.youtube_tokens = YouTubeTokenHandler()

    def get_auth_url(self):
        return self.youtube_tokens.get_auth_url()

    def get_token(self, user_id, code):
        token_info = self.youtube_tokens.exchange_code_for_tokens(user_id, code)
        return token_info

    def logout(self, user_id):
        self.youtube_tokens.revoke_tokens(user_id)

    def get_user_playlists(self, user_id):        
        token = self.youtube_tokens.get_valid_access_token(user_id)
        
        youtube = build(self.api_service_name, self.api_version, credentials=token)
        request = youtube.playlists().list(part="snippet", mine=True, maxResults=10)
        response = request.execute()
        return response['items']
        
    def get_playlist_tracks(self, user_id, playlist_id):        
        token = self.youtube_tokens.get_valid_access_token(user_id)
        
        youtube = build(self.api_service_name, self.api_version, credentials=token)
        request = youtube.playlistItems().list(part="snippet", playlistId=playlist_id, maxResults=10)
        response = request.execute()
        return response['items']
        
