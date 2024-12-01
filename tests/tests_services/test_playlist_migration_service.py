from unittest import TestCase
from unittest.mock import patch, MagicMock
from services.playlist_migration_service import PlaylistMigration
from services.spotify_service import SpotifyService
from services.youtube_service import YouTubeService
from errors.playlist_exceptions import APIRequestError, PlaylistNotFoundError, AuthenticationError, TrackNotFoundError

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
    @patch('token_handler.youtube_tokens.YouTubeTokenHandler.get_valid_access_token', return_value="fake_youtube_token")
    def test_playlist_not_found_youtube(self, mock_youtube_token, mock_spotify_token):
        # Configura el mock para que lance una excepción PlaylistNotFoundError
        self.youtube_service.get_playlist.side_effect = PlaylistNotFoundError("Playlist not found on YouTube")

        with self.assertRaises(PlaylistNotFoundError):
            self.playlist_migration.migrate_youtube_to_spotify(self.current_user, "nonexistent_playlist_id")

    @patch('token_handler.spotify_tokens.SpotifyTokenHandler.get_access_token', return_value="fake_spotify_token")
    @patch('token_handler.youtube_tokens.YouTubeTokenHandler.get_valid_access_token', return_value="fake_youtube_token")
    def test_playlist_not_found_spotify(self, mock_youtube_token, mock_spotify_token):
        # Configura el mock para que lance una excepción PlaylistNotFoundError
        self.spotify_service.get_playlist.side_effect = PlaylistNotFoundError("Playlist not found on Spotify")

        with self.assertRaises(PlaylistNotFoundError):
            self.playlist_migration.migrate_spotify_to_youtube(self.current_user, "nonexistent_playlist_id")


        @patch('token_handler.spotify_tokens.SpotifyTokenHandler.get_access_token', return_value="fake_spotify_token")
        @patch('token_handler.youtube_tokens.YouTubeTokenHandler.get_valid_access_token', return_value="fake_youtube_token")
        def test_migrate_spotify_to_youtube(self, mock_youtube_token, mock_spotify_token):
            # Configura los mocks para simular una playlist válida en Spotify
            self.spotify_service.get_playlist.return_value = {"name": "Test Playlist"}
            self.spotify_service.get_playlist_tracks.return_value = [
                {"track": {"name": "Song1", "artists": [{"name": "Artist1"}]}},
                {"track": {"name": "Song2", "artists": [{"name": "Artist2"}]}}
            ]
            self.youtube_service.create_playlist.return_value = "youtube_playlist_id"

            # Simula que Song2 no fue encontrada debido a los filtros
            self.youtube_service.search_and_buffer_tracks.return_value = [
                {"snippet": {"title": "Song1", "channelTitle": "Artist1"}}
            ]

            # Llamada a la función de migración y verificación
            result = self.playlist_migration.migrate_spotify_to_youtube(self.current_user, "spotify_playlist_id")
            
            # Verifica el ID de la playlist creada
            self.assertEqual(result["youtube_playlist_id"], "youtube_playlist_id")
            
            # Verifica el estado de las canciones migradas
            self.assertEqual(result["tracks_migrated"], [
                {"track": "Song1", "artist": "Artist1", "found": True},
                {"track": "Song2", "artist": "Artist2", "found": False}
            ])
  

        @patch('token_handler.spotify_tokens.SpotifyTokenHandler.get_access_token', return_value="fake_spotify_token")
        @patch('token_handler.youtube_tokens.YouTubeTokenHandler.get_valid_access_token', return_value="fake_youtube_token")
        def test_migrate_spotify_to_youtube_no_tracks_found(self, mock_youtube_token, mock_spotify_token):
            # Configura los mocks para simular una playlist válida en Spotify
            self.spotify_service.get_playlist.return_value = {"name": "Test Playlist"}
            self.spotify_service.get_playlist_tracks.return_value = [
                {"track": {"name": "Song1", "artists": [{"name": "Artist1"}]}}
            ]
            self.youtube_service.create_playlist.return_value = "youtube_playlist_id"

            # Simula que no se encontraron tracks en YouTube
            self.youtube_service.search_and_buffer_tracks.return_value = []

            # Llamada a la función de migración y verificación
            result = self.playlist_migration.migrate_spotify_to_youtube(self.current_user, "spotify_playlist_id")
            
            # Verifica el ID de la playlist creada
            self.assertEqual(result["youtube_playlist_id"], "youtube_playlist_id")
            
            # Verifica el estado de las canciones migradas
            self.assertEqual(result["tracks_migrated"], [
                {"track": "Song1", "artist": "Artist1", "found": False},
            ])


