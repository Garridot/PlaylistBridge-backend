import unittest
from unittest.mock import patch, Mock
from services.youtube_service import YouTubeService

class TestYouTubeService(unittest.TestCase):
    def setUp(self):
        """Set up the YouTubeService instance and common test data."""
        self.youtube_service = YouTubeService()
        self.user_id = "test_user"
        self.playlist_id = "test_playlist_id"
        self.video_id = "test_video_id"

    @patch('token_handler.youtube_tokens.YouTubeTokenHandler.get_auth_url')
    def test_get_auth_url(self, mock_get_auth_url):
        """Test that get_auth_url returns the expected authentication URL."""
        mock_get_auth_url.return_value = "https://auth.youtube.com/"

        auth_url = self.youtube_service.get_auth_url()
        
        # Assert that the returned URL matches the mock URL.
        self.assertEqual(auth_url, "https://auth.youtube.com/")
        mock_get_auth_url.assert_called_once()

    @patch('token_handler.youtube_tokens.YouTubeTokenHandler.exchange_code_for_tokens')
    def test_get_token(self, mock_exchange_tokens):
        """Test that get_token retrieves access and refresh tokens."""
        mock_exchange_tokens.return_value = {
            "access_token": "test_token", 
            "refresh_token": "refresh_test_token"
        }
        
        token_info = self.youtube_service.get_token(self.user_id, "auth_code")
        
        # Assert that the correct token information is returned.
        self.assertEqual(token_info, {
            "access_token": "test_token", 
            "refresh_token": "refresh_test_token"
        })
        mock_exchange_tokens.assert_called_once_with(self.user_id, "auth_code")

    @patch('token_handler.youtube_tokens.YouTubeTokenHandler.revoke_tokens')
    def test_logout(self, mock_revoke_tokens):
        """Test that logout calls revoke_tokens with the correct user ID."""
        self.youtube_service.logout(self.user_id)
        
        # Verify that revoke_tokens is called with the correct user ID.
        mock_revoke_tokens.assert_called_once_with(self.user_id)
    
    @patch('services.youtube_service.build')
    @patch('token_handler.youtube_tokens.YouTubeTokenHandler.get_valid_access_token')
    def test_get_playlist(self, mock_get_token, mock_build):
        """Test retrieving a playlist from YouTube API."""
        # Configure mocks for YouTube API response.
        mock_youtube = Mock()
        mock_build.return_value = mock_youtube
        mock_youtube.playlists().list().execute.return_value = {
            "items": [{"snippet": {"title": "Playlist 1", "description": "Description"}}]
        }
        
        playlist = self.youtube_service.get_playlist(self.user_id, self.playlist_id)
        
        # Assert the playlist details match the mock response.
        self.assertEqual(playlist['items'][0]['snippet']['title'], 'Playlist 1')
        self.assertEqual(playlist['items'][0]['snippet']['description'], 'Description')

    @patch('services.youtube_service.build')
    @patch('token_handler.youtube_tokens.YouTubeTokenHandler.get_valid_access_token')
    def test_get_playlist_tracks(self, mock_get_token, mock_build):
        """Test retrieving tracks from a YouTube playlist."""
        # Set up mocks for playlistItems response.
        mock_youtube = Mock()
        mock_build.return_value = mock_youtube
        mock_youtube.playlistItems().list().execute.return_value = {
            "items": [{"snippet": {"title": "Track 1"}}, {"snippet": {"title": "Track 2"}}]
        }
        
        tracks = self.youtube_service.get_playlist_tracks(self.user_id, self.playlist_id)
        
        # Assert the returned tracks match the expected titles.
        self.assertEqual(tracks, [{"snippet": {"title": "Track 1"}}, {"snippet": {"title": "Track 2"}}])

    @patch('services.youtube_service.build')
    @patch('token_handler.youtube_tokens.YouTubeTokenHandler.get_valid_access_token')
    def test_create_playlist(self, mock_get_token, mock_build):
        """Test creating a new YouTube playlist."""
        mock_youtube = Mock()
        mock_build.return_value = mock_youtube
        mock_youtube.playlists().insert().execute.return_value = {
            "id": "new_playlist_id",
            "snippet": {"title": "New Playlist"}
        }
        
        playlist = self.youtube_service.create_playlist(self.user_id, "New Playlist", "A description")
        
        # Assert the playlist ID and title match the mock response.
        self.assertEqual(playlist["id"], "new_playlist_id")
        self.assertEqual(playlist["snippet"]["title"], "New Playlist")

    @patch('services.youtube_service.build')
    @patch('token_handler.youtube_tokens.YouTubeTokenHandler.get_valid_access_token')
    def test_add_track_to_playlist(self, mock_get_token, mock_build):
        """Test adding a video to an existing YouTube playlist."""
        mock_youtube = Mock()
        mock_build.return_value = mock_youtube
        mock_youtube.playlistItems().insert().execute.return_value = {
            "snippet": {"title": "Video Title", "playlistId": self.playlist_id}
        }
        
        response = self.youtube_service.add_track_to_playlist(self.user_id, self.playlist_id, self.video_id)
        
        # Assert the video details match the mock response.
        self.assertEqual(response["snippet"]["playlistId"], self.playlist_id)
        self.assertEqual(response["snippet"]["title"], "Video Title")

if __name__ == '__main__':
    unittest.main() 

