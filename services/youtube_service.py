from googleapiclient.discovery import build
from google.oauth2.credentials import Credentials

class YouTubeService:
    def get_user_playlists(self, credentials):
        youtube = build('youtube', 'v3', credentials=credentials)
        request = youtube.playlists().list(
            part="snippet",
            mine=True
        )
        response = request.execute()
        return response['items']

    def get_playlist_tracks(self, credentials, playlist_id):        
        youtube = build('youtube', 'v3', credentials=credentials)
        request = youtube.playlistItems().list(
            part="snippet",
            playlistId=playlist_id
        )
        response = request.execute()
        return response['items']

