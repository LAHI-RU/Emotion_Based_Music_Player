import cv2
from deepface import DeepFace
import numpy as np

class EmotionDetector:
    def __init__(self):
        # Load the face cascade for detecting faces
        self.face_cascade = cv2.CascadeClassifier(cv2.data.haarcascades + 'haarcascade_frontalface_default.xml')
        self.emotions = ["angry", "disgust", "fear", "happy", "sad", "surprise", "neutral"]
        
    def detect_emotion(self, frame):
        """
        Detect emotion from a video frame
        Returns: dominant emotion and face coordinates
        """
        # Convert to grayscale
        gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
        
        # Detect faces
        faces = self.face_cascade.detectMultiScale(gray, 1.1, 4)
        
        if len(faces) == 0:
            return None, None
        
        # For the first face detected
        x, y, w, h = faces[0]
        
        # Extract the face
        face_img = frame[y:y+h, x:x+w]
        
        try:
            # Analyze emotion using DeepFace
            result = DeepFace.analyze(face_img, actions=['emotion'], enforce_detection=False)
            
            # Get the dominant emotion
            emotion = result[0]['dominant_emotion']
            return emotion, (x, y, w, h)
        except Exception as e:
            print(f"Error in emotion detection: {e}")
            return None, (x, y, w, h)
    
    def draw_emotion_on_frame(self, frame, emotion, face_coords):
        """
        Draw a box around the face and label with emotion
        """
        if face_coords is None:
            return frame
        
        x, y, w, h = face_coords
        
        # Draw rectangle around face
        cv2.rectangle(frame, (x, y), (x+w, y+h), (0, 255, 0), 2)
        
        # Add emotion text if detected
        if emotion:
            cv2.putText(frame, emotion, (x, y-10), cv2.FONT_HERSHEY_SIMPLEX, 0.9, (0, 255, 0), 2)
        
        return frame
    
# clinet_ID - c49fba99aece4be592249af0a17e0a80
# client_secret - 1afe076060d74424ad77f908739b7f33