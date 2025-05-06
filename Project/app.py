from flask import Flask, render_template, Response, jsonify
import cv2
import threading
import time
import numpy as np  # Add this import for np
from emotion_detector import EmotionDetector
from music_player import MusicPlayer
import config

app = Flask(__name__)

# Initialize components
emotion_detector = EmotionDetector()
music_player = MusicPlayer(
    client_id=config.SPOTIFY_CLIENT_ID,
    client_secret=config.SPOTIFY_CLIENT_SECRET,
    redirect_uri=config.SPOTIFY_REDIRECT_URI
)

# Global variables
camera = None
current_emotion = "neutral"
current_track = None
emotion_lock = threading.Lock()
detection_thread = None
detection_active = False

def init_camera():
    global camera
    camera = cv2.VideoCapture(config.CAMERA_INDEX)
    
def release_camera():
    global camera
    if camera is not None:
        camera.release()
        camera = None

def detect_emotion_thread():
    global current_emotion, detection_active
    
    while detection_active:
        if camera is None:
            time.sleep(1)
            continue
        
        # Capture frame
        ret, frame = camera.read()
        if not ret:
            continue
        
        # Detect emotion
        emotion, _ = emotion_detector.detect_emotion(frame)
        
        if emotion:
            with emotion_lock:
                # Only update if emotion is different
                if emotion != current_emotion:
                    current_emotion = emotion
                    # Play appropriate music
                    play_music_for_current_emotion()
        
        # Wait before next detection
        time.sleep(config.EMOTION_DETECTION_INTERVAL)

def play_music_for_current_emotion():
    global current_track
    with emotion_lock:
        # Get a track matching the current emotion
        track_info = music_player.play_random_track_for_emotion(current_emotion)
        if track_info:
            current_track = track_info

def generate_frames():
    while True:
        if camera is None:
            # Return a blank frame if camera not initialized
            blank_frame = 255 * np.ones(shape=[480, 640, 3], dtype=np.uint8)
            _, buffer = cv2.imencode('.jpg', blank_frame)
            frame = buffer.tobytes()
            yield (b'--frame\r\n'
                  b'Content-Type: image/jpeg\r\n\r\n' + frame + b'\r\n')
            time.sleep(0.1)
            continue
            
        success, frame = camera.read()
        if not success:
            break
        
        # Get current emotion to display
        with emotion_lock:
            emotion_to_display = current_emotion
        
        # Draw emotion on frame
        if emotion_to_display:
            # Detect face again just to get coordinates
            _, face_coords = emotion_detector.detect_emotion(frame)
            frame = emotion_detector.draw_emotion_on_frame(frame, emotion_to_display, face_coords)
        
        # Convert to JPEG
        ret, buffer = cv2.imencode('.jpg', frame)
        frame = buffer.tobytes()
        
        # Yield the frame in the response
        yield (b'--frame\r\n'
               b'Content-Type: image/jpeg\r\n\r\n' + frame + b'\r\n')

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/video_feed')
def video_feed():
    return Response(generate_frames(),
                   mimetype='multipart/x-mixed-replace; boundary=frame')

@app.route('/start_detection')
def start_detection():
    global detection_thread, detection_active
    
    if detection_thread is None or not detection_thread.is_alive():
        init_camera()
        detection_active = True
        detection_thread = threading.Thread(target=detect_emotion_thread)
        detection_thread.daemon = True
        detection_thread.start()
        return jsonify({"status": "started"})
    
    return jsonify({"status": "already_running"})

@app.route('/stop_detection')
def stop_detection():
    global detection_active
    
    detection_active = False
    release_camera()
    return jsonify({"status": "stopped"})

@app.route('/current_info')
def current_info():
    with emotion_lock:
        return jsonify({
            "emotion": current_emotion,
            "track": current_track
        })

if __name__ == '__main__':
    app.run(debug=config.DEBUG, port=config.PORT)