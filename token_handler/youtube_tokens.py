from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import Flow
from connection.youtube_connection import YouTubeAuth
from database.redis_connection import get_redis_connection
from errors.custom_exceptions import NoRefreshTokenError, InvalidTokenError
from datetime import datetime, timedelta

redis = get_redis_connection()

class YouTubeTokenHandler:
    """
    Manages YouTube OAuth tokens, including storing, refreshing, and retrieving access tokens.

    Methods:
    --------
    get_auth_url():
        Returns the authorization URL for YouTube.

    exchange_code_for_tokens(user_id, code):
        Exchanges the OAuth code for tokens and stores them in Redis.

    get_valid_access_token(user_id):
        Retrieves a valid access token for a given user. Refreshes the token if needed.

    refresh_access_token(user_id):
        Refreshes the access token using the stored refresh token.
        Raises:
            NoRefreshTokenError: If no refresh token is found in Redis.
            InvalidTokenError: If refreshing the token fails.

    store_access_token(user_id, token_info):
        Stores access token in Redis.

    store_refresh_token(user_id, token_info):
        Stores refresh token in Redis.    

    revoke_tokens(user_id):
        Deletes the stored tokens for a user from Redis.
    """
    
    def __init__(self):
        self.youtube_auth = YouTubeAuth()
        self.redis_prefix = "youtube_"
    
    def get_auth_url(self):
        return self.youtube_auth.get_auth_url()

    def exchange_code_for_tokens(self, user_id, code):

        """
        Exchanges an authorization code for access and refresh tokens, then stores them.
        
        Parameters:
        -----------
        user_id (str): The ID of the user.
        code (str): The authorization code obtained from the OAuth callback.
        
        Returns:
        --------
        dict: Token information, including access_token and refresh_token.
        """
        token_info = self.youtube_auth.get_token(code)
        self.store_access_token(user_id, token_info)
        self.store_refresh_token(user_id, token_info)        
        return token_info

    def get_valid_access_token(self, user_id):

        """
        Retrieves a valid access token. If expired or unavailable, it refreshes the token.    

        Returns:
        --------
        Credentials: Google OAuth credentials object containing the access token.
        """

        access_token = redis.get(f"{self.redis_prefix}access_token:{user_id}")          

        if not access_token: 
            access_token = self.refresh_access_token(user_id)            

        credentials = Credentials(token=access_token)  

        return credentials

    def refresh_access_token(self, user_id):
        """
        Refreshes the access token using the stored refresh token.
        Raises:
            NoRefreshTokenError: If no refresh token is found in Redis.
            InvalidTokenError: If refreshing the token fails.
        """
        
        refresh_token = redis.get(f"{self.redis_prefix}refresh_token:{user_id}") 
        
        if not refresh_token: raise NoRefreshTokenError()

        try: 
            token_info = self.youtube_auth.refresh_access_token(refresh_token)            
            self.store_access_token(user_id, token_info)               
            try:       
                return token_info.token
            except:
                return token_info["access_token"]
                       
        except InvalidTokenError as e:            
            raise 

    def store_access_token(self, user_id, token_info):   
        """
        Store the user's access token in Redis.
        """
        access_token = token_info["access_token"]       
        redis.setex(f"{self.redis_prefix}access_token:{user_id}", 3600, access_token)        

    def store_refresh_token(self, user_id, token_info):
        """
        Store the user's refresh token in Redis.
        """
        refresh_token = token_info["refresh_token"] 
        redis.set(f"{self.redis_prefix}refresh_token:{user_id}", refresh_token)    
            
    def revoke_tokens(self, user_id):
        # Remove Access Token from Redis and cache
        redis.delete(f"{self.redis_prefix}access_token:{user_id}")
        # Remove Refresh Token from Redis 
        redis.delete(f"{self.redis_prefix}refresh_token:{user_id}")

