import spotipy

class SpotifyService:
    def get_user_playlists(self, token):
        sp = spotipy.Spotify(auth=token)
        playlists = sp.current_user_playlists(limit=10)
        return playlists['items']

    def get_playlist_tracks(self, token, playlist_id):
        sp = spotipy.Spotify(auth=token)
        tracks = sp.playlist_tracks(playlist_id)
        return tracks['items']