document.addEventListener('DOMContentLoaded', function() {
    // DOM elements
    const startBtn = document.getElementById('startBtn');
    const stopBtn = document.getElementById('stopBtn');
    const emotionText = document.getElementById('emotionText');
    const albumArt = document.getElementById('albumArt');
    const trackName = document.getElementById('trackName');
    const artistName = document.getElementById('artistName');
    const albumName = document.getElementById('albumName');
    
    // Store the current track to avoid unnecessary updates
    let currentTrackUri = null;
    
    // Emotion colors
    const emotionColors = {
        'angry': '#ff5252',
        'disgust': '#8bc34a',
        'fear': '#9c27b0',
        'happy': '#ffeb3b',
        'sad': '#2196f3',
        'surprise': '#ff9800',
        'neutral': '#e0e0e0'
    };
    
    // Start detection
    startBtn.addEventListener('click', function() {
        fetch('/start_detection')
            .then(response => response.json())
            .then(data => {
                console.log('Detection started:', data);
                startPolling();
            })
            .catch(error => console.error('Error starting detection:', error));
    });
    
    // Stop detection
    stopBtn.addEventListener('click', function() {
        fetch('/stop_detection')
            .then(response => response.json())
            .then(data => {
                console.log('Detection stopped:', data);
                stopPolling();
            })
            .catch(error => console.error('Error stopping detection:', error));
    });
    
    // Poll for updates
    let pollingInterval = null;
    
    function startPolling() {
        if (!pollingInterval) {
            pollingInterval = setInterval(updateInfo, 1000);
        }
    }
    
    function stopPolling() {
        if (pollingInterval) {
            clearInterval(pollingInterval);
            pollingInterval = null;
        }
    }
    
    // Update UI with current emotion and track
    function updateInfo() {
        fetch('/current_info')
            .then(response => response.json())
            .then(data => {
                // Update emotion display
                if (data.emotion) {
                    emotionText.textContent = data.emotion.charAt(0).toUpperCase() + data.emotion.slice(1);
                    emotionText.style.color = emotionColors[data.emotion] || '#e0e0e0';
                }
                
                // Update track info
                if (data.track && data.track.uri !== currentTrackUri) {
                    currentTrackUri = data.track.uri;
                    
                    trackName.textContent = data.track.name;
                    artistName.textContent = data.track.artist;
                    albumName.textContent = data.track.album;
                    
                    if (data.track.image) {
                        albumArt.src = data.track.image;
                    }
                }
            })
            .catch(error => console.error('Error getting current info:', error));
    }
});