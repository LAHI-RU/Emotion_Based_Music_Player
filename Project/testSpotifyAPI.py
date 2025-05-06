import spotipy
from spotipy.oauth2 import SpotifyOAuth
import os

# Clear the .cache file if it exists
if os.path.exists(".cache"):
    os.remove(".cache")
    print("Removed existing cache file")

# Your Spotify API credentials - replace with your actual credentials
CLIENT_ID = "c49fba99aece4be592249af0a17e0a80"
CLIENT_SECRET = "1afe076060d74424ad77f908739b7f33"
REDIRECT_URI = "http://127.0.0.1:8000/callback"

# The scopes determine what permissions your app has
SCOPES = [
    "user-read-playback-state",
    "user-modify-playback-state",
    "user-read-currently-playing",
    "app-remote-control",
    "playlist-read-private",
    "playlist-read-collaborative",
    "playlist-modify-private",
    "playlist-modify-public",
    "user-library-modify",
    "user-library-read",
    "user-read-email",
    "user-read-private"
]

print("Initializing Spotify client with OAuth authentication...")
sp = spotipy.Spotify(
    auth_manager=SpotifyOAuth(
        client_id=CLIENT_ID,
        client_secret=CLIENT_SECRET,
        redirect_uri=REDIRECT_URI,
        scope=" ".join(SCOPES),
        open_browser=True,
        cache_path=".spotify_cache"
    )
)

print("\n--- Testing User Profile ---")
try:
    user_info = sp.current_user()
    print(f"Successfully logged in as: {user_info['display_name']} (ID: {user_info['id']})")
except Exception as e:
    print(f"Error getting user info: {e}")

print("\n--- Testing Device Access ---")
try:
    devices = sp.devices()
    if devices and 'devices' in devices and devices['devices']:
        print("Available devices:")
        for i, device in enumerate(devices['devices']):
            print(f"  {i+1}. {device['name']} ({device['type']}) - ID: {device['id']}")
    else:
        print("No active devices found. Please open Spotify on a device.")
except Exception as e:
    print(f"Error getting devices: {e}")

print("\n--- Testing Playlist Access ---")
try:
    # Get user's playlists instead of a hardcoded one
    results = sp.current_user_playlists(limit=5)
    if results and 'items' in results:
        print(f"Found {len(results['items'])} playlists:")
        for i, playlist in enumerate(results['items']):
            print(f"  {i+1}. {playlist['name']} (ID: {playlist['id']})")
            
            # Try to get tracks from the first playlist
            if i == 0 and playlist['tracks']['total'] > 0:
                print(f"\nAttempting to get tracks from playlist: {playlist['name']}")
                tracks = sp.playlist_tracks(playlist['id'], limit=1)
                if tracks and 'items' in tracks and tracks['items']:
                    track = tracks['items'][0]['track']
                    print(f"Found track: {track['name']} by {track['artists'][0]['name']}")
                else:
                    print("No tracks found in this playlist")
    else:
        print("No playlists found")
except Exception as e:
    print(f"Error accessing playlists: {e}")

print("\n--- Testing Top Tracks ---")
try:
    top_tracks = sp.current_user_top_tracks(limit=5, time_range="short_term")
    if top_tracks and 'items' in top_tracks:
        print(f"Found {len(top_tracks['items'])} top tracks:")
        for i, track in enumerate(top_tracks['items']):
            print(f"  {i+1}. {track['name']} by {track['artists'][0]['name']}")
    else:
        print("No top tracks found")
except Exception as e:
    print(f"Error getting top tracks: {e}")

print("\n--- Testing Recommendations ---")
try:
    # Get recommendations based on genres
    recommendations = sp.recommendations(
        seed_genres=['pop', 'rock'],
        limit=5
    )
    if recommendations and 'tracks' in recommendations:
        print(f"Found {len(recommendations['tracks'])} recommended tracks:")
        for i, track in enumerate(recommendations['tracks']):
            print(f"  {i+1}. {track['name']} by {track['artists'][0]['name']}")
    else:
        print("No recommendations found")
except Exception as e:
    print(f"Error getting recommendations: {e}")

print("\nSpotify API test complete!")