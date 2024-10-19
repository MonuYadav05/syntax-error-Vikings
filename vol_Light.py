import cv2
import mediapipe as mp
import math
import numpy as np
from flask import Flask, jsonify, Response
from flask_cors import CORS
import threading

app = Flask(__name__)
CORS(app)

mp_draw = mp.solutions.drawing_utils
mp_hand = mp.solutions.hands

# Finger landmarks ids
thumb_tip = 4
index_tip = 8
middle_tip = 12
ring_tip = 16
pinky_tip = 20

video = None
camera_active = False  # State to control camera
frame_thread = None

# Placeholder function to control light intensity
def set_light_intensity(intensity):
    # Implement your light control logic here
    # Example for Raspberry Pi GPIO:
    # pwm.ChangeDutyCycle(intensity)  # Set the intensity
    print(f"Setting light intensity to: {intensity}")

@app.route('/gesture', methods=['GET'])
def gesture_control():
    global camera_active
    if camera_active and video is not None:
        ret, image = video.read()
        if not ret:
            return jsonify({"error": "Failed to capture image."}), 500
        
        image = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
        image.flags.writeable = False
        results = hands.process(image)
        image.flags.writeable = True
        image = cv2.cvtColor(image, cv2.COLOR_RGB2BGR)

        response_data = {
            "intensity": 0,
            "fingers": 0,
        }

        if results.multi_hand_landmarks and results.multi_handedness:
            for idx, hand_landmark in enumerate(results.multi_hand_landmarks):
                lmList = []
                for id, lm in enumerate(hand_landmark.landmark):
                    h, w, c = image.shape
                    cx, cy = int(lm.x * w), int(lm.y * h)
                    lmList.append([id, cx, cy])

                hand_label = results.multi_handedness[idx].classification[0].label

                if lmList:
                    # Light Control with Right Hand
                    if hand_label == "Right":
                        x1, y1 = lmList[thumb_tip][1], lmList[thumb_tip][2]
                        x2, y2 = lmList[index_tip][1], lmList[index_tip][2]
                        length = math.hypot(x2 - x1, y2 - y1)

                        min_length = 50
                        max_length = 300
                        intensity = np.interp(length, [min_length, max_length], [0, 100])
                        set_light_intensity(int(intensity))  # Set the light intensity

                        response_data["intensity"] = int(intensity)

                        # Display light intensity on the frame
                        cv2.putText(image, f'Light Intensity: {int(intensity)} %', (50, 100),
                                    cv2.FONT_HERSHEY_SIMPLEX, 1, (255, 0, 0), 2)

                    # Finger Counting with Left Hand
                    if hand_label == "Left":
                        fingers = [
                            1 if lmList[thumb_tip][1] < lmList[3][1] else 0,
                            1 if lmList[index_tip][2] < lmList[index_tip - 2][2] else 0,
                            1 if lmList[middle_tip][2] < lmList[middle_tip - 2][2] else 0,
                            1 if lmList[ring_tip][2] < lmList[ring_tip - 2][2] else 0,
                            1 if lmList[pinky_tip][2] < lmList[pinky_tip - 2][2] else 0
                        ]

                        totalFingers = fingers.count(1)
                        response_data["fingers"] = totalFingers

                        # Display number of fingers raised
                        cv2.putText(image, f'Fingers: {totalFingers}', (50, 450),
                                    cv2.FONT_HERSHEY_SIMPLEX, 1, (255, 0, 0), 2)

                    # Draw landmarks for hands
                    mp_draw.draw_landmarks(image, hand_landmark, mp_hand.HAND_CONNECTIONS)

        return jsonify(response_data)
    else:
        return jsonify({"error": "Camera is not active."}), 400

@app.route('/toggle_camera', methods=['POST'])
def toggle_camera():
    global camera_active, video, frame_thread

    # Start or stop the camera
    if camera_active:
        camera_active = False
        if video:
            video.release()  # Release the video capture
            video = None
        if frame_thread:
            frame_thread.join()  # Wait for the frame processing thread to finish
    else:
        camera_active = True
        video = cv2.VideoCapture(0)
        frame_thread = threading.Thread(target=generate_frames)
        frame_thread.start()  # Start the frame processing in a separate thread

    return jsonify({"camera_active": camera_active})

def generate_frames():
    with mp_hand.Hands(min_detection_confidence=0.5, min_tracking_confidence=0.5, max_num_hands=2) as hands:
        while camera_active:
            success, frame = video.read()
            if not success:
                print("Failed to capture frame")  # Log failure
                break
            
            # Flip the frame horizontally
            frame = cv2.flip(frame, 1)  # 1 means flipping around the y-axis
            
            # Process the frame for hand landmarks
            image_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
            results = hands.process(image_rgb)

            # Draw landmarks for hands
            if results.multi_hand_landmarks:
                for hand_landmark in results.multi_hand_landmarks:
                    mp_draw.draw_landmarks(frame, hand_landmark, mp_hand.HAND_CONNECTIONS)

            # Encode the processed frame to JPEG
            ret, buffer = cv2.imencode('.jpg', frame)
            if not ret:
                print("Failed to encode frame")  # Log encoding failure
                break
            frame_bytes = buffer.tobytes()
            
            # Yield the frame with drawn landmarks
            yield (b'--frame\r\n'
                   b'Content-Type: image/jpeg\r\n\r\n' + frame_bytes + b'\r\n')

@app.route('/video_feed')
def video_feed():
    # Video streaming route
    return Response(generate_frames(), mimetype='multipart/x-mixed-replace; boundary=frame')

if __name__ == '__main__':
    with mp_hand.Hands(min_detection_confidence=0.5,
                       min_tracking_confidence=0.5,
                       max_num_hands=2) as hands:
        app.run(host='0.0.0.0', port=5000, debug=True)

video.release()
cv2.destroyAllWindows()
