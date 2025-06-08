# Subway Surfers Hand Gesture Control

A computer vision-based hand gesture control system that allows you to play Subway Surfers (or any game) using hand movements detected through your webcam. Control the game by making flick gestures with your index finger!

![Demo Animation](https://via.placeholder.com/600x300/4CAF50/FFFFFF?text=Hand+Gesture+Demo)
*Replace this placeholder with an animated GIF showing the gesture controls in action*

## Features

- **Real-time Hand Detection**: Uses MediaPipe for accurate hand landmark detection
- **Gesture Recognition**: Recognizes flick gestures in four directions
- **Game Control**: Maps gestures to keyboard inputs for game control
- **Visual Feedback**: Shows detected gestures on screen with visual indicators
- **Responsive Controls**: Optimized debounce timing for smooth gameplay

## Supported Gestures

| Gesture | Action | Key Mapping |
|---------|--------|-------------|
| Flick Right → | Move Right | Right Arrow Key |
| Flick Left ← | Move Left | Left Arrow Key |
| Flick Up ↑ | Jump | Up Arrow Key |
| Flick Down ↓ | Slide/Duck | Down Arrow Key |

![Gesture Guide](https://via.placeholder.com/800x200/2196F3/FFFFFF?text=Gesture+Guide+Animation)
*Replace this placeholder with an animated guide showing each gesture*

## Requirements

- Python 3.7 or higher
- Webcam
- Good lighting conditions for optimal hand detection

## Installation

### 1. Clone the Repository

```bash
git clone https://github.com/yourusername/Subway-Surfers-hand-gesture.git
cd Subway-Surfers-hand-gesture
```

### 2. Create Virtual Environment (Recommended)

```bash
# Create virtual environment
python -m venv venv

# Activate virtual environment
# On Windows:
venv\Scripts\activate
# On macOS/Linux:
source venv/bin/activate
```

### 3. Install Dependencies

```bash
pip install -r requirements.txt
```

### 4. Verify Installation

Test if all packages are installed correctly:

```bash
python -c "import cv2, mediapipe, pynput; print('All packages installed successfully!')"
```

## Usage

### 1. Start the Gesture Control System

```bash
python gesture_control.py
```

### 2. Position Your Hand

- Sit about 2-3 feet away from your webcam
- Ensure good lighting on your hand
- Keep your hand visible in the camera frame
- Use your index finger for gestures

### 3. Calibrate Your Gestures

- Start with small, quick flick movements
- Adjust the speed and distance based on responsiveness
- The system has a built-in cooldown to prevent accidental multiple inputs

### 4. Launch Your Game

- Open Subway Surfers or any game that uses arrow keys
- The gesture control will send keyboard inputs to the active window

![Setup Guide](https://via.placeholder.com/600x400/FF9800/FFFFFF?text=Setup+Guide+Animation)
*Replace this placeholder with a setup demonstration*

## Configuration

You can adjust the sensitivity and behavior by modifying these parameters in `gesture_control.py`:

```python
# Gesture sensitivity (higher = less sensitive)
speed_threshold = 1500

# Cooldown between gestures (in seconds)
debounce_time = 0.5

# Hand detection confidence
min_detection_confidence = 0.75
```

## Troubleshooting

### Common Issues

**Camera not detected:**
- Ensure your webcam is connected and not being used by other applications
- Try changing the camera index in `cv2.VideoCapture(0)` to `cv2.VideoCapture(1)`

**Gestures not detected:**
- Improve lighting conditions
- Move closer to the camera
- Make more pronounced flick movements
- Lower the `speed_threshold` value

**Game not responding:**
- Make sure the game window is active and in focus
- Verify that the game uses arrow keys for controls
- Check if any other applications are intercepting keyboard inputs

**Performance issues:**
- Close unnecessary applications
- Ensure good lighting to improve detection accuracy
- Consider lowering the camera resolution

## Technical Details

### Dependencies

- **OpenCV**: Computer vision library for camera input and image processing
- **MediaPipe**: Google's framework for hand landmark detection
- **pynput**: Cross-platform library for keyboard input simulation

### How It Works

1. **Camera Input**: Captures video feed from webcam
2. **Hand Detection**: MediaPipe identifies hand landmarks in real-time
3. **Gesture Recognition**: Calculates velocity of index finger movement
4. **Input Mapping**: Converts gestures to keyboard inputs
5. **Game Control**: Sends arrow key presses to control the game

## Contributing

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

## Future Enhancements

- [ ] Add more gesture types (pinch, grab, etc.)
- [ ] Implement gesture customization interface
- [ ] Add support for multiple games
- [ ] Create GUI for easy configuration
- [ ] Add gesture recording and playback
- [ ] Implement machine learning for improved accuracy

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## Acknowledgments

- [MediaPipe](https://mediapipe.dev/) for hand tracking technology
- [OpenCV](https://opencv.org/) for computer vision capabilities
- Subway Surfers game developers for creating an awesome game to control!

---

**Note**: Replace the placeholder images with actual animated GIFs or screenshots showing:
1. The gesture control system in action
2. A guide demonstrating each gesture
3. The setup process and hand positioning

Enjoy playing Subway Surfers with hand gestures! 🏃‍♂️✋