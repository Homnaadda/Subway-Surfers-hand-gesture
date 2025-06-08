import cv2
import mediapipe as mp
import time
from pynput.keyboard import Controller, Key

# Setup
mp_hands = mp.solutions.hands
hands = mp_hands.Hands(max_num_hands=1, min_detection_confidence=0.75)
mp_draw = mp.solutions.drawing_utils
keyboard = Controller()

cap = cv2.VideoCapture(0)

# Tracking
prev_x, prev_y = 0, 0
prev_time = 0
debounce_time = 0.5  # More responsive
gesture_cooldown = 0

while True:
    success, img = cap.read()
    if not success or img is None:
        continue

    img = cv2.flip(img, 1)
    img_rgb = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
    results = hands.process(img_rgb)

    h, w, _ = img.shape
    current_time = time.time()

    if results.multi_hand_landmarks:
        for handLms in results.multi_hand_landmarks:
            mp_draw.draw_landmarks(img, handLms, mp_hands.HAND_CONNECTIONS)

            # Index fingertip
            x = int(handLms.landmark[8].x * w)
            y = int(handLms.landmark[8].y * h)

            dt = current_time - prev_time
            dx = x - prev_x
            dy = y - prev_y

            velocity_x = dx / dt if dt > 0 else 0
            velocity_y = dy / dt if dt > 0 else 0

            gesture = None
            speed_threshold = 1500  # Flick sensitivity

            if current_time - gesture_cooldown > debounce_time:
                if abs(velocity_x) > abs(velocity_y):
                    if velocity_x > speed_threshold:
                        gesture = "FLICK RIGHT"
                        keyboard.press(Key.right)
                        keyboard.release(Key.right)
                    elif velocity_x < -speed_threshold:
                        gesture = "FLICK LEFT"
                        keyboard.press(Key.left)
                        keyboard.release(Key.left)
                else:
                    if velocity_y < -speed_threshold:
                        gesture = "FLICK UP (JUMP)"
                        keyboard.press(Key.up)
                        keyboard.release(Key.up)
                    elif velocity_y > speed_threshold:
                        gesture = "FLICK DOWN (SLIDE)"
                        keyboard.press(Key.down)
                        keyboard.release(Key.down)

                if gesture:
                    gesture_cooldown = current_time
                    cv2.putText(img, f'{gesture}', (10, 70),
                                cv2.FONT_HERSHEY_SIMPLEX, 1.2, (0, 255, 255), 3)

            prev_x, prev_y = x, y
            prev_time = current_time

    cv2.imshow("Flick Gesture Control", img)
    if cv2.waitKey(1) & 0xFF == 27:
        break

cap.release()
cv2.destroyAllWindows()