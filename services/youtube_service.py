from googleapiclient.discovery import build
from googleapiclient.errors import HttpError
from token_handler.youtube_tokens import YouTubeTokenHandler
from errors.youtube_exceptions import *
from concurrent.futures import ThreadPoolExecutor
import time
import logging

logger = logging.getLogger(__name__)

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
        return token_info

    def logout(self, user_id):
        """
        logout(user_id):
            Revokes the user's YouTube tokens.
        """
        self.youtube_tokens.revoke_tokens(user_id)

    def get_user_account_info(self, user_id):
        """
        Retrieves account details of the authenticated YouTube user.

        Parameters:
        -----------
        user_id (str): The unique user identifier.

        Returns:
        --------
        dict: Information about the user's YouTube account, including channel details.

        Raises:
        --------
        HttpError: If the YouTube API call fails.
        """
        try:            

            token = self.youtube_tokens.get_valid_access_token(user_id)
            youtube = build(self.api_service_name, self.api_version, credentials=token)
            
            request = youtube.channels().list(
                part="snippet,statistics",
                mine=True
            )
            response = request.execute()            
            return response["items"][0]
        except HttpError as e:
            logger.error(f"HTTP Error occurred while retrieving account info: {e}")
            raise
        except Exception as e:
            logger.error(f"An unexpected error occurred while retrieving account info: {e}")
            raise    

    def get_user_playlists_list(self, user_id):       
        """
        get_user_playlists(user_id):
        Retrieves a list of YouTube playlists for the authenticated user.
        Returns:
            list: A list of playlists .
        Raises:
            HttpError: If the YouTube API call fails.

        """ 
        try:
            token = self.youtube_tokens.get_valid_access_token(user_id)
                        
            youtube = build(self.api_service_name, self.api_version, credentials=token)
            request = youtube.playlists().list(part="snippet", mine=True)
            response = request.execute()
            return response['items']
        except HttpError as e:
            self.handle_http_error(e)
        except Exception as e:
            logger.error(f"An unexpected error occurred getting playlists: {e}")
            raise YouTubeUnexpectedError(f"An unexpected error occurred: {str(e)}")                    

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
        try:
            token = self.youtube_tokens.get_valid_access_token(user_id)                  
            
            youtube = build(self.api_service_name, self.api_version, credentials=token)               

            request = youtube.playlists().list(part="snippet", id=playlist_id)
            response = request.execute()

            return response

        except HttpError as e:
            self.handle_http_error(e)

        except Exception as e:
            logger.error(f"An unexpected error occurred getting playlist: {e}")
            raise YouTubeUnexpectedError(f"An unexpected error occurred: {str(e)}")

        except HttpError as e:            
            logger.error(f"HTTP Error occurred: {e}")
            raise           
                
    def get_playlist_tracks(self, user_id, playlist_id):   
        """
        get_playlist_tracks(user_id, playlist_id):
        Retrieves the tracks from a specific YouTube playlist.
        Parameters:
        -----------
        playlist_id (str): The ID of the playlist.
        """   
        try:
            token = self.youtube_tokens.get_valid_access_token(user_id)
            
            youtube = build(self.api_service_name, self.api_version, credentials=token)
            request = youtube.playlistItems().list(part="snippet", playlistId=playlist_id)
            response = request.execute()
            return response['items']

        except HttpError as e:
            self.handle_http_error(e)

        except Exception as e:
            logger.error(f"An unexpected error occurred getting playlist tracks: {e}")
            raise YouTubeUnexpectedError(f"An unexpected error occurred: {str(e)}")

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
        
        try:
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
        except HttpError as e:
            self.handle_http_error(e)
        except Exception as e:
            logger.error(f"An unexpected error occurred creating playlist: {e}")
            raise YouTubeUnexpectedError(f"An unexpected error occurred: {str(e)}")

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
        try:
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
        except HttpError as e:
            self.handle_http_error(e)
        except Exception as e:
            logger.error(f"An unexpected error occurred adding tracks playlist: {e}")
            raise YouTubeUnexpectedError(f"An unexpected error occurred: {str(e)}")            


    def search_track(self, user_id, track):
        """
        Search on YouTube with specific filters to get audio-only videos or music tracks.

        Parameters:
        -----------
        user_id (str): The unique identifier of the user.
        query (str): The search query, which includes the song name and artist.

        Returns:
        --------
        dict: YouTube search results.
        """
        try:
            token = self.youtube_tokens.get_valid_access_token(user_id)
            youtube = build(self.api_service_name, self.api_version, credentials=token)  

            track_name, artist = track["track"]["name"], track["track"]['artists'][0]["name"]        

            query = f"{track_name} {artist}"  

            request = youtube.search().list(
                part="snippet",
                q=f"{query}",
                type="video",
                maxResults=1,
                order="relevance",            
            )
            response = request.execute()           

            return response["items"][0]     

        except HttpError as e:
            self.handle_http_error(e)
        except Exception as e:
            logger.error(f"An unexpected error occurred searching track: {e}")
            raise YouTubeUnexpectedError(f"An unexpected error occurred: {str(e)}")        
 
    def handle_http_error(self, error):
        """Handles HTTP errors from YouTube API and raises specific exceptions."""
        if error.resp.status == 401:
            logger.error(f"Authentication error: {error}")
            raise YouTubeAuthenticationError("Authentication with YouTube API failed.")
        elif error.resp.status == 404:
            logger.error(f"Resource not found: {error}")
            raise YouTubeNotFoundError("Requested YouTube resource not found.")
        elif error.resp.status == 403 and 'quota' in str(error):
            logger.error(f"Quota exceeded: {error}")
            raise YouTubeQuotaExceededError("YouTube API quota exceeded.")
        elif error.resp.status == 400:
            logger.error(f"Invalid request: {error}")
            raise YouTubeInvalidRequestError("Invalid request to YouTube API.")
        else:
            logger.error(f"Unexpected HTTP error: {error}")
            raise YouTubeAPIError(f"Unexpected YouTube API error: {error}")
          
