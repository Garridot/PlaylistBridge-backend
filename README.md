
# PlaylistBridge

PlaylistBridge is a web application that allows users to seamlessly migrate and share playlists between Spotify and YouTube Music. The project automates authentication and token management, and facilitates the synchronization of playlists across platforms, providing a unified experience for playlist management.

## Features

- **Authentication with Spotify and YouTube**: Users can log in with their Spotify and YouTube accounts using OAuth2.
- **Playlist Migration**: Easily transfer playlists from Spotify to YouTube and vice versa.
- **Playlist Sharing**: Share playlists across platforms in real-time.
- **Token Management**: Secure handling and refreshing of access tokens and refresh tokens using Redis.
- **Scalability**: The project is structured to be scalable with modularized services for authentication, token management, and playlist handling.

## Project Structure

The project follows a modular architecture divided into key layers for better organization and scalability:

- **Controllers**: Handle HTTP requests and routing.
- **Services**: Manage business logic (e.g., retrieving playlists, managing tokens).
- **Connection**: Manages API connections for authentication (Spotify and YouTube).
- **Token Handlers**: Automates token storage and refresh processes for both platforms.

### Main Modules

#### 1. Spotify Authentication and Token Management
- **Authentication**: Users authenticate with Spotify via OAuth2.
- **Token Handling**: The system stores and refreshes tokens securely using Redis.
- **Services**: After authentication, users can fetch playlists and tracks from their Spotify account.

#### 2. YouTube Authentication and Token Management
- **Authentication**: Users authenticate with YouTube via OAuth2.
- **Token Handling**: Similar to Spotify, tokens are stored and refreshed automatically.
- **Services**: Once authenticated, users can retrieve and manage their YouTube playlists.

## Workflow

1. **Authentication**:
   - Users authenticate with either Spotify or YouTube using OAuth2.
   - Tokens are securely stored in Redis for future API requests.

2. **Token Automation**:
   - Tokens are automatically refreshed when expired.
   - Both access tokens and refresh tokens are handled efficiently using a memory cache and Redis for storage.

3. **Playlist Management**:
   - Users can fetch their playlists and tracks from either Spotify or YouTube.
   - Playlists can be migrated between platforms.

4. **Error Handling**:
   - Custom exceptions are raised for invalid or missing tokens.
   - A decorator is used to handle token-related errors in a centralized manner.

## Installation

1. Clone the repository:
```bash
git clone https://github.com/your-username/playlistbridge.git
```
2. Install dependencies:
```bash
pip install -r requirements.txt
```
3. Set up environment variables in a .env file or use Config class:
```bash
SPOTIFY_CLIENT_ID=your_spotify_client_id
SPOTIFY_CLIENT_SECRET=your_spotify_client_secret
SPOTIFY_REDIRECT_URI=your_spotify_redirect_uri
YOUTUBE_CLIENT_ID=your_youtube_client_id
YOUTUBE_CLIENT_SECRET=your_youtube_client_secret
YOUTUBE_REDIRECT_URI=your_youtube_redirect_uri
```
4. Run the application:
```bash
python app.py   
```
## API Endpoints

### Spotify
- **GET /auth/login:** Redirects user to Spotify login page.
- **GET /auth/callback:** Handles Spotify callback and stores tokens.
- **GET /auth/logout:** Revokes Spotify access and refresh tokens.
- **GET /playlists:** Retrieves user playlists from Spotify.
- **GET /playlists/<playlist_id>/tracks:** Retrieves tracks from a specific Spotify playlist.

### YouTube
- **GET /auth/login:** Redirects user to YouTube login page.
- **GET /auth/callback:** Handles YouTube callback and stores tokens.
- **GET /auth/logout:** Revokes YouTube access and refresh tokens.
- **GET /playlists:** Retrieves user playlists from YouTube.
- **GET /playlists/<playlist_id>/tracks:** Retrieves tracks from a specific YouTube playlist.

## Technologies Used
- **Flask:** Backend framework for API development.
- **Spotipy:** Python library for Spotify API integration.
- **Google API Client:** Handles YouTube API integration.
- **Redis:** Used for token storage and caching.
- **PostgreSQL:** For storing structured data (e.g., playlists, user data).
- **OAuth2:** For secure user authentication with Spotify and YouTube.

##  Future Enhancements
- **Cross-platform Playlist Sync:** Automatically sync playlists between platforms based on user settings.
- **Mobile and Desktop Versions:** Extend the application to mobile and desktop platforms.
- **Enhanced Error Handling:** Improve error handling for API request failures.



