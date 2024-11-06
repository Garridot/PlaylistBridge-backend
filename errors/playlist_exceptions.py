class PlaylistNotFoundError(Exception):
    """Raised when the playlist is not found in the source platform."""
    def __init__(self, message="Playlist not found in the source platform."):
        self.message = message
        super().__init__(self.message)


class TrackNotFoundError(Exception):
    """Raised when a track cannot be found in the destination platform."""
    def __init__(self, message="Track not found in the destination platform."):
        self.message = message
        super().__init__(self.message)


class AuthenticationError(Exception):
    """Raised when there is an authentication problem with the platform's API."""
    def __init__(self, message="Authentication failed. Please check your credentials."):
        self.message = message
        super().__init__(self.message)


class APIRequestError(Exception):
    """Raised when an error occurs while making a request to the API."""
    def __init__(self, message="API request error. Please try again later."):
        self.message = message
        super().__init__(self.message)


class InvalidPlatformError(Exception):
    """Raised when the source or destination platform is invalid."""
    def __init__(self, message="Invalid source or destination platform."):
        self.message = message
        super().__init__(self.message)

class InvalidPlaylistIDError(Exception):
    """Raised when a Spotify playlist ID is not in the valid base62 format."""
    def __init__(self, message="API request error. Playlist ID is not in the valid base62 format."):
        self.message = message
        super().__init__(self.message)
