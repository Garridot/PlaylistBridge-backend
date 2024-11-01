from googleapiclient.discovery import build
from token_handler.youtube_tokens import YouTubeTokenHandler
import time

class YouTubeService:
    """
    Service layer for interacting with the YouTube API.   
    """    
    def __init__(self):
        self.api_service_name = "youtube"
        self.api_version = "v3"
        self.youtube_tokens = YouTubeTokenHandler()

    def get_auth_url(self):
        """
        get_auth_url():
            Returns the URL for user authentication with YouTube (Google OAuth).
        """
        return self.youtube_tokens.get_auth_url()

    def get_token(self, user_id, code):
        """
        get_token(user_id, code):
            Exchanges the authorization code for tokens and stores them.
        """
        token_info = self.youtube_tokens.exchange_code_for_tokens(user_id, code)
        print(token_info)
        return token_info

    def logout(self, user_id):
        """
        logout(user_id):
            Revokes the user's YouTube tokens.
        """
        self.youtube_tokens.revoke_tokens(user_id)

    def get_user_playlists_list(self, user_id):       
        """
        get_user_playlists(user_id):
        Retrieves a list of YouTube playlists for the authenticated user.
        Returns:
            list: A list of playlists .
        Raises:
            HttpError: If the YouTube API call fails.

        """ 
        token = self.youtube_tokens.get_valid_access_token(user_id)
        
        youtube = build(self.api_service_name, self.api_version, credentials=token)
        request = youtube.playlists().list(part="snippet", mine=True)
        response = request.execute()
        return response['items']        

    def get_playlist(self, user_id, playlist_id):
        """
        Retrieves details of a specific YouTube playlist by its ID.
        
        Parameters:
        -----------
        user_id (str): The unique user identifier.
        playlist_id (str): The ID of the playlist to retrieve.

        Returns:
        --------
        dict: Details of the playlist including title, description, and items.

        Raises:
        --------
        HttpError: If the YouTube API call fails.
        """
        token = self.youtube_tokens.get_valid_access_token(user_id)
        youtube = build(self.api_service_name, self.api_version, credentials=token)
        
        request = youtube.playlists().list(part="snippet", id=playlist_id)
        response = request.execute()

        return response
        
    def get_playlist_tracks(self, user_id, playlist_id):   
        """
        get_playlist_tracks(user_id, playlist_id):
        Retrieves the tracks from a specific YouTube playlist.
        Parameters:
        -----------
        playlist_id (str): The ID of the playlist.
        """   
        token = self.youtube_tokens.get_valid_access_token(user_id)
        
        youtube = build(self.api_service_name, self.api_version, credentials=token)
        request = youtube.playlistItems().list(part="snippet", playlistId=playlist_id, maxResults=10)
        response = request.execute()
        return response['items']

    def create_playlist(self, user_id, title, description, privacy_status="public"):
        """
        Creates a new YouTube playlist.
        
        Parameters:
        -----------
        user_id (str): The unique user identifier.
        title (str): Title of the new playlist.
        description (str): Description of the new playlist.
        privacy_status (str): Privacy status of the playlist (e.g., "private", "public").

        Returns:
        --------
        dict: Details of the newly created playlist.
        
        Raises:
        --------
        HttpError: If the YouTube API call fails.
        """
        token = self.youtube_tokens.get_valid_access_token(user_id)
        youtube = build(self.api_service_name, self.api_version, credentials=token)
        
        request = youtube.playlists().insert(
            part="snippet,status",
            body={
                "snippet": {
                    "title": title,
                    "description": description
                },
                "status": {
                    "privacyStatus": privacy_status
                }
            }
        )
        response = request.execute()
        return response

    def add_track_to_playlist(self, user_id, playlist_id, video_id):
        """
        Adds a video to a specified YouTube playlist.
        
        Parameters:
        -----------
        user_id (str): The unique user identifier.
        playlist_id (str): The ID of the playlist to add the video to.
        video_id (str): The ID of the video to be added.

        Returns:
        --------
        dict: Details of the action performed.
        
        Raises:
        --------
        HttpError: If the YouTube API call fails.
        """
        token = self.youtube_tokens.get_valid_access_token(user_id)
        youtube = build(self.api_service_name, self.api_version, credentials=token)
        
        request = youtube.playlistItems().insert(
            part="snippet",
            body={
                "snippet": {
                    "playlistId": playlist_id,
                    "resourceId": {
                        "kind": "youtube#video",
                        "videoId": video_id
                    }
                }
            }
        )
        response = request.execute()
        return response        

    def search_and_buffer_tracks(self, current_user, tracks):
        buffer = []
        results = []

        for track in tracks:
            track_name = track["track"]["name"]
            artist = track["track"]["artists"][0]["name"]
            query = f"{track_name} {artist}"

            # Realiza la búsqueda y acumula en buffer
            search_result = self.youtube.search(query)
            if search_result:
                buffer.append(search_result)

            # Procesa el buffer cada 5 pistas
            if len(buffer) >= 5:
                results.extend(buffer)
                buffer.clear()
                time.sleep(1)  # Pausa para evitar exceder el límite de la API

        # Agrega cualquier búsqueda restante en el buffer
        if buffer:
            results.extend(buffer)
        return results    
        
