# 🎵 Emotion-Based Music Player

A machine learning application that detects emotions from facial expressions and plays music matching your mood using the Spotify API.

![Emotion Music Player Demo](https://media.giphy.com/media/placeholder/giphy.gif)

## ✨ Features

- **Real-time Emotion Detection**: Uses computer vision to analyze facial expressions via webcam
- **Music Recommendation Engine**: Selects music that matches your current emotional state
- **Spotify Integration**: Plays tracks directly on your Spotify account
- **Responsive Web Interface**: Clean, intuitive design that updates in real-time

## 🧠 Emotions Detected

- 😠 Angry
- 🤢 Disgust
- 😨 Fear
- 😊 Happy
- 😢 Sad
- 😲 Surprise
- 😐 Neutral

## 🚀 Installation

### Prerequisites

- Python 3.8+
- Webcam
- Spotify account (Free or Premium)
- Spotify Developer account with registered application

### Step 1: Clone the repository

```bash
git clone https://github.com/yourusername/emotion-based-music-player.git
cd emotion-based-music-player
```

### Step 2: Set up a virtual environment

```bash
python -m venv venv
```

Activate the virtual environment:

**Windows**
```bash
venv\Scripts\activate
```

**macOS/Linux**
```bash
source venv/bin/activate
```

### Step 3: Install dependencies

```bash
pip install -r requirements.txt
```

### Step 4: Configure Spotify API credentials

1. Create a Spotify Developer account at [developer.spotify.com](https://developer.spotify.com/)
2. Create a new application in the Spotify Developer Dashboard
3. Set the Redirect URI to `http://127.0.0.1:8000/callback`
4. Note your Client ID and Client Secret
5. Create a `config.py` file in the project root:

```python
# Spotify API credentials
SPOTIFY_CLIENT_ID = "your-client-id-here"
SPOTIFY_CLIENT_SECRET = "your-client-secret-here"
SPOTIFY_REDIRECT_URI = "http://127.0.0.1:8000/callback"

# Emotion detection settings
EMOTION_DETECTION_INTERVAL = 5  # Detect emotion every 5 seconds
CAMERA_INDEX = 0  # Default camera (usually the webcam)

# Flask app settings
DEBUG = True
PORT = 8000
```

### Step 5: Create default album art

Run the following script to create a default album art image:

```bash
python generate_default_album.py
```

## 📊 Usage

1. Start the application:
```bash
python app.py
```

2. Open your browser and go to:
```
http://127.0.0.1:8000
```

3. Click "Start Detection" to enable the webcam and begin emotion detection
4. Open the Spotify application on your device (to act as a playback device)
5. The system will detect your emotion and play appropriate music automatically

## 🔧 How It Works

1. **Emotion Detection**: The application uses OpenCV for face detection and DeepFace for emotion classification.
2. **Music Selection**: Based on detected emotions, the application:
   - First attempts to find matching songs from your personal playlists
   - Falls back to your liked songs library if no playlist matches
   - Uses Spotify's recommendation API as a final fallback
3. **Playback**: The selected track is played on your active Spotify device

## 🧩 Project Structure

```
emotion-music-player/
├── app.py                # Main application file
├── emotion_detector.py   # Emotion detection module
├── music_player.py       # Music recommendation and playback
├── config.py             # Configuration settings
├── requirements.txt      # Dependencies
├── static/               # Static files for web interface
│   ├── css/              # Stylesheets
│   ├── js/               # JavaScript files
│   └── img/              # Images
└── templates/            # HTML templates
    └── index.html        # Main interface
```

## 🛠️ Customization

### Emotion-Music Mapping

Edit the `emotion_features` and `emotion_genres` dictionaries in `music_player.py` to customize the audio features and genres associated with each emotion.

### Interface

Modify the CSS in `static/css/style.css` to change the appearance of the web interface.

## 🤝 Contributing

Contributions are welcome! Here's how you can contribute:

1. Fork the repository
2. Create a feature branch: `git checkout -b feature-name`
3. Commit your changes: `git commit -m 'Add some feature'`
4. Push to the branch: `git push origin feature-name`
5. Submit a pull request

## 📝 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 🙏 Acknowledgements

- [DeepFace](https://github.com/serengil/deepface) for facial emotion recognition
- [Spotipy](https://github.com/plamere/spotipy) for Spotify API integration
- [Flask](https://flask.palletsprojects.com/) for the web framework
- [OpenCV](https://opencv.org/) for computer vision capabilities

## 📧 Contact

For questions or feedback, please contact:
- Your Name - [your.email@example.com](mailto:your.email@example.com)
- Project Link: [https://github.com/yourusername/emotion-based-music-player](https://github.com/yourusername/emotion-based-music-player)