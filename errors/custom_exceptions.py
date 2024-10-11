class TokenError(Exception):
    def __init__(self, message, status_code=400):
        super().__init__(message)
        self.message = message
        self.status_code = status_code

class NoRefreshTokenError(TokenError):
    def __init__(self):
        super().__init__("No refresh token found for this user.", status_code=401)

class InvalidTokenError(TokenError):
    def __init__(self):
        super().__init__("Invalid or expired access token.", status_code=401)
