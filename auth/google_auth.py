from models.users import User  # Suponiendo que tienes un modelo User
from token_handler.auth_tokens import generate_access_token, generate_refresh_token
from connection.google_connection import GoogleAuth
from database.db_connection import db


def google_auth_user(user_info):  
    """
    Authenticate or register a user using Google authentication.

    This function checks if a user with the provided Google email already exists
    in the database. If not, it creates a new user account flagged as authenticated
    via Google. Afterward, it generates and returns an access token and a refresh
    token for the user.

    Parameters:
    ----------
    user_info : dict
        A dictionary containing user information retrieved from Google, 
        primarily containing the user's email address.

    Returns:
    -------
    dict
        A dictionary containing:
        - 'access_token': JWT access token for authenticated access.
        - 'refresh_token': JWT refresh token for maintaining the session.
        - 'user': Original `user_info` provided for reference.  
    """
    
    # check if the user already exists in the database.
    user = User.query.filter_by(email=user_info['email']).first()
    
    if not user: # create new user if it does not exist.

        user = User(
            email=user_info['email'],
            is_google_auth=True, # indicate that Google authenticates the user.    
        )         

        # save the user in the database.
        db.session.add(user)
        db.session.commit()
    
    # generate Access Token and Refresh Token for the user.
    access_token = generate_access_token(user.id)
    refresh_token = generate_refresh_token(user.id)

    return {
        'access_token': access_token,
        'refresh_token': refresh_token,
        'user': user_info
    }
