from connection.spotify_connection import SpotifyAuth
from database.redis_connection import get_redis_connection
from datetime import datetime, timedelta
from errors.custom_exceptions import NoRefreshTokenError, InvalidTokenError
import logging
logger = logging.getLogger(__name__)

redis = get_redis_connection()

 
class SpotifyTokenHandler:
    """
    Manages Spotify access and refresh tokens using Redis and in-memory caching.  

    Methods:
    --------
    stored_access_token(user_id: str, token_info: dict):
        Stores the access token in Redis and in-memory cache.
    
    stored_refresh_token(user_id: str, token_info: dict):
        Stores the refresh token in Redis.
    
    get_access_token(user_id: str) -> str:
        Retrieves the access token, either from memory cache or Redis, and refreshes it if expired.
    
    refresh_token(user_id: str) -> str:
        Uses the refresh token to obtain a new access token and updates the stored tokens.
    
    revoke_access_token(user_id: str):
        Deletes the access token from Redis and memory cache.
    
    revoke_refresh_token(user_id: str):
        Deletes the refresh token from Redis.  
    """

    def __init__(self):
        """
        Initializes the SpotifyAuth object and sets up access to Spotify API via Spotipy.
        """
        self.spotify_auth = SpotifyAuth()        

    def stored_access_token(self, user_id, token_info):
        """
        This method stores the user's access token in Redis and also caches it in memory for faster access.
        
        Parameters:
        --------
        user_id (str): The unique user identifier.
        token_info (dict): A dictionary containing the access token and its expiration information.
        """
        access_token = token_info['access_token']
        expires_in = token_info['expires_in']

        # convert timedelta to seconds
        expiration_time_in_seconds = timedelta(seconds=expires_in).total_seconds()

        # store the access token in Redis
        redis.setex(f"spotify_access_token:{user_id}", int(expiration_time_in_seconds), access_token)        

        logger.info(f"Access token stored for user {user_id}: {redis.get(f'spotify_access_token:{user_id}')}")
    

    def stored_refresh_token(self, user_id, token_info):
        """
        Stores the refresh token in Redis for the specified user.
        
        Parameters:
        --------
        user_id (str): The unique user identifier.
        token_info (dict): A dictionary containing the access token and its expiration information.
        """        
        refresh_token = token_info['refresh_token']        
        # store the refresh token in Redis
        redis.set(f"spotify_refresh_token:{user_id}", refresh_token)       
    
    
    def get_access_token(self, user_id):
        """
        Retrieves the access token from memory cache or Redis. If it has expired, it refreshes the token using the refresh token.
        
        Parameters:
        --------
        user_id (str): The unique user identifier.

        Returns: 
        --------
        The new access token as a string.
        """
        
        access_token = redis.get(f"spotify_access_token:{user_id}")        

        if not access_token:
            # if the token is not in Redis, refresh it           
            access_token = self.refresh_token(user_id)      

        return access_token

    def refresh_token(self, user_id):
        """
        Uses the refresh token to generate a new access token and updates both the access and refresh tokens in Redis and memory.
        
        Parameters:
        --------
        user_id (str): The unique user identifier. 
        
        Returns: 
        --------
        The new access token as a string.
        """ 
        refresh_token = redis.get(f"spotify_refresh_token:{user_id}")        

        if not refresh_token:
            raise NoRefreshTokenError()

        try:
            token_info = self.spotify_auth.sp_oauth.refresh_access_token(refresh_token)
        except Exception as e:
            raise InvalidTokenError()       

        # Store the new access token and update the refresh token if necessary
        self.stored_access_token(user_id, token_info)
        self.stored_refresh_token(user_id, token_info)

        return token_info['access_token']    

    def revoke_access_token(self, user_id):
        """
        Deletes the access token from Redis for the specified user.
        
        Parameters:
        --------
        user_id (str): The unique user identifier.        
        """
        redis.delete(f"spotify_access_token:{user_id}")          
        
    
    def revoke_refresh_token(self, user_id):
        """
        Deletes the refresh token from Redis for the specified user.
        
        Parameters:
        --------
        user_id (str): The unique user identifier.        
        """  
        redis.delete(f"spotify_refresh_token:{user_id}")
        
        

    
            
            
