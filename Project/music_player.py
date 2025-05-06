import spotipy
from spotipy.oauth2 import SpotifyOAuth, SpotifyClientCredentials
import random
import time
import os

class MusicPlayer:
    def __init__(self, client_id, client_secret, redirect_uri):
        # Define all necessary scopes
        self.scopes = [
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
        
        # Clear any existing cache
        if os.path.exists(".spotify_cache"):
            try:
                os.remove(".spotify_cache")
                print("Removed existing Spotify cache file")
            except:
                pass
        
        # First, try the OAuth flow which allows playback control
        try:
            print("Authenticating with Spotify using OAuth...")
            self.sp = spotipy.Spotify(
                auth_manager=SpotifyOAuth(
                    client_id=client_id,
                    client_secret=client_secret,
                    redirect_uri=redirect_uri,
                    scope=" ".join(self.scopes),
                    cache_path=".spotify_cache",
                    open_browser=True
                )
            )
            # Test the connection
            user = self.sp.current_user()
            print(f"Successfully authenticated as: {user['display_name']}")
            self.playback_available = True
            self.user_id = user['id']
        except Exception as e:
            print(f"OAuth authentication failed: {e}")
            print("Falling back to Client Credentials flow (no playback control)...")
            # Fall back to Client Credentials flow (no playback control)
            try:
                self.sp = spotipy.Spotify(
                    auth_manager=SpotifyClientCredentials(
                        client_id=client_id,
                        client_secret=client_secret
                    )
                )
                print("Successfully authenticated with Spotify using Client Credentials")
                self.playback_available = False
                self.user_id = None
            except Exception as e:
                print(f"Client Credentials authentication failed: {e}")
                self.sp = None
                self.playback_available = False
                self.user_id = None
        
        # Emotion to audio features mapping for recommendations
        self.emotion_features = {
            "angry": {"valence": 0.2, "energy": 0.8, "tempo": 140},
            "disgust": {"valence": 0.2, "energy": 0.6, "tempo": 120},
            "fear": {"valence": 0.3, "energy": 0.7, "tempo": 130},
            "happy": {"valence": 0.8, "energy": 0.7, "tempo": 120},
            "sad": {"valence": 0.2, "energy": 0.3, "tempo": 90},
            "surprise": {"valence": 0.6, "energy": 0.8, "tempo": 135},
            "neutral": {"valence": 0.5, "energy": 0.5, "tempo": 110}
        }
        
        # Define genre seeds for each emotion
        self.emotion_genres = {
            "angry": ["metal", "hard-rock", "punk"],
            "disgust": ["industrial", "metal", "goth"],
            "fear": ["ambient", "atmospheric", "industrial"],
            "happy": ["pop", "dance", "disco", "edm"],
            "sad": ["sad", "acoustic", "piano", "indie"],
            "surprise": ["edm", "electronic", "dubstep"],
            "neutral": ["pop", "rock", "indie"]
        }
        
        # Initialize user playlists
        self.user_playlists = {}
        self.load_user_playlists()
    
    def load_user_playlists(self):
        """Load and categorize user playlists for emotions"""
        if self.sp is None or self.user_id is None:
            print("Cannot load playlists: Spotify client not fully initialized")
            return
            
        try:
            print("Loading user playlists...")
            results = self.sp.current_user_playlists(limit=50)
            
            if not results or 'items' not in results or not results['items']:
                print("No playlists found")
                return
                
            # Simple keyword matching to categorize playlists by emotion
            emotion_keywords = {
                "angry": ["angry", "rage", "metal", "hard", "intense"],
                "disgust": ["dark", "heavy", "intense"],
                "fear": ["scary", "tense", "suspense", "horror"],
                "happy": ["happy", "joy", "fun", "dance", "party", "upbeat", "edm"],
                "sad": ["sad", "melancholy", "emotional", "heartbreak", "slow"],
                "surprise": ["epic", "dramatic", "cinematic", "surprise"],
                "neutral": ["chill", "relax", "ambient", "focus", "work"]
            }
            
            # Assign playlists to emotions based on name matching
            for playlist in results['items']:
                name = playlist['name'].lower()
                
                for emotion, keywords in emotion_keywords.items():
                    if any(keyword in name for keyword in keywords):
                        if emotion not in self.user_playlists:
                            self.user_playlists[emotion] = []
                        self.user_playlists[emotion].append(playlist['id'])
                        print(f"Added playlist '{playlist['name']}' to {emotion} category")
                        break
            
            # If we don't have playlists for all emotions, assign some default ones
            for emotion in self.emotion_features:
                if emotion not in self.user_playlists or not self.user_playlists[emotion]:
                    self.user_playlists[emotion] = []
                    # Use the first few playlists as fallbacks
                    for i in range(min(3, len(results['items']))):
                        self.user_playlists[emotion].append(results['items'][i]['id'])
            
            print(f"Loaded playlists for {len(self.user_playlists)} emotion categories")
        except Exception as e:
            print(f"Error loading user playlists: {e}")
    
    def get_tracks_for_emotion(self, emotion, method="playlist"):
        """
        Get a list of tracks based on the emotion
        method: 'playlist', 'library', or 'features'
        """
        if self.sp is None:
            print("Spotify client is not initialized")
            return []
            
        if emotion not in self.emotion_features:
            emotion = "neutral"  # Default to neutral if emotion not recognized
        
        if method == "playlist" and self.user_id is not None:
            # Get tracks from user's playlists
            try:
                print(f"Getting tracks from playlists for emotion: {emotion}")
                
                if emotion not in self.user_playlists or not self.user_playlists[emotion]:
                    print(f"No playlists available for {emotion}, trying library instead")
                    return self.get_tracks_for_emotion(emotion, "library")
                
                # Select a random playlist from the emotion category
                playlist_id = random.choice(self.user_playlists[emotion])
                
                # Try up to 3 times to get the playlist tracks (handling intermittent 404s)
                max_retries = 3
                for attempt in range(max_retries):
                    try:
                        results = self.sp.playlist_tracks(playlist_id, limit=50)
                        
                        if not results or 'items' not in results:
                            print(f"No tracks found in playlist (attempt {attempt+1}/{max_retries})")
                            time.sleep(1)  # Wait before retry
                            continue
                            
                        tracks = results['items']
                        print(f"Found {len(tracks)} tracks in playlist")
                        
                        valid_tracks = [track['track'] for track in tracks if track['track'] is not None]
                        if valid_tracks:
                            print(f"Returning {len(valid_tracks)} valid tracks")
                            return valid_tracks
                        else:
                            print("No valid tracks found, trying another method")
                    except Exception as e:
                        print(f"Error getting playlist tracks (attempt {attempt+1}/{max_retries}): {e}")
                        time.sleep(1)  # Wait before retry
                
                # If we get here, all attempts failed
                print("All playlist attempts failed, trying library instead")
                return self.get_tracks_for_emotion(emotion, "library")
            except Exception as e:
                print(f"Error getting tracks from playlist: {e}")
                return self.get_tracks_for_emotion(emotion, "library")
        
        elif method == "library" and self.user_id is not None:
            # Get tracks from user's saved tracks
            try:
                print(f"Getting tracks from user's library for emotion: {emotion}")
                results = self.sp.current_user_saved_tracks(limit=50)
                
                if not results or 'items' not in results:
                    print("No tracks found in user library, trying features instead")
                    return self.get_tracks_for_emotion(emotion, "features")
                
                tracks = [item['track'] for item in results['items'] if item['track'] is not None]
                print(f"Found {len(tracks)} tracks in user library")
                
                if tracks:
                    return tracks
                else:
                    print("No valid tracks found in library, trying features instead")
                    return self.get_tracks_for_emotion(emotion, "features")
            except Exception as e:
                print(f"Error getting tracks from library: {e}")
                return self.get_tracks_for_emotion(emotion, "features")
        
        elif method == "features":
            # Get tracks based on audio features matching the emotion
            try:
                print(f"Getting tracks based on audio features for emotion: {emotion}")
                target_features = self.emotion_features[emotion]
                seed_genres = self.emotion_genres[emotion]
                
                # Try up to 3 times to get recommendations (handling intermittent 404s)
                max_retries = 3
                for attempt in range(max_retries):
                    try:
                        # Get recommendations based on features
                        results = self.sp.recommendations(
                            seed_genres=seed_genres[:min(3, len(seed_genres))],
                            target_valence=target_features['valence'],
                            target_energy=target_features['energy'],
                            limit=50
                        )
                        
                        if not results or 'tracks' not in results:
                            print(f"No tracks found from recommendations (attempt {attempt+1}/{max_retries})")
                            time.sleep(1)  # Wait before retry
                            continue
                            
                        tracks = results['tracks']
                        print(f"Found {len(tracks)} tracks from recommendations")
                        
                        if tracks:
                            return tracks
                    except Exception as e:
                        print(f"Error getting recommendations (attempt {attempt+1}/{max_retries}): {e}")
                        time.sleep(1)  # Wait before retry
                
                # If we reached here, all attempts failed
                print("All recommendation attempts failed, returning empty list")
                return []
            except Exception as e:
                print(f"Error getting tracks based on features: {e}")
                return []
        
        # If all methods fail or are inapplicable, return empty list
        return []
    
    def get_active_device(self):
        """
        Get the first available active device
        """
        if not self.playback_available:
            print("Playback control not available with current authentication")
            return None
            
        try:
            print("Checking for active devices...")
            devices = self.sp.devices()
            
            if not devices or 'devices' not in devices or not devices['devices']:
                print("No active devices found. Please open Spotify on a device.")
                return None
            
            # Find active device or use the first one
            active_devices = [d for d in devices['devices'] if d.get('is_active', False)]
            
            if active_devices:
                device = active_devices[0]
            else:
                device = devices['devices'][0]
                
            print(f"Using device: {device['name']} ({device['type']})")
            return device['id']
        except Exception as e:
            print(f"Error getting active device: {e}")
            return None
    
    def play_track(self, track):
        """
        Play a specific track on an active Spotify device
        """
        if not self.playback_available:
            print("Playback control not available with current authentication")
            # Return track info without playing
            return {
                'name': track['name'],
                'artist': track['artists'][0]['name'],
                'album': track['album']['name'],
                'image': track['album']['images'][0]['url'] if track['album']['images'] else None,
                'uri': track['uri']
            }
            
        try:
            # Get available device
            device_id = self.get_active_device()
            
            if not device_id:
                print("No active device available for playback")
                return False
            
            # Play the track - try up to 3 times
            max_retries = 3
            for attempt in range(max_retries):
                try:
                    print(f"Playing track: {track['name']} by {track['artists'][0]['name']} (attempt {attempt+1}/{max_retries})")
                    self.sp.start_playback(device_id=device_id, uris=[track['uri']])
                    return True
                except Exception as e:
                    print(f"Error playing track (attempt {attempt+1}/{max_retries}): {e}")
                    if attempt < max_retries - 1:
                        time.sleep(1)  # Wait before retry
            
            return False
        except Exception as e:
            print(f"Error playing track: {e}")
            return False
    
    def play_random_track_for_emotion(self, emotion, method="playlist"):
        """
        Play a random track matching the detected emotion
        """
        print(f"\n--- Finding music for emotion: {emotion} ---")
        tracks = self.get_tracks_for_emotion(emotion, method)
        
        if not tracks:
            print(f"No tracks found for emotion: {emotion}")
            # Try other methods if the first one fails
            if method == "playlist":
                return self.play_random_track_for_emotion(emotion, "library")
            elif method == "library":
                return self.play_random_track_for_emotion(emotion, "features")
            else:
                return None
        
        # Select a random track
        track = random.choice(tracks)
        print(f"Selected track: {track['name']} by {track['artists'][0]['name']}")
        
        # Play the track or just return track info if playback not available
        if self.playback_available:
            success = self.play_track(track)
            
            if success:
                print(f"Now playing: {track['name']}")
                return {
                    'name': track['name'],
                    'artist': track['artists'][0]['name'],
                    'album': track['album']['name'],
                    'image': track['album']['images'][0]['url'] if track['album']['images'] else None,
                    'uri': track['uri']
                }
            else:
                print("Failed to play track")
                return None
        else:
            # Return track info without playing
            print(f"Playback not available, but would play: {track['name']}")
            return {
                'name': track['name'],
                'artist': track['artists'][0]['name'],
                'album': track['album']['name'],
                'image': track['album']['images'][0]['url'] if track['album']['images'] else None,
                'uri': track['uri']
            }