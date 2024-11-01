import unittest
from unittest.mock import patch, Mock
from services.spotify_service import SpotifyService
from errors.custom_exceptions import NoRefreshTokenError
from errors.playlist_exceptions import  PlaylistNotFoundError, TrackNotFoundError

class TestSpotifyService(unittest.TestCase):
    def setUp(self):
        """Set up SpotifyService instance and common test data."""
        self.spotify_service = SpotifyService()
        self.user_id = "test_user"
        self.playlist_id = "test_playlist_id"
        self.track_name = "test_track"
        self.artist_name = "test_artist"
        self.mock_spotify_client = Mock()

    @patch('services.spotify_service.SpotifyTokenHandler.get_access_token')
    @patch('spotipy.Spotify')
    def test_get_user_playlists(self, mock_spotify, mock_get_access_token):
        """Test retrieving the user's playlists."""
        # Set up mock token and Spotify client response
        mock_get_access_token.return_value = "valid_token"
        mock_spotify.return_value = self.mock_spotify_client
        self.mock_spotify_client.current_user_playlists.return_value = {
            "items": [{"name": "Playlist 1"}, {"name": "Playlist 2"}]
        }

        playlists = self.spotify_service.get_user_playlists(self.user_id)

        # Assert playlists match the mock data
        self.assertEqual(len(playlists), 2)
        self.assertEqual(playlists[0]["name"], "Playlist 1")
        mock_get_access_token.assert_called_once_with(self.user_id)

    @patch('services.spotify_service.SpotifyTokenHandler.get_access_token')
    @patch('spotipy.Spotify')
    def test_get_playlist(self, mock_spotify, mock_get_access_token):
        """Test retrieving a specific playlist by ID."""
        mock_get_access_token.return_value = "valid_token"
        mock_spotify.return_value = self.mock_spotify_client
        self.mock_spotify_client.playlist.return_value = {
            "name": "My Playlist",
            "description": "A test playlist",
            "tracks": {"items": [{"track": {"name": "Song 1"}}, {"track": {"name": "Song 2"}}]}
        }

        playlist = self.spotify_service.get_playlist(self.user_id, self.playlist_id)

        # Assert playlist data matches the mock response
        self.assertEqual(playlist["name"], "My Playlist")
        self.assertEqual(playlist["description"], "A test playlist")
        self.assertEqual(len(playlist["tracks"]), 2)
        mock_get_access_token.assert_called_once_with(self.user_id)

    @patch('services.spotify_service.SpotifyTokenHandler.get_access_token')
    @patch('spotipy.Spotify')
    def test_get_playlist_tracks(self, mock_spotify, mock_get_access_token):
        """Test retrieving tracks from a playlist."""
        mock_get_access_token.return_value = "valid_token"
        mock_spotify.return_value = self.mock_spotify_client
        self.mock_spotify_client.playlist_tracks.return_value = {
            "items": [{"track": {"name": "Track 1"}}, {"track": {"name": "Track 2"}}]
        }

        tracks = self.spotify_service.get_playlist_tracks(self.user_id, self.playlist_id)

        # Assert tracks match the mock response
        self.assertEqual(len(tracks), 2)
        self.assertEqual(tracks[0]["track"]["name"], "Track 1")
        mock_get_access_token.assert_called_once_with(self.user_id)

    @patch('services.spotify_service.SpotifyTokenHandler.get_access_token')
    @patch('spotipy.Spotify')
    def test_create_playlist(self, mock_spotify, mock_get_access_token):
        """Test creating a new playlist."""
        mock_get_access_token.return_value = "valid_token"
        mock_spotify.return_value = self.mock_spotify_client
        self.mock_spotify_client.user_playlist_create.return_value = {"id": "new_playlist_id"}

        playlist_id = self.spotify_service.create_playlist(self.user_id, "New Playlist")

        # Assert that playlist ID matches the mock response
        self.assertEqual(playlist_id, "new_playlist_id")
        mock_get_access_token.assert_called_once_with(self.user_id)

    @patch('services.spotify_service.SpotifyTokenHandler.get_access_token')
    @patch('spotipy.Spotify')
    def test_add_track_to_playlist(self, mock_spotify, mock_get_access_token):
        """Test adding a track to a playlist by searching for the track."""
        mock_get_access_token.return_value = "valid_token"
        mock_spotify.return_value = self.mock_spotify_client
        # Mock the search and playlist addition responses
        self.mock_spotify_client.search.return_value = {
            "tracks": {"items": [{"id": "track_id_1"}]}
        }
        self.mock_spotify_client.playlist_add_items.return_value = {}

        self.spotify_service.add_track_to_playlist(self.user_id, self.playlist_id, self.track_name, self.artist_name)

        # Check that search and playlist addition were called with the correct parameters
        self.mock_spotify_client.search.assert_called_once_with(q=f"track:{self.track_name} artist:{self.artist_name}", type='track', limit=1)
        self.mock_spotify_client.playlist_add_items.assert_called_once_with(self.playlist_id, ["track_id_1"])

    @patch('services.spotify_service.SpotifyTokenHandler.get_access_token')
    @patch('spotipy.Spotify')
    def test_add_track_to_playlist_not_found(self, mock_spotify, mock_get_access_token):
        """Test adding a track to a playlist when the track is not found on Spotify."""
        mock_get_access_token.return_value = "valid_token"
        mock_spotify.return_value = self.mock_spotify_client
        # Mock search response to return no tracks
        self.mock_spotify_client.search.return_value = {"tracks": {"items": []}}

        with self.assertRaises(TrackNotFoundError):
            self.spotify_service.add_track_to_playlist(self.user_id, self.playlist_id, self.track_name, self.artist_name)

        # Verify that search was called with the correct query
        self.mock_spotify_client.search.assert_called_once_with(q=f"track:{self.track_name} artist:{self.artist_name}", type='track', limit=1)

    @patch('services.spotify_service.SpotifyTokenHandler.get_access_token')
    def test_no_refresh_token_error(self, mock_get_access_token):
        """Test handling of NoRefreshTokenError if no valid token is retrieved."""
        mock_get_access_token.return_value = None  # Simulate no token scenario

        with self.assertRaises(NoRefreshTokenError):
            self.spotify_service.get_user_playlists(self.user_id)

if __name__ == '__main__':
    unittest.main()

