class TokenError(Exception):
    """
    Base class for token-related exceptions.

    This class provides a foundation for all custom exceptions related to token handling, 
    allowing for a standardized error message and status code. By default, it returns a 
    400 status code, which can be customized in derived classes.

    Parameters:
    ----------
    message : str
        A description of the error that occurred.
    status_code : int, optional
        HTTP status code associated with the error (default is 400).

    Attributes:
    ----------
    message : str
        Error message describing the exception.
    status_code : int
        HTTP status code indicating the error type.
    """
    def __init__(self, message, status_code=400):
        super().__init__(message)
        self.message = message
        self.status_code = status_code

class NoRefreshTokenError(TokenError):
    """
    Exception raised when a required refresh token is not found for the user.

    This exception is used to indicate the absence of a refresh token, signaling 
    that the user must re-authenticate. It returns a 401 status code by default.

    Inherits:
    --------
    TokenError : Base class for token-related exceptions.

    Usage:
    ------
    raise NoRefreshTokenError()
    """
    def __init__(self):
        super().__init__("No refresh token found for this user.", status_code=401)

class InvalidTokenError(TokenError):
    """
    Exception raised when an access token is invalid or has expired.

    This exception is used to indicate that the provided access token is either 
    malformed or no longer valid, prompting the user to refresh their token. 
    It returns a 401 status code by default.

    Inherits:
    --------
    TokenError : Base class for token-related exceptions.

    Usage:
    ------
    raise InvalidTokenError()
    """
    def __init__(self):
        super().__init__("Invalid or expired access token.", status_code=401)