from unittest import TestCase
from unittest.mock import patch, MagicMock
from services.playlist_migration_service import PlaylistMigration
from services.spotify_service import SpotifyService
from services.youtube_service import YouTubeService
from errors.playlist_exceptions import APIRequestError, PlaylistNotFoundError, AuthenticationError

class TestPlaylistMigration(TestCase):
    def setUp(self):
        self.spotify_service = MagicMock(spec=SpotifyService)
        self.youtube_service = MagicMock(spec=YouTubeService)
        
        # Configura los mocks
        self.youtube_service.get_playlist = MagicMock()
        self.youtube_service.get_playlist_tracks = MagicMock()
        self.spotify_service.create_playlist = MagicMock()
        self.spotify_service.search_and_buffer_tracks = MagicMock()
        self.spotify_service.add_track_to_playlist = MagicMock()
        
        self.playlist_migration = PlaylistMigration(
            spotify_service=self.spotify_service,
            youtube_service=self.youtube_service
        )
        self.current_user = MagicMock()

    @patch('token_handler.spotify_tokens.SpotifyTokenHandler.get_access_token', return_value="fake_spotify_token")
    @patch('token_handler.spotify_tokens.SpotifyTokenHandler.refresh_token', return_value="fake_spotify_token")
    @patch('token_handler.youtube_tokens.YouTubeTokenHandler.get_valid_access_token', return_value="fake_youtube_token")
    @patch('token_handler.youtube_tokens.YouTubeTokenHandler.refresh_access_token', return_value="fake_youtube_token")
    def test_migrate_spotify_to_youtube_success(self, mock_youtube_token, mock_youtube_refresh, mock_spotify_token, mock_spotify_refresh):
        # Configura los mocks para simular los resultados esperados de las APIs
        self.spotify_service.get_playlist.return_value = {"name": "Test Playlist"}
        self.spotify_service.get_playlist_tracks.return_value = [
            {"track": {"name": "Song1", "artists": [{"name": "Artist1"}]}}
        ]
        self.youtube_service.create_playlist.return_value = "youtube_playlist_id"
        self.youtube_service.search_and_buffer_tracks.return_value = [
            {"track": {"name": "Song1", "artists": [{"name": "Artist1"}]}}
        ]

        # Llamada a la función de migración y verificación
        result = self.playlist_migration.migrate_spotify_to_youtube(self.current_user, "spotify_playlist_id")
        self.assertEqual(result, "youtube_playlist_id")

    @patch('token_handler.spotify_tokens.SpotifyTokenHandler.get_access_token', return_value="fake_spotify_token")
    @patch('token_handler.spotify_tokens.SpotifyTokenHandler.refresh_token', return_value="fake_spotify_token")
    @patch('token_handler.youtube_tokens.YouTubeTokenHandler.get_valid_access_token', return_value="fake_youtube_token")
    @patch('token_handler.youtube_tokens.YouTubeTokenHandler.refresh_access_token', return_value="fake_youtube_token")
    def test_migrate_youtube_to_spotify_success(self, mock_youtube_token, mock_youtube_refresh, mock_spotify_token, mock_spotify_refresh):
        # Configura los mocks para simular los resultados esperados de las APIs
        self.youtube_service.get_playlist.return_value = {"snippet":{"title": "Test Playlist"}}
        self.youtube_service.get_playlist_tracks.return_value = [
            {"track": {"name": "Song1", "artists": [{"name": "Artist1"}]}}
        ]
        self.spotify_service.create_playlist.return_value = "youtube_playlist_id"
        self.spotify_service.batch_search_tracks.return_value = [
            {"track": {"name": "Song1", "artists": [{"name": "Artist1"}]}}
        ]

        # Llamada a la función de migración y verificación
        result = self.playlist_migration.migrate_youtube_to_spotify(self.current_user, "spotify_playlist_id")
        self.assertEqual(result, "youtube_playlist_id")   

