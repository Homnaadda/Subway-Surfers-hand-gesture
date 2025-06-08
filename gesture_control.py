import cv2
import mediapipe as mp
import time
import numpy as np
from pynput.keyboard import Controller, Key
import threading
from collections import deque
import math

class GestureController:
    def __init__(self):
        # MediaPipe setup
        self.mp_hands = mp.solutions.hands
        self.hands = self.mp_hands.Hands(
            static_image_mode=False,
            max_num_hands=1,
            min_detection_confidence=0.8,
            min_tracking_confidence=0.7
        )
        self.mp_draw = mp.solutions.drawing_utils
        
        # Keyboard controller
        self.keyboard = Controller()
        
        # Camera setup
        self.cap = cv2.VideoCapture(0)
        self.cap.set(cv2.CAP_PROP_FRAME_WIDTH, 640)
        self.cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 480)
        self.cap.set(cv2.CAP_PROP_FPS, 30)
        
        # Flick detection variables
        self.hand_positions = deque(maxlen=10)  # Store last 10 hand positions
        self.gesture_history = deque(maxlen=5)
        self.last_gesture_time = 0
        self.gesture_cooldown = 0.4  # Slightly longer for flick gestures
        self.current_gesture = "None"
        
        # Flick detection parameters
        self.min_flick_distance = 0.08  # Minimum distance for flick detection
        self.flick_time_window = 0.3    # Time window to detect flick (seconds)
        self.velocity_threshold = 0.25   # Minimum velocity for flick
        
        # Hand tracking state
        self.hand_detected = False
        self.hand_lost_time = 0
        self.hand_stable_frames = 0
        
        # Performance tracking
        self.fps_counter = 0
        self.fps_start_time = time.time()
        self.current_fps = 0
        
    def calculate_distance(self, point1, point2):
        """Calculate Euclidean distance between two points"""
        return math.sqrt((point1[0] - point2[0])**2 + (point1[1] - point2[1])**2)
    
    def calculate_velocity(self, positions, time_window):
        """Calculate velocity of hand movement"""
        if len(positions) < 2:
            return 0, (0, 0)
        
        # Get positions within time window
        current_time = time.time()
        recent_positions = []
        
        for pos_data in reversed(positions):
            pos, timestamp = pos_data
            if current_time - timestamp <= time_window:
                recent_positions.append(pos)
            else:
                break
        
        if len(recent_positions) < 2:
            return 0, (0, 0)
        
        # Calculate displacement and velocity
        start_pos = recent_positions[-1]  # Oldest position in window
        end_pos = recent_positions[0]     # Most recent position
        
        displacement_x = end_pos[0] - start_pos[0]
        displacement_y = end_pos[1] - start_pos[1]
        
        distance = math.sqrt(displacement_x**2 + displacement_y**2)
        velocity = distance / time_window
        
        return velocity, (displacement_x, displacement_y)
    
    def detect_flick_gesture(self, landmarks):
        """Detect flick gestures based on hand movement"""
        # Use index finger tip for tracking (landmark 8)
        index_tip = landmarks[8]
        current_pos = (index_tip.x, index_tip.y)
        current_time = time.time()
        
        # Store position with timestamp
        self.hand_positions.append((current_pos, current_time))
        
        # Need at least 3 positions to detect flick
        if len(self.hand_positions) < 3:
            return "None"
        
        # Calculate velocity and direction
        velocity, (dx, dy) = self.calculate_velocity(self.hand_positions, self.flick_time_window)
        
        # Check if velocity exceeds threshold
        if velocity < self.velocity_threshold:
            return "None"
        
        # Determine flick direction based on displacement
        abs_dx = abs(dx)
        abs_dy = abs(dy)
        
        gesture = "None"
        
        # Horizontal flicks (left/right)
        if abs_dx > abs_dy and abs_dx > self.min_flick_distance:
            if dx > 0:
                gesture = "FLICK_RIGHT"
            else:
                gesture = "FLICK_LEFT"
        
        # Vertical flicks (up/down)
        elif abs_dy > abs_dx and abs_dy > self.min_flick_distance:
            if dy < 0:  # Negative Y is up in screen coordinates
                gesture = "FLICK_UP"
            else:
                gesture = "FLICK_DOWN"
        
        return gesture
    
    def is_hand_stable(self, landmarks):
        """Check if hand is relatively stable (not in middle of flick)"""
        if len(self.hand_positions) < 3:
            return True
        
        # Check recent movement
        recent_positions = list(self.hand_positions)[-3:]
        max_movement = 0
        
        for i in range(1, len(recent_positions)):
            pos1 = recent_positions[i-1][0]
            pos2 = recent_positions[i][0]
            movement = self.calculate_distance(pos1, pos2)
            max_movement = max(max_movement, movement)
        
        return max_movement < 0.03  # Threshold for stability
    
    def execute_gesture(self, gesture):
        """Execute keyboard action based on flick gesture"""
        current_time = time.time()
        
        # Check cooldown
        if current_time - self.last_gesture_time < self.gesture_cooldown:
            return False
        
        action_executed = False
        
        if gesture == "FLICK_UP":
            self.keyboard.press(Key.up)
            self.keyboard.release(Key.up)
            action_executed = True
            print("🔥 JUMP!")
        elif gesture == "FLICK_DOWN":
            self.keyboard.press(Key.down)
            self.keyboard.release(Key.down)
            action_executed = True
            print("⬇️ SLIDE!")
        elif gesture == "FLICK_LEFT":
            self.keyboard.press(Key.left)
            self.keyboard.release(Key.left)
            action_executed = True
            print("⬅️ MOVE LEFT!")
        elif gesture == "FLICK_RIGHT":
            self.keyboard.press(Key.right)
            self.keyboard.release(Key.right)
            action_executed = True
            print("➡️ MOVE RIGHT!")
        
        if action_executed:
            self.last_gesture_time = current_time
            self.gesture_history.append(gesture)
            # Clear position history after successful gesture
            self.hand_positions.clear()
            return True
        
        return False
    
    def draw_ui(self, img, gesture, velocity=0, landmarks=None):
        """Draw UI elements on the image"""
        h, w, _ = img.shape
        
        # Draw header background
        cv2.rectangle(img, (0, 0), (w, 140), (0, 0, 0), -1)
        cv2.rectangle(img, (0, 0), (w, 140), (50, 50, 50), 2)
        
        # Title
        cv2.putText(img, "Subway Surfers Flick Control", (10, 30),
                   cv2.FONT_HERSHEY_SIMPLEX, 0.8, (255, 255, 255), 2)
        
        # Current gesture
        gesture_color = (0, 255, 0) if gesture != "None" else (100, 100, 100)
        gesture_display = gesture.replace("FLICK_", "").replace("_", " ") if gesture != "None" else "None"
        cv2.putText(img, f"Gesture: {gesture_display}", (10, 60),
                   cv2.FONT_HERSHEY_SIMPLEX, 0.7, gesture_color, 2)
        
        # Velocity indicator
        velocity_color = (0, 255, 255) if velocity > self.velocity_threshold else (100, 100, 100)
        cv2.putText(img, f"Velocity: {velocity:.2f}", (10, 90),
                   cv2.FONT_HERSHEY_SIMPLEX, 0.6, velocity_color, 2)
        
        # Hand status
        hand_status = "DETECTED" if self.hand_detected else "NOT DETECTED"
        hand_color = (0, 255, 0) if self.hand_detected else (0, 0, 255)
        cv2.putText(img, f"Hand: {hand_status}", (10, 120),
                   cv2.FONT_HERSHEY_SIMPLEX, 0.6, hand_color, 2)
        
        # FPS
        cv2.putText(img, f"FPS: {self.current_fps:.1f}", (w-100, 30),
                   cv2.FONT_HERSHEY_SIMPLEX, 0.6, (255, 255, 255), 2)
        
        # Draw gesture guide
        self.draw_gesture_guide(img)
        
        # Draw hand landmarks and tracking
        if landmarks:
            self.draw_hand_tracking(img, landmarks)
    
    def draw_gesture_guide(self, img):
        """Draw flick gesture guide on the side"""
        h, w, _ = img.shape
        guide_x = w - 220
        guide_y = 160
        
        # Guide background
        cv2.rectangle(img, (guide_x-10, guide_y-30), (w-10, guide_y+220), (0, 0, 0), -1)
        cv2.rectangle(img, (guide_x-10, guide_y-30), (w-10, guide_y+220), (50, 50, 50), 2)
        
        # Guide title
        cv2.putText(img, "Flick Gesture Guide:", (guide_x, guide_y),
                   cv2.FONT_HERSHEY_SIMPLEX, 0.5, (255, 255, 255), 1)
        
        # Gesture instructions
        instructions = [
            "Flick Right → → MOVE RIGHT",
            "Flick Left ← ← MOVE LEFT", 
            "Flick Up ↑ ↑ JUMP",
            "Flick Down ↓ ↓ SLIDE",
            "",
            "Tips:",
            "• Make quick, sharp movements",
            "• Keep hand clearly visible",
            "• Wait between gestures"
        ]
        
        for i, instruction in enumerate(instructions):
            y_pos = guide_y + 25 + (i * 20)
            color = (200, 200, 200) if instruction else (100, 100, 100)
            if instruction.startswith("•"):
                color = (150, 150, 255)
            cv2.putText(img, instruction, (guide_x, y_pos),
                       cv2.FONT_HERSHEY_SIMPLEX, 0.35, color, 1)
    
    def draw_hand_tracking(self, img, landmarks):
        """Draw hand tracking visualization"""
        h, w, _ = img.shape
        
        # Highlight index finger tip (used for tracking)
        index_tip = landmarks[8]
        x = int(index_tip.x * w)
        y = int(index_tip.y * h)
        cv2.circle(img, (x, y), 12, (0, 255, 255), -1)
        cv2.circle(img, (x, y), 15, (255, 255, 255), 2)
        
        # Draw movement trail
        if len(self.hand_positions) > 1:
            trail_points = []
            for pos_data in self.hand_positions:
                pos, _ = pos_data
                trail_x = int(pos[0] * w)
                trail_y = int(pos[1] * h)
                trail_points.append((trail_x, trail_y))
            
            # Draw trail lines
            for i in range(1, len(trail_points)):
                alpha = i / len(trail_points)  # Fade effect
                color_intensity = int(255 * alpha)
                cv2.line(img, trail_points[i-1], trail_points[i], 
                        (0, color_intensity, color_intensity), 2)
        
        # Draw velocity vector
        if len(self.hand_positions) >= 2:
            velocity, (dx, dy) = self.calculate_velocity(self.hand_positions, 0.2)
            if velocity > 0.1:
                # Scale vector for visualization
                vector_scale = 200
                end_x = x + int(dx * vector_scale)
                end_y = y + int(dy * vector_scale)
                cv2.arrowedLine(img, (x, y), (end_x, end_y), (255, 0, 255), 3)
    
    def calculate_fps(self):
        """Calculate and update FPS"""
        self.fps_counter += 1
        if time.time() - self.fps_start_time >= 1.0:
            self.current_fps = self.fps_counter
            self.fps_counter = 0
            self.fps_start_time = time.time()
    
    def run(self):
        """Main loop"""
        print("🎮 Subway Surfers Flick Gesture Control Started!")
        print("📋 Instructions:")
        print("   • Flick Right → = MOVE RIGHT")
        print("   • Flick Left ← = MOVE LEFT")
        print("   • Flick Up ↑ = JUMP")
        print("   • Flick Down ↓ = SLIDE")
        print("   • Press ESC to quit")
        print("\n🎯 Make sure Subway Surfers is running and in focus!")
        print("💡 Tip: Make quick, sharp flick movements with your index finger")
        
        while True:
            success, img = self.cap.read()
            if not success or img is None:
                print("❌ Failed to read from camera")
                continue
            
            # Flip image horizontally for mirror effect
            img = cv2.flip(img, 1)
            img_rgb = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
            
            # Process hand detection
            results = self.hands.process(img_rgb)
            
            gesture = "None"
            velocity = 0
            landmarks = None
            
            if results.multi_hand_landmarks:
                self.hand_detected = True
                self.hand_stable_frames += 1
                
                for hand_landmarks in results.multi_hand_landmarks:
                    landmarks = hand_landmarks.landmark
                    
                    # Draw hand landmarks
                    self.mp_draw.draw_landmarks(
                        img, hand_landmarks, self.mp_hands.HAND_CONNECTIONS,
                        self.mp_draw.DrawingSpec(color=(0, 255, 0), thickness=2, circle_radius=2),
                        self.mp_draw.DrawingSpec(color=(255, 0, 0), thickness=2)
                    )
                    
                    # Detect flick gesture
                    gesture = self.detect_flick_gesture(landmarks)
                    
                    # Calculate current velocity for display
                    if len(self.hand_positions) >= 2:
                        velocity, _ = self.calculate_velocity(self.hand_positions, 0.2)
                    
                    # Execute gesture if detected
                    if gesture != "None":
                        executed = self.execute_gesture(gesture)
                        if executed:
                            self.current_gesture = gesture
            else:
                self.hand_detected = False
                self.hand_stable_frames = 0
                # Clear positions when hand is lost
                if time.time() - self.hand_lost_time > 1.0:
                    self.hand_positions.clear()
                    self.hand_lost_time = time.time()
            
            # Draw UI
            self.draw_ui(img, gesture, velocity, landmarks)
            
            # Calculate FPS
            self.calculate_fps()
            
            # Show image
            cv2.imshow("Subway Surfers Flick Gesture Control", img)
            
            # Check for exit
            key = cv2.waitKey(1) & 0xFF
            if key == 27:  # ESC key
                break
            elif key == ord('r'):  # Reset
                self.gesture_history.clear()
                self.hand_positions.clear()
                print("🔄 Gesture history and tracking reset")
            elif key == ord('c'):  # Calibrate
                self.hand_positions.clear()
                print("🎯 Hand tracking calibrated")
        
        self.cleanup()
    
    def cleanup(self):
        """Clean up resources"""
        self.cap.release()
        cv2.destroyAllWindows()
        print("👋 Flick gesture control stopped. Thanks for playing!")

def main():
    try:
        controller = GestureController()
        controller.run()
    except KeyboardInterrupt:
        print("\n⏹️  Interrupted by user")
    except Exception as e:
        print(f"❌ Error: {e}")
    finally:
        cv2.destroyAllWindows()

if __name__ == "__main__":
    main()
