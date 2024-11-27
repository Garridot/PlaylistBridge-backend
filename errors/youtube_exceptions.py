class YouTubeAPIError(Exception):
    """Base class for YouTube API errors."""
    pass


class YouTubeAuthenticationError(YouTubeAPIError):
    """Raised when there is an authentication issue with YouTube API."""
    pass

class YouTubeNotFoundError(YouTubeAPIError):
    """Raised when a requested YouTube resource is not found."""
    pass

class YouTubeQuotaExceededError(YouTubeAPIError):
    """Raised when YouTube API quota limit is exceeded."""
    pass

class YouTubeInvalidRequestError(YouTubeAPIError):
    """Raised for invalid requests to YouTube API."""
    pass

class YouTubeUnexpectedError(YouTubeAPIError):
    """Raised for any unexpected YouTube API errors."""
    pass