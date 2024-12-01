import unittest
from unittest.mock import patch, MagicMock
from token_handler.youtube_tokens import YouTubeTokenHandler
from errors.custom_exceptions import NoRefreshTokenError, InvalidTokenError
from google.oauth2.credentials import Credentials

class TestYouTubeTokenHandler(unittest.TestCase):

    def setUp(self):
        self.token_handler = YouTubeTokenHandler()
        self.user_id = "test_user"

    @patch('database.redis_connection.get_redis_connection')
    def test_get_valid_access_token_cached(self, mock_redis):
        # Simular un token de acceso en Redis
        mock_redis.return_value.get.return_value = b'cached_access_token'
        
        token = self.token_handler.get_valid_access_token(self.user_id)
        
        # Verificar que se devolvió un objeto de tipo Credentials con el token correcto
        self.assertIsInstance(token, Credentials)
        self.assertEqual(token.token, 'cached_access_token')

    @patch('database.redis_connection.get_redis_connection')
    @patch('youtube_token_handler.YouTubeAuth.refresh_access_token')
    def test_get_valid_access_token_refresh(self, mock_refresh_access_token, mock_redis):
        # Simular la ausencia de un token de acceso en Redis y la presencia de un refresh token
        mock_redis.return_value.get.side_effect = [None, b'refresh_token']
        mock_refresh_access_token.return_value = {
            'access_token': 'new_access_token',
            'refresh_token': 'new_refresh_token'
        }
        
        token = self.token_handler.get_valid_access_token(self.user_id)
        
        # Verificar que se devolvió un objeto de tipo Credentials con el nuevo token
        self.assertIsInstance(token, Credentials)
        self.assertEqual(token.token, 'new_access_token')

    @patch('database.redis_connection.get_redis_connection')
    def test_get_valid_access_token_no_refresh_token(self, mock_redis):
        # Simular la ausencia de tokens en Redis
        mock_redis.return_value.get.side_effect = [None, None]

        with self.assertRaises(NoRefreshTokenError):
            self.token_handler.get_valid_access_token(self.user_id)

    @patch('database.redis_connection.get_redis_connection')
    @patch('youtube_token_handler.YouTubeAuth.refresh_access_token')
    def test_refresh_access_token_invalid_token(self, mock_refresh_access_token, mock_redis):
        # Simular la presencia de un refresh token en Redis
        mock_redis.return_value.get.return_value = b'refresh_token'
        # Simular una excepción al refrescar el token
        mock_refresh_access_token.side_effect = Exception("Invalid token")

        with self.assertRaises(InvalidTokenError):
            self.token_handler.refresh_access_token(self.user_id)

    @patch('database.redis_connection.get_redis_connection')
    def test_store_tokens(self, mock_redis):
        # Simular la conexión de Redis
        token_info = {
            'access_token': 'test_access_token',
            'refresh_token': 'test_refresh_token',
            'expires_in': 3600
        }

        self.token_handler.store_tokens(self.user_id, token_info)

        # Verificar que Redis almacenó el token correctamente
        mock_redis.return_value.set.assert_any_call(
            f"youtube_access_token:{self.user_id}", 'test_access_token', ex=3600
        )
        mock_redis.return_value.set.assert_any_call(
            f"youtube_refresh_token:{self.user_id}", 'test_refresh_token'
        )

if __name__ == '__main__':
    unittest.main()
